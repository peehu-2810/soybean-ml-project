# app/routes/predict.py

from fastapi import APIRouter, HTTPException

from app.config import TARGET_UNIT
from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.model_service import model_service

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput):
    """Predict water uptake using the K, Mg or N model."""

    try:
        prediction = model_service.predict(
            data.nutrient,
            data.inputs
        )

        return PredictionOutput(
            nutrient=data.nutrient,
            predicted_water_uptake=prediction,
            unit=TARGET_UNIT,
            model_used="mock"
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )