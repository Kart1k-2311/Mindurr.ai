from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Any, Literal
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

try:
    from .config import Settings, get_settings, SUPABASE_URL
except ImportError:  # Supports `uvicorn main:app` from the backend directory.
    from config import Settings, get_settings, SUPABASE_URL

try:
    from database import get_admin_client
except ImportError:
    try:
        from .database import get_admin_client
    except ImportError:
        get_admin_client = None

try:
    from routes import router
except ImportError:
    try:
        from .routes import router
    except ImportError:
        router = None


logger = logging.getLogger(__name__)


INDUSTRY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "frontend": {
        "goals": ["Build responsive user interfaces", "Create reusable components", "Optimize web experiences"],
        "languages": ["JavaScript", "TypeScript", "HTML/CSS"],
        "technologies": {
            "JavaScript": ["React", "Vue.js", "Angular", "Next.js", "Svelte"],
            "TypeScript": ["React", "Angular", "Next.js"],
            "HTML/CSS": ["Tailwind CSS", "SASS/SCSS", "Bootstrap"],
        },
    },
    "backend": {
        "goals": ["Build production APIs", "Design reliable data services", "Scale backend systems"],
        "languages": ["Python", "JavaScript", "Java", "Go", "Rust"],
        "technologies": {
            "Python": ["Django", "FastAPI", "Flask", "Celery"],
            "JavaScript": ["Express.js", "NestJS", "Fastify"],
            "Java": ["Spring Boot", "Micronaut"],
            "Go": ["Gin", "Echo", "Fiber"],
            "Rust": ["Actix Web", "Axum"],
        },
    },
    "devops": {
        "goals": ["Automate deployments", "Manage cloud infrastructure", "Improve system reliability"],
        "languages": ["Python", "Bash", "Go"],
        "technologies": {
            "Python": ["Docker", "Kubernetes", "Terraform", "Ansible"],
            "Bash": ["Docker", "Linux Administration", "CI/CD"],
            "Go": ["Docker", "Kubernetes", "Terraform"],
        },
    },
    "data_science": {
        "goals": ["Analyze real-world datasets", "Build predictive models", "Deploy machine learning workflows"],
        "languages": ["Python", "R", "SQL"],
        "technologies": {
            "Python": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
            "R": ["ggplot2", "dplyr", "Shiny"],
            "SQL": ["PostgreSQL", "MySQL", "BigQuery"],
        },
    },
    "mobile": {
        "goals": ["Build cross-platform apps", "Create native mobile interfaces", "Ship mobile experiences"],
        "languages": ["JavaScript", "Dart", "Kotlin", "Swift"],
        "technologies": {
            "JavaScript": ["React Native", "Expo"],
            "Dart": ["Flutter"],
            "Kotlin": ["Android Jetpack Compose"],
            "Swift": ["SwiftUI", "UIKit"],
        },
    },
    "fullstack": {
        "goals": ["Build end-to-end products", "Integrate frontend and backend", "Deliver production web apps"],
        "languages": ["JavaScript", "TypeScript", "Python"],
        "technologies": {
            "JavaScript": ["React", "Node.js", "Express.js", "Next.js"],
            "TypeScript": ["React", "Next.js", "NestJS"],
            "Python": ["Django", "FastAPI", "Flask"],
        },
    },
}


DEVOPS_ASSESSMENT_QUESTIONS: tuple[tuple[str, tuple[str, ...], int], ...] = (
    ("What does DevOps combine?", ("A) Development and Operations", "B) Design and Testing", "C) Database and Security", "D) Development and Marketing"), 0),
    ("What is CI/CD?", ("A) Code Integration/Code Deployment", "B) Continuous Integration/Continuous Delivery or Deployment", "C) Computer Integration/Computer Development", "D) Continuous Inspection/Continuous Debugging"), 1),
    ("Which tool is commonly used for CI/CD pipelines?", ("A) Jenkins", "B) Photoshop", "C) Figma", "D) MySQL"), 0),
    ("What is Docker primarily used for?", ("A) Database design", "B) Containerization", "C) UI development", "D) Network routing"), 1),
    ("What is Kubernetes primarily used for?", ("A) Managing containerized applications", "B) Writing JavaScript", "C) Creating databases", "D) Designing websites"), 0),
    ("What is Infrastructure as Code (IaC)?", ("A) Writing infrastructure configuration as code", "B) Writing frontend code", "C) Creating documentation", "D) Building hardware"), 0),
    ("Which tool is commonly associated with Infrastructure as Code?", ("A) Terraform", "B) Figma", "C) React", "D) Excel"), 0),
    ("What is Ansible commonly used for?", ("A) Configuration management and automation", "B) Image editing", "C) Database querying", "D) UI design"), 0),
    ("What is a container?", ("A) A lightweight isolated environment for running applications", "B) A physical server", "C) A database table", "D) A network cable"), 0),
    ("What is a Docker image?", ("A) A template used to create containers", "B) A screenshot", "C) A database backup", "D) A virtual machine"), 0),
    ("What is version control used for?", ("A) Tracking changes to code and files", "B) Monitoring CPU temperature only", "C) Encrypting databases", "D) Designing interfaces"), 0),
    ("Which tool is widely used for version control?", ("A) Git", "B) Docker", "C) Kubernetes", "D) Jenkins"), 0),
    ("What does git pull generally do?", ("A) Uploads local changes", "B) Retrieves and integrates changes from a remote repository", "C) Deletes a repository", "D) Creates a Docker image"), 1),
    ("What is monitoring in DevOps?", ("A) Observing system health and performance", "B) Writing application code", "C) Designing logos", "D) Creating database tables"), 0),
    ("Which tool is commonly used for metrics monitoring?", ("A) Prometheus", "B) Git", "C) Docker", "D) Maven"), 0),
    ("Which tool is commonly used for dashboards and visualization?", ("A) Grafana", "B) Git", "C) Terraform", "D) Ansible"), 0),
    ("What is logging?", ("A) Recording application and system events", "B) Compressing files", "C) Creating containers", "D) Writing HTML"), 0),
    ("What is horizontal scaling?", ("A) Adding more instances/servers", "B) Increasing RAM on one server", "C) Removing servers", "D) Reducing CPU usage"), 0),
    ("What is vertical scaling?", ("A) Adding more servers", "B) Increasing resources of an existing server", "C) Creating more containers", "D) Adding users"), 1),
    ("What is a load balancer used for?", ("A) Distributing traffic among servers", "B) Encrypting passwords", "C) Building Docker images", "D) Writing code"), 0),
    ("What is blue-green deployment?", ("A) Running two production environments and switching traffic between them", "B) Deploying only on weekends", "C) Deploying without testing", "D) Deploying to two programming languages"), 0),
    ("What is a rolling deployment?", ("A) Updating instances gradually rather than all at once", "B) Deleting all servers", "C) Deploying only once", "D) Rebuilding a database"), 0),
    ("What is a rollback?", ("A) Reverting to a previous version", "B) Deleting Git", "C) Increasing server capacity", "D) Creating a new database"), 0),
    ("What is a secrets manager used for?", ("A) Securely storing sensitive credentials and secrets", "B) Storing images", "C) Writing code", "D) Monitoring CPU"), 0),
    ("What is cloud computing?", ("A) On-demand computing resources delivered over a network", "B) Local-only computing", "C) Writing code without a computer", "D) A programming language"), 0),
    ("Which is a major cloud platform?", ("A) AWS", "B) Git", "C) Linux", "D) Jenkins"), 0),
    ("What is a health check?", ("A) A mechanism for determining whether a service is functioning correctly", "B) A database query", "C) A Git command", "D) A Docker image"), 0),
    ("What is immutable infrastructure?", ("A) Replacing infrastructure rather than modifying existing instances in place", "B) Infrastructure that cannot be monitored", "C) Infrastructure without servers", "D) A database system"), 0),
    ("What is DevOps automation intended to achieve?", ("A) Reduce repetitive manual work and improve consistency", "B) Eliminate testing", "C) Remove version control", "D) Increase manual deployment"), 0),
    ("What is the primary goal of DevOps?", ("A) Faster and more reliable software delivery through collaboration and automation", "B) Eliminate developers", "C) Only manage databases", "D) Only design websites"), 0),
)


class AssessmentStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    industry: str = Field(min_length=1, max_length=50)
    goal: str | None = Field(default=None, max_length=120)
    languages: list[str] = Field(min_length=1, max_length=10)
    technologies: list[str] = Field(min_length=1, max_length=20)

    @field_validator("industry")
    @classmethod
    def clean_industry(cls, value: str) -> str:
        return value.strip()

    @field_validator("languages", "technologies")
    @classmethod
    def clean_unique_values(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("values cannot be empty")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("values must be unique")
        return cleaned


class SubmittedAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1, max_length=80)
    answer: int = Field(ge=0, le=20, strict=True)


class SubmitAnswersRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: list[SubmittedAnswer] = Field(min_length=1, max_length=100)

    @field_validator("answers")
    @classmethod
    def unique_question_ids(cls, answers: list[SubmittedAnswer]) -> list[SubmittedAnswer]:
        ids = [answer.question_id for answer in answers]
        if len(set(ids)) != len(ids):
            raise ValueError("answers must contain one entry per question")
        return answers


class PublicQuestion(BaseModel):
    id: str
    q: str
    options: list[str]
    technology: str


class AssessmentStartResponse(BaseModel):
    assessment_id: UUID
    status: Literal["in_progress"]
    started_at: datetime
    question_count: int = Field(ge=1)


class AssessmentQuestionsResponse(BaseModel):
    assessment_id: UUID
    status: Literal["in_progress", "submitted"]
    questions: list[PublicQuestion] = Field(min_length=1)


class AssessmentQuestionResponse(BaseModel):
    assessment_id: UUID
    status: Literal["in_progress", "submitted"]
    question: PublicQuestion
    question_index: int = Field(ge=0)
    total_questions: int = Field(ge=1)
    has_next: bool


class AssessmentResultResponse(BaseModel):
    assessment_id: UUID
    status: Literal["submitted"]
    score: float = Field(ge=0, le=100)
    result: dict[str, Any]
    submitted_at: datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=20.0)
    if get_admin_client:
        try:
            admin = get_admin_client()
            app.state.supabase = admin
        except Exception as e:
            logger.warning("Could not initialize Supabase admin client: %s", e)
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(title="Mindurr.ai API", version="1.0.0", lifespan=lifespan)
settings_for_cors = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8080",
        "null",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if router:
    app.include_router(router)


@app.get("/")
def read_root():
    return {
        "message": "Hello from the Mindurr.ai Python Backend!",
        "database_url_loaded": SUPABASE_URL,
        "docs": "/docs",
        "status": "ready",
    }


def _configured_settings() -> Settings:
    settings = get_settings()
    try:
        settings.validate()
    except RuntimeError as exc:
        logger.error("FastAPI server configuration is incomplete: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assessment service is not configured",
        ) from exc
    return settings


def _http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def _service_headers(settings: Settings) -> dict[str, str]:
    headers = {
        "apikey": settings.supabase_service_key,
        "Content-Type": "application/json",
    }
    # Legacy service_role keys are JWTs. New sb_secret_ keys must stay on apikey.
    if settings.supabase_service_key.count(".") == 2:
        headers["Authorization"] = f"Bearer {settings.supabase_service_key}"
    return headers


async def _get_current_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    settings = _configured_settings()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        response = await _http_client(request).get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.supabase_auth_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )
    except httpx.RequestError as exc:
        logger.warning("Supabase Auth request failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc

    if response.status_code != httpx.codes.OK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = response.json()
        user_id = UUID(str(user["id"]))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        logger.error("Supabase Auth returned an invalid user response")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service returned an invalid response",
        ) from exc

    return {"id": str(user_id), "email": user.get("email")}


CurrentUser = Annotated[dict[str, Any], Depends(_get_current_user)]


def _validate_selections(payload: AssessmentStartRequest) -> None:
    definition = INDUSTRY_DEFINITIONS.get(payload.industry)
    if not definition:
        raise HTTPException(status_code=422, detail="Unsupported industry")

    if payload.goal and payload.goal not in definition["goals"]:
        raise HTTPException(status_code=422, detail="Assessment goal is not valid for the selected industry")

    allowed_languages = set(definition["languages"])
    invalid_languages = sorted(set(payload.languages) - allowed_languages)
    if invalid_languages:
        raise HTTPException(
            status_code=422,
            detail=f"Languages are not valid for the selected industry: {', '.join(invalid_languages)}",
        )

    allowed_technologies = {
        technology
        for language in payload.languages
        for technology in definition["technologies"].get(language, [])
    }
    invalid_technologies = sorted(set(payload.technologies) - allowed_technologies)
    if invalid_technologies:
        raise HTTPException(
            status_code=422,
            detail="One or more technologies are not valid for the selected languages",
        )


def _normalise_questions(raw_questions: Any, technologies: list[str]) -> list[dict[str, Any]]:
    if not isinstance(raw_questions, list) or not raw_questions or len(raw_questions) > 100:
        raise HTTPException(status_code=502, detail="Question generator returned an invalid question set")

    # Keep the assessment size stable when a model returns more than requested.
    raw_questions = raw_questions[:30]
    allowed_technologies = set(technologies)
    normalised: list[dict[str, Any]] = []
    for index, raw_question in enumerate(raw_questions):
        if not isinstance(raw_question, dict):
            raise HTTPException(status_code=502, detail="Question generator returned invalid data")

        question = raw_question.get("q")
        options = raw_question.get("options")
        answer = raw_question.get("answer")
        technology = raw_question.get("technology")
        if (
            not isinstance(question, str)
            or not question.strip()
            or len(question) > 2000
            or not isinstance(options, list)
            or len(options) != 4
            or any(not isinstance(option, str) or not option.strip() or len(option) > 500 for option in options)
            or isinstance(answer, bool)
            or not isinstance(answer, int)
            or answer < 0
            or answer >= len(options)
            or not isinstance(technology, str)
            or technology not in allowed_technologies
        ):
            raise HTTPException(status_code=502, detail="Question generator returned invalid data")

        normalised.append(
            {
                "id": str(index),
                "q": question.strip(),
                "options": [option.strip() for option in options],
                "answer": answer,
                "technology": technology,
            }
        )
    return normalised


def _devops_questions(technologies: list[str]) -> list[dict[str, Any]]:
    raw_questions = [
        {
            "q": question,
            "options": list(options),
            "answer": answer,
            # The supplied quiz is cross-cutting, so distribute it across the
            # technologies selected by the student for meaningful breakdowns.
            "technology": technologies[index % len(technologies)],
        }
        for index, (question, options, answer) in enumerate(DEVOPS_ASSESSMENT_QUESTIONS)
    ]
    return _normalise_questions(raw_questions, technologies)


def _public_question(question: dict[str, Any]) -> PublicQuestion:
    return PublicQuestion(
        id=question["id"],
        q=question["q"],
        options=question["options"],
        technology=question["technology"],
    )


async def _supabase_rest(
    request: Request,
    method: str,
    resource: str,
    *,
    params: dict[str, str] | None = None,
    body: Any = None,
    prefer: str | None = None,
    timeout: float | None = None,
) -> Any:
    settings = _configured_settings()
    headers = _service_headers(settings)
    if prefer:
        headers["Prefer"] = prefer

    try:
        response = await _http_client(request).request(
            method,
            f"{settings.supabase_url}/rest/v1/{resource.lstrip('/')}",
            headers=headers,
            params=params,
            json=body,
            timeout=timeout or settings.request_timeout_seconds,
        )
    except httpx.RequestError as exc:
        logger.warning("Supabase REST request failed for %s: %s", resource, type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable",
        ) from exc

    if response.status_code < 200 or response.status_code >= 300:
        logger.error("Supabase REST request returned status %s for %s", response.status_code, resource)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database request failed",
        )

    if not response.content:
        return None
    try:
        return response.json()
    except ValueError as exc:
        logger.error("Supabase REST returned a non-JSON response for %s", resource)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database returned an invalid response",
        ) from exc


async def _get_assessment(
    request: Request,
    assessment_id: UUID,
    user_id: str,
) -> dict[str, Any] | None:
    rows = await _supabase_rest(
        request,
        "GET",
        "assessments",
        params={
            "select": "id,user_id,industry,languages,technologies,questions,submitted_answers,started_at,submitted_at,score,result,status",
            "id": f"eq.{assessment_id}",
            "user_id": f"eq.{user_id}",
            "limit": "1",
        },
    )
    return rows[0] if isinstance(rows, list) and rows else None


async def _update_assessment(
    request: Request,
    assessment_id: UUID,
    user_id: str,
    fields: dict[str, Any],
) -> dict[str, Any]:
    rows = await _supabase_rest(
        request,
        "PATCH",
        "assessments",
        params={"id": f"eq.{assessment_id}", "user_id": f"eq.{user_id}"},
        body=fields,
        prefer="return=representation",
    )
    if not isinstance(rows, list) or not rows:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assessment could not be updated",
        )
    return rows[0]


async def _generate_questions(
    request: Request,
    payload: AssessmentStartRequest,
) -> list[dict[str, Any]]:
    if payload.industry == "devops":
        return _devops_questions(payload.technologies)

    settings = _configured_settings()
    prompt = (
        "You are a technical assessment engine. Generate exactly 30 multiple-choice "
        f"questions to assess skill level for: {', '.join(payload.technologies)}. "
        f"Industry context: {payload.industry}. Assessment goal: {payload.goal or 'general skill assessment'}. "
        "Return ONLY a valid JSON array, no "
        'markdown, no explanation. Each object must have: "q" (string question), '
        '"options" (array of exactly 4 strings), "answer" (0-3 index of correct '
        'answer), "technology" (which selected technology this question covers). '
        "Mix questions evenly across all selected technologies. Vary difficulty: "
        "some beginner, some intermediate, some advanced."
    )
    if settings.groq_api_key:
        provider = "Groq"
        endpoint = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": settings.groq_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        response_parser = "groq"
    else:
        provider = "Gemini"
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        headers = {"Content-Type": "application/json"}
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        response_parser = "gemini"

    try:
        response = await _http_client(request).post(
            endpoint,
            params={"key": settings.gemini_api_key} if response_parser == "gemini" else None,
            headers=headers,
            json=body,
            timeout=settings.generator_timeout_seconds,
        )
    except httpx.RequestError as exc:
        logger.warning("%s question generator request failed: %s", provider, type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate assessment questions",
        ) from exc

    if response.status_code < 200 or response.status_code >= 300:
        logger.error("%s question generator returned status %s", provider, response.status_code)
        if response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Question generation is temporarily rate-limited. Please try again later.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate assessment questions",
        )

    try:
        data = response.json()
        if response_parser == "groq":
            text = data["choices"][0]["message"]["content"]
        else:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Question generator returned an invalid response",
        ) from exc
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Question generator returned an invalid response",
        ) from exc

    text = str(text).strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        raw_questions = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Question generator returned invalid JSON",
        ) from exc
    return _normalise_questions(raw_questions, payload.technologies)


def _not_found() -> HTTPException:
    # Do not reveal whether another student's assessment ID exists.
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")


def _result_response(row: dict[str, Any], assessment_id: UUID) -> AssessmentResultResponse:
    submitted_at = row.get("submitted_at")
    result = row.get("result")
    score = row.get("score")
    if not submitted_at or not isinstance(result, dict) or score is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assessment result is incomplete",
        )
    return AssessmentResultResponse(
        assessment_id=assessment_id,
        status="submitted",
        score=float(score),
        result=result,
        submitted_at=submitted_at,
    )


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/assessments",
    response_model=AssessmentStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_assessment(
    payload: AssessmentStartRequest,
    request: Request,
    user: CurrentUser,
) -> AssessmentStartResponse:
    _validate_selections(payload)
    user_id = user["id"]
    now = datetime.now(timezone.utc).isoformat()
    inserted = await _supabase_rest(
        request,
        "POST",
        "assessments",
        body=[
            {
                "user_id": user_id,
                "industry": payload.industry,
                "languages": payload.languages,
                "technologies": payload.technologies,
                "status": "generating",
                "started_at": now,
                "updated_at": now,
            }
        ],
        prefer="return=representation",
    )
    if not isinstance(inserted, list) or not inserted or not inserted[0].get("id"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assessment could not be started",
        )

    assessment_id = UUID(str(inserted[0]["id"]))
    try:
        questions = await _generate_questions(request, payload)
        updated = await _update_assessment(
            request,
            assessment_id,
            user_id,
            {"questions": questions, "status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()},
        )
    except HTTPException:
        try:
            await _update_assessment(
                request,
                assessment_id,
                user_id,
                {"status": "failed", "updated_at": datetime.now(timezone.utc).isoformat()},
            )
        except HTTPException:
            logger.exception("Could not mark failed assessment %s", assessment_id)
        raise

    return AssessmentStartResponse(
        assessment_id=assessment_id,
        status="in_progress",
        started_at=updated["started_at"],
        question_count=len(questions),
    )


@app.get(
    "/api/assessments/{assessment_id}/questions",
    response_model=AssessmentQuestionResponse,
)
async def get_assessment_question(
    assessment_id: UUID,
    request: Request,
    user: CurrentUser,
    question_index: int = Query(default=0, ge=0, le=99),
) -> AssessmentQuestionResponse:
    row = await _get_assessment(request, assessment_id, user["id"])
    if not row:
        raise _not_found()
    if row.get("status") == "failed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Question generation failed")

    questions = row.get("questions")
    if not isinstance(questions, list) or not questions:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Questions are not ready")

    if question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment question not found",
        )

    return AssessmentQuestionResponse(
        assessment_id=assessment_id,
        status="submitted" if row.get("status") == "submitted" else "in_progress",
        question=_public_question(questions[question_index]),
        question_index=question_index,
        total_questions=len(questions),
        has_next=question_index < len(questions) - 1,
    )


@app.post(
    "/api/assessments/{assessment_id}/answers",
    response_model=AssessmentResultResponse,
)
async def submit_assessment_answers(
    assessment_id: UUID,
    payload: SubmitAnswersRequest,
    request: Request,
    user: CurrentUser,
) -> AssessmentResultResponse:
    user_id = user["id"]
    row = await _get_assessment(request, assessment_id, user_id)
    if not row:
        raise _not_found()
    if row.get("status") == "failed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Assessment is not available")
    if row.get("status") == "submitted":
        existing_answers = row.get("submitted_answers") or []
        submitted_answers = [{"question_id": answer.question_id, "answer": answer.answer} for answer in payload.answers]
        canonical_existing = sorted(existing_answers, key=lambda answer: answer.get("question_id", ""))
        canonical_submitted = sorted(submitted_answers, key=lambda answer: answer["question_id"])
        if canonical_existing == canonical_submitted:
            return _result_response(row, assessment_id)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Assessment has already been submitted")

    questions = row.get("questions")
    if not isinstance(questions, list) or not questions:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Questions are not ready")

    question_by_id = {str(question.get("id")): question for question in questions}
    answers_by_id = {answer.question_id: answer.answer for answer in payload.answers}
    if set(answers_by_id) != set(question_by_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Submit one answer for every assessment question",
        )

    technology_results: dict[str, dict[str, int | float]] = {}
    correct_answers = 0
    for question_id, question in question_by_id.items():
        selected_answer = answers_by_id[question_id]
        options = question.get("options")
        if not isinstance(options, list) or selected_answer >= len(options):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="An answer is outside the valid option range",
            )
        technology = str(question["technology"])
        bucket = technology_results.setdefault(technology, {"correct": 0, "total": 0, "score": 0})
        bucket["total"] = int(bucket["total"]) + 1
        is_correct = selected_answer == question.get("answer")
        if is_correct:
            correct_answers += 1
            bucket["correct"] = int(bucket["correct"]) + 1

    total_questions = len(questions)
    overall_score = round((correct_answers / total_questions) * 100, 2)
    technology_scores: dict[str, float] = {}
    for technology, bucket in technology_results.items():
        technology_scores[technology] = round(
            (int(bucket["correct"]) / int(bucket["total"])) * 100,
            2,
        )
        bucket["score"] = technology_scores[technology]

    result = {
        "overall_score": overall_score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "technology_scores": technology_scores,
        "technology_breakdown": technology_results,
    }
    submitted_at = datetime.now(timezone.utc).isoformat()
    submitted_answers = [
        {"question_id": answer.question_id, "answer": answer.answer}
        for answer in payload.answers
    ]

    # Keep the existing recruiter-facing profile table populated from the verified result.
    await _supabase_rest(
        request,
        "POST",
        "skill_profiles",
        params={"on_conflict": "user_id"},
        body=[
            {
                "user_id": user_id,
                "industry": row["industry"],
                "languages": row["languages"],
                "technologies": row["technologies"],
                "scores": technology_scores,
                "total_score": overall_score,
                "completed_at": submitted_at,
            }
        ],
        prefer="resolution=merge-duplicates,return=representation",
    )
    updated = await _update_assessment(
        request,
        assessment_id,
        user_id,
        {
            "submitted_answers": submitted_answers,
            "submitted_at": submitted_at,
            "score": overall_score,
            "result": result,
            "status": "submitted",
            "updated_at": submitted_at,
        },
    )
    return _result_response(updated, assessment_id)


@app.get(
    "/api/assessments/{assessment_id}/result",
    response_model=AssessmentResultResponse,
)
async def get_assessment_result(
    assessment_id: UUID,
    request: Request,
    user: CurrentUser,
) -> AssessmentResultResponse:
    row = await _get_assessment(request, assessment_id, user["id"])
    if not row:
        raise _not_found()
    if row.get("status") != "submitted":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Assessment has not been submitted")
    return _result_response(row, assessment_id)
