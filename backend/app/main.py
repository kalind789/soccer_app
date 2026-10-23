import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import DbSession
from app.routers import drills, session_plans

# The address the React app runs at. Browsers block it from calling this API unless it's allowed here.
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

# Tables are created and changed by Alembic migrations: run `uv run alembic upgrade head`.
app = FastAPI(title="Practice Planner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(drills.router)
app.include_router(session_plans.router)


@app.get("/health")
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "0.1.0"}
