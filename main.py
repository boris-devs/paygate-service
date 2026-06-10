from fastapi import FastAPI
from src.routers import auth_router, users_router, admin_router, webhooks_router

app = FastAPI()

prefix = "/api/v1"

app.include_router(router=auth_router, prefix=f"{prefix}/auth", tags=["Authentication"])
app.include_router(router=users_router, prefix=f"{prefix}/users", tags=["users"])
app.include_router(router=admin_router, prefix=f"{prefix}/admin", tags=["Admin Panel"])
app.include_router(router=webhooks_router, prefix=f"{prefix}/webhooks", tags=["Webhooks"])
