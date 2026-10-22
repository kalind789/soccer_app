from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, DbSession, engine
from app.routers import drills


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create any missing tables when the server starts. Alembic replaces this later.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Practice Planner", lifespan=lifespan)
app.include_router(drills.router)


@app.get("/health")
def health(db: DbSession) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "0.1.0"}
