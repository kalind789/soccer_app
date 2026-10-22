from fastapi import FastAPI

app = FastAPI(title="Practice Planner")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
