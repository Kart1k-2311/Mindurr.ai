import json
import re
import time
import httpx
from json_repair import repair_json
from config import AI_API_KEY

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _call_gemini(system_prompt: str, user_prompt: str, attempt: int = 0) -> str:
    if attempt >= 3:
        raise RuntimeError("Gemini API failed after 3 attempts")

    body = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": user_prompt},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = httpx.post(
            GEMINI_ENDPOINT,
            params={"key": AI_API_KEY},
            json=body,
            timeout=90.0,
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _strip_json_fences(text)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            time.sleep(10 * (attempt + 1))
            return _call_gemini(system_prompt, user_prompt, attempt + 1)
        if exc.response.status_code >= 500:
            time.sleep(3 * (attempt + 1))
            return _call_gemini(system_prompt, user_prompt, attempt + 1)
        raise
    except (httpx.HTTPError, KeyError, IndexError):
        return _call_gemini(system_prompt, user_prompt, attempt + 1)


def _parse_json(text: str) -> dict | list:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = min(
        (i for i in (text.find("["), text.find("{")) if i != -1),
        default=-1,
    )
    if start == -1:
        raise ValueError("No JSON structure found in AI response")

    if text[start] == "[":
        end = text.rfind("]")
        candidate = text[start : end + 1]
    else:
        end = text.rfind("}")
        candidate = text[start : end + 1]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        try:
            return json.loads(candidate.replace("'", '"'))
        except json.JSONDecodeError:
            repaired = repair_json(candidate)
            try:
                return json.loads(repaired)
            except (json.JSONDecodeError, TypeError, ValueError):
                raise ValueError("Could not parse AI JSON response")


async def analyze_skill_profile(profile_data: dict) -> dict:
    from prompts import (
        ANALYZE_SKILL_PROFILE_SYSTEM,
        ANALYZE_SKILL_PROFILE_USER,
    )

    user_prompt = ANALYZE_SKILL_PROFILE_USER.format(
        goal=profile_data.get("goal", "Not specified"),
        industry=profile_data.get("industry", ""),
        languages=", ".join(profile_data.get("languages", [])),
        technologies=", ".join(profile_data.get("technologies", [])),
        scores=json.dumps(profile_data.get("scores", {})),
        total_score=profile_data.get("total_score", 0),
    )

    raw = _call_gemini(ANALYZE_SKILL_PROFILE_SYSTEM, user_prompt)
    return _parse_json(raw)


async def match_candidates_to_job(
    job_description: str,
    candidates: list[dict],
) -> list[dict]:
    from prompts import (
        MATCH_JOB_DESCRIPTION_SYSTEM,
        MATCH_JOB_DESCRIPTION_USER,
    )

    candidates_json = json.dumps(candidates, default=str)
    user_prompt = MATCH_JOB_DESCRIPTION_USER.format(
        job_description=job_description,
        candidates_json=candidates_json,
    )

    raw = _call_gemini(MATCH_JOB_DESCRIPTION_SYSTEM, user_prompt)
    result = _parse_json(raw)
    return result.get("matches", []) if isinstance(result, dict) else result


async def recommend_resources(
    target_career: str,
    profile_data: dict,
) -> dict:
    from prompts import (
        RECOMMEND_RESOURCES_SYSTEM,
        RECOMMEND_RESOURCES_USER,
    )

    user_prompt = RECOMMEND_RESOURCES_USER.format(
        target_career=target_career,
        industry=profile_data.get("industry", ""),
        languages=", ".join(profile_data.get("languages", [])),
        technologies=", ".join(profile_data.get("technologies", [])),
        scores=json.dumps(profile_data.get("scores", {})),
        skill_gaps=json.dumps(profile_data.get("skill_gaps", [])),
    )

    raw = _call_gemini(RECOMMEND_RESOURCES_SYSTEM, user_prompt)
    return _parse_json(raw)


async def generate_questions(
    technologies: list[str],
    industry: str,
) -> list[dict]:
    from prompts import (
        GENERATE_QUESTIONS_SYSTEM,
        GENERATE_QUESTIONS_USER,
    )

    user_prompt = GENERATE_QUESTIONS_USER.format(
        technologies=", ".join(technologies),
        industry=industry,
    )

    raw = _call_gemini(GENERATE_QUESTIONS_SYSTEM, user_prompt)
    questions = _parse_json(raw)
    if isinstance(questions, dict):
        questions = questions.get("questions", [])

    return [_normalize_question(q) for q in questions]


def _normalize_question(q: dict) -> dict:
    options = q.get("options", [])
    if not isinstance(options, list) or len(options) < 2:
        options = ["Option A", "Option B", "Option C", "Option D"]

    answer = q.get("answer")
    answer_idx = -1

    if isinstance(answer, bool):
        answer_idx = 1 if answer else 0
    elif isinstance(answer, (int, float)) and not isinstance(answer, bool):
        answer_idx = int(answer)
    elif isinstance(answer, str):
        try:
            answer_idx = int(answer)
        except ValueError:
            answer_idx = options.index(answer) if answer in options else -1

    if answer_idx < 0 or answer_idx >= len(options):
        answer_idx = 0

    return {
        "q": q.get("q", "Untitled question"),
        "options": options,
        "answer": answer_idx,
        "technology": q.get("technology", ""),
    }