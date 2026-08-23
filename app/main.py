from fastapi import FastAPI
from .database import init_db

app = FastAPI(
    title="CSA Assurance Planner",
    description="Portfolio-safe CSA planning workspace — synthetic data only.",
    version="0.1.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "CSA Assurance Planner",
        "data_boundary": "All records are synthetic and fictional.",
    }
