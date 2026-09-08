import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass(frozen=True)
class Settings:
    """Server-only configuration used by the FastAPI application."""

    supabase_url: str
    supabase_service_key: str
    supabase_auth_key: str
    frontend_origins: tuple[str, ...]
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    request_timeout_seconds: float = 20.0
    generator_timeout_seconds: float = 90.0

    def validate(self) -> None:
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_key:
            missing.append("SUPABASE_SERVICE_KEY or SUPABASE_SERVICE_ROLE_KEY")
        if not self.gemini_api_key and not self.groq_api_key:
            missing.append("GEMINI_API_KEY, AI_API_KEY, or GROQ_API_KEY")
        if missing:
            raise RuntimeError("Missing required server configuration: " + ", ".join(missing))


def get_settings() -> Settings:
    service_key = (
        os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SUPABASE_SECRET_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    )
    auth_key = (
        os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("SUPABASE_PUBLISHABLE_KEY")
        or service_key
    )
    raw_origins = os.getenv("FRONTEND_ORIGINS", "*")
    frontend_origins = tuple(
        origin.strip() for origin in raw_origins.split(",") if origin.strip()
    ) or ("*",)

    return Settings(
        supabase_url=os.getenv("SUPABASE_URL", "").rstrip("/"),
        supabase_service_key=service_key,
        supabase_auth_key=auth_key,
        frontend_origins=frontend_origins,
        gemini_api_key=(
            os.getenv("GEMINI_API_KEY")
            or os.getenv("AI_API_KEY")
            or os.getenv("AI_MODEL_API_KEY")
            or ""
        ),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        groq_api_key=os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API") or "",
        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    )


# Keep the existing names available to any local tooling that imports config.py.
settings = get_settings()
SUPABASE_URL = settings.supabase_url
SUPABASE_SERVICE_KEY = settings.supabase_service_key
AI_MODEL_API_KEY = os.getenv("AI_MODEL_API_KEY")
