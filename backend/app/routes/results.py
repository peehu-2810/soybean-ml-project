from fastapi import APIRouter

router = APIRouter(tags=["Results"])


@router.get("/results")
def get_results():
    return {
        "status": "success",
        "message": "Model comparison results are not available yet.",
        "results": {
            "K": {},
            "Mg": {},
            "N": {}
        }
    }