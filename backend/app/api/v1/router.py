from fastapi import APIRouter

from app.api.v1.endpoints.assessment import router as assessment_router


router = APIRouter()
router.include_router(assessment_router, prefix="/risk", tags=["risk"])
