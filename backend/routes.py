import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user, require_role
from database import get_admin_client, get_user_client
from ai_engine import analyze_skill_profile, match_candidates_to_job, generate_questions, recommend_resources

router = APIRouter(prefix="/api")


@router.get("/auth/me")
async def get_me(user: AuthenticatedUser = Depends(get_current_user)):
    return {"user_id": user.user_id, "email": user.email, "role": user.role}


@router.get("/profile")
async def get_profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]

    client = get_user_client(token)
    auth_result = client.auth.get_user(token)
    user = auth_result.user

    profile = None
    try:
        result = client.table("profiles").select("*").eq("id", user.id).limit(1).execute()
        rows = result.data if result.data else []
        profile = rows[0] if rows else None
    except Exception:
        profile = None

    skill_profile = None
    try:
        result = client.table("skill_profiles").select("*").eq("user_id", user.id).limit(1).execute()
        rows = result.data if result.data else []
        skill_profile = rows[0] if rows else None
    except Exception:
        skill_profile = None

    return {
        "user": {"id": user.id, "email": user.email},
        "profile": profile,
        "skill_profile": skill_profile,
    }


@router.get("/skill-profile")
async def get_skill_profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]

    client = get_user_client(token)
    auth_result = client.auth.get_user(token)
    user = auth_result.user

    result = client.table("skill_profiles").select("*").eq("user_id", user.id).limit(1).execute()
    rows = result.data if result.data else []
    if not rows:
        raise HTTPException(status_code=404, detail="No skill profile found")
    return rows[0]


@router.post("/skill-profile")
async def save_skill_profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]

    body = await request.json()
    client = get_user_client(token)
    auth_result = client.auth.get_user(token)
    user = auth_result.user

    upsert_data = {
        "user_id": user.id,
        "goal": body.get("goal"),
        "industry": body.get("industry"),
        "languages": body.get("languages", []),
        "technologies": body.get("technologies", []),
        "scores": body.get("scores", {}),
        "total_score": body.get("total_score", 0),
    }

    try:
        result = client.table("skill_profiles").upsert(
            upsert_data, on_conflict="user_id"
        ).execute()
    except Exception as exc:
        # skill_profiles.goal only exists after sql/007 migration — fall back gracefully
        if "goal" not in str(exc).lower():
            raise
        upsert_data.pop("goal", None)
        result = client.table("skill_profiles").upsert(
            upsert_data, on_conflict="user_id"
        ).execute()

    rows = result.data if result.data else []
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to save skill profile")

    return {"success": True, "skill_profile": rows[0]}


@router.post("/skill-profile/analyze")
async def analyze_profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]

    client = get_user_client(token)
    auth_result = client.auth.get_user(token)
    user = auth_result.user

    result = client.table("skill_profiles").select("*").eq("user_id", user.id).limit(1).execute()
    rows = result.data if result.data else []
    if not rows:
        raise HTTPException(status_code=404, detail="Save your skill profile first")

    profile = rows[0]
    analysis = await analyze_skill_profile({
        "goal": profile.get("goal"),
        "industry": profile.get("industry"),
        "languages": profile.get("languages", []),
        "technologies": profile.get("technologies", []),
        "scores": profile.get("scores", {}),
        "total_score": profile.get("total_score", 0),
    })

    client.table("skill_profiles").update({
        "ai_insights": analysis
    }).eq("user_id", user.id).execute()

    return {"analysis": analysis}


@router.get("/recommendations")
async def get_recommendations(
    user: AuthenticatedUser = Depends(get_current_user),
):
    admin = get_admin_client()
    result = admin.table("skill_profiles").select("*").eq("user_id", user.user_id).limit(1).execute()
    rows = result.data if result.data else []
    if not rows:
        raise HTTPException(status_code=404, detail="No skill profile found")

    profile = rows[0]
    insights = profile.get("ai_insights") or {}
    return {
        "career_paths": insights.get("career_paths", []),
        "roadmap": insights.get("roadmap", []),
        "courses": insights.get("recommended_courses", []),
    }


def _extract_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    return auth_header.split(" ")[1]


@router.post("/recruiter/job")
async def create_job(
    request: Request,
    user: AuthenticatedUser = Depends(require_role(["authenticated"])),
):
    body = await request.json()
    admin = get_admin_client()
    result = admin.table("job_descriptions").insert({
        "recruiter_id": user.user_id,
        "title": body.get("title"),
        "description": body.get("description"),
        "required_skills": body.get("required_skills", []),
        "experience_level": body.get("experience_level", "entry"),
    }).execute()

    rows = result.data if result.data else []
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to create job")

    return {"success": True, "job": rows[0]}


@router.post("/recruiter/match")
async def match_job(
    request: Request,
    user: AuthenticatedUser = Depends(require_role(["authenticated"])),
):
    body = await request.json()
    job_id = body.get("job_id")
    job_description = body.get("description")

    if not job_description:
        raise HTTPException(status_code=400, detail="Job description is required")

    admin = get_admin_client()

    job = None
    if job_id:
        job_result = admin.table("job_descriptions").select("*").eq("id", job_id).limit(1).execute()
        job_rows = job_result.data if job_result.data else []
        job = job_rows[0] if job_rows else None
        if job:
            job_description = job.get("description", job_description)

    skill_result = admin.table("skill_profiles").select("*").execute()
    skill_rows = skill_result.data if skill_result.data else []

    profiles_result = admin.table("profiles").select("id, full_name, email").execute()
    profile_rows = profiles_result.data if profiles_result.data else []
    id_to_profile = {p["id"]: p for p in profile_rows}

    candidates = []
    for sp in skill_rows:
        p = id_to_profile.get(sp.get("user_id"), {})
        candidates.append({
            "id": str(sp.get("user_id")),
            "name": p.get("full_name", "Unknown"),
            "email": p.get("email", ""),
            "industry": sp.get("industry"),
            "languages": sp.get("languages", []),
            "technologies": sp.get("technologies", []),
            "scores": sp.get("scores", {}),
            "total_score": sp.get("total_score", 0),
            "ai_insights": sp.get("ai_insights", {}),
        })

    if not candidates:
        return {"success": True, "matches": [], "message": "No candidates found yet"}

    matches = await match_candidates_to_job(job_description, candidates)

    for m in matches:
        cid = m.get("candidate_id")
        if cid and job_id:
            admin.table("candidate_matches").upsert({
                "job_id": job_id,
                "user_id": cid,
                "match_score": m.get("match_score", 0),
                "match_reasoning": json.dumps(m, default=str),
            }).execute()

    return {"success": True, "matches": matches}


@router.get("/recruiter/jobs")
async def list_jobs(
    user: AuthenticatedUser = Depends(get_current_user),
):
    admin = get_admin_client()
    result = admin.table("job_descriptions").select("*").eq("recruiter_id", user.user_id).execute()
    return {"jobs": result.data if result.data else []}


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/questions/generate")
async def generate_assessment_questions(request: Request):
    body = await request.json()
    technologies = body.get("technologies", [])
    industry = body.get("industry", "")

    if not technologies:
        raise HTTPException(status_code=400, detail="technologies is required")

    questions = await generate_questions(technologies, industry)
    return {"questions": questions}


@router.post("/recommendations/generate")
async def generate_recommendations(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
):
    body = await request.json()
    admin = get_admin_client()
    admin.table("skill_profiles").update({
        "ai_insights": body.get("analysis", {})
    }).eq("user_id", user.user_id).execute()
    return {"success": True}


@router.post("/recommendations/roadmap")
async def generate_roadmap(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
):
    body = await request.json()
    target_career = body.get("target_career", "")
    if not target_career:
        raise HTTPException(status_code=400, detail="target_career is required")

    admin = get_admin_client()
    result = admin.table("skill_profiles").select("*").eq("user_id", user.user_id).limit(1).execute()
    rows = result.data if result.data else []
    if not rows:
        raise HTTPException(status_code=404, detail="No skill profile found")

    profile = rows[0]
    roadmap = await recommend_resources(target_career, {
        "industry": profile.get("industry"),
        "languages": profile.get("languages", []),
        "technologies": profile.get("technologies", []),
        "scores": profile.get("scores", {}),
        "skill_gaps": (profile.get("ai_insights") or {}).get("weaknesses", []),
    })

    return {"roadmap": roadmap.get("roadmap", []), "courses": roadmap.get("courses", [])}