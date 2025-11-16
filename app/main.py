from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api import health, pull_requests, statistics, teams, users
from app.core.exceptions import http_exception_handler, validation_exception_handler
from app.database.base import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="PR Reviewer Assignment Service",
    version="1.0.0",
    description="Service for assigning reviewers to PRs",
    response_model_by_alias=True,
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(teams.router, tags=["Teams"])
app.include_router(users.router, tags=["Users"])
app.include_router(pull_requests.router, tags=["PullRequests"])
app.include_router(health.router, tags=["Health"])
app.include_router(statistics.router, tags=["Statistics"])


@app.get("/")
async def root():
    """root endpoint"""
    return {"message": "PR Reviewer Assignment Service"}
