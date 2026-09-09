from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_admin_client
from routes import router
from config import SUPABASE_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    admin = get_admin_client()
    app.state.supabase = admin
    yield


app = FastAPI(title="Mindurr.ai API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8080",
        "null",  # allows local testing opened via file://
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)


@app.get("/")
def read_root():
    return {
        "message": "Hello from the Mindurr.ai Python Backend!",
        "database_url_loaded": SUPABASE_URL,
        "docs": "/docs",
        "status": "ready",
    }