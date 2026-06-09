from fastapi import FastAPI
from src.routers import auth_router

app = FastAPI()

prefix = "/api/v1"

app.include_router(router=auth_router, prefix=f"{prefix}/auth", tags=["Authentication"])