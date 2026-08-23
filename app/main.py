from fastapi import FastAPI

from .database import init_db
from .router import router

app = FastAPI(
    title="CSA Assurance Planner",
    description="Portfolio-safe CSA planning workspace — synthetic data only.",
    version="0.1.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


app.include_router(router)
