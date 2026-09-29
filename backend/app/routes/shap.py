import json

from fastapi import APIRouter, HTTPException

from app.config import SHAP_PATH


router = APIRouter(tags=["SHAP"])


@router.get("/shap")
def get_shap():
    """
    Return SHAP feature-importance data.
    """

    try:
        with open(SHAP_PATH, "r", encoding="utf-8") as file:
            shap_data = json.load(file)

        return {
            "status": "success",
            "shap": shap_data
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="SHAP feature-importance file not found."
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="SHAP file contains invalid JSON."
        )