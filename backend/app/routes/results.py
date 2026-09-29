import json

from fastapi import APIRouter, HTTPException

from app.config import RESULTS_PATH


router = APIRouter(tags=["Results"])


@router.get("/results")
def get_results():
    """
    Return model comparison results for K, Mg and N.
    """

    try:
        with open(RESULTS_PATH, "r", encoding="utf-8") as file:
            results = json.load(file)

        return {
            "status": "success",
            "results": results
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Model comparison file not found."
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model comparison file contains invalid JSON."
        )