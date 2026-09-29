from fastapi import APIRouter

from app.config import FEATURES_BY_NUTRIENT

router = APIRouter(tags=["Features"])


@router.get("/features")
def get_features():
    return FEATURES_BY_NUTRIENT