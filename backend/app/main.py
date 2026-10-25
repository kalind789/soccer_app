from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import DbSession
from app.routers import drills, session_plans, teams
from app.settings import FRONTEND_ORIGIN

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
app.include_router(teams.router)


@app.get("/health")
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "0.1.0"}
