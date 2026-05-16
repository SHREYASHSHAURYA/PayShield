from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.assessment import router as assessment_router

router = APIRouter()
router.include_router(assessment_router, prefix="/risk", tags=["risk"])
router.include_router(admin_router, prefix="/admin", tags=["admin"])
