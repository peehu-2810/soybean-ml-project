from fastapi import APIRouter

from app.config import (
    FEATURES_BY_NUTRIENT,
    FEATURE_RANGES_BY_NUTRIENT,
)


router = APIRouter(tags=["Features"])


@router.get("/features")
def get_features():
    """
    Return required features and valid ranges for each nutrient model.
    """

    result = {}

    for nutrient in FEATURES_BY_NUTRIENT:
        result[nutrient] = {
            "feature_count": len(FEATURES_BY_NUTRIENT[nutrient]),
            "features": FEATURES_BY_NUTRIENT[nutrient],
            "ranges": {
                feature: {
                    "min": FEATURE_RANGES_BY_NUTRIENT[nutrient][feature][0],
                    "max": FEATURE_RANGES_BY_NUTRIENT[nutrient][feature][1],
                }
                for feature in FEATURES_BY_NUTRIENT[nutrient]
            },
        }

    return result