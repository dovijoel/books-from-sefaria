from fastapi import APIRouter
from app.api.v1 import sefaria, jobs, configs

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(sefaria.router)
v1_router.include_router(jobs.router)
v1_router.include_router(configs.router)
