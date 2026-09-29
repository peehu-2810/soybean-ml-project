# app/schemas/prediction.py
# Describes the data going INTO /predict and coming OUT of it.

from typing import Dict, Literal

from pydantic import BaseModel, model_validator

from app.config import FEATURES_BY_NUTRIENT, FEATURE_RANGES


class PredictionInput(BaseModel):
    """Data the frontend sends to /predict."""

    # Which model to use. Must match the keys in FEATURES_BY_NUTRIENT.
    nutrient: Literal["K", "Mg", "N"]

    # Feature name -> number, e.g. {"Ca": 120, "Na": 15, ...}
    inputs: Dict[str, float]

    @model_validator(mode="after")
    def check_inputs(self):
        expected = FEATURES_BY_NUTRIENT[self.nutrient]

        missing = [name for name in expected if name not in self.inputs]
        if missing:
            raise ValueError(f"Missing inputs for {self.nutrient} model: {missing}")

        extra = [name for name in self.inputs if name not in expected]
        if extra:
            raise ValueError(
                f"Unexpected inputs for {self.nutrient} model: {extra}. "
                f"Allowed: {expected}"
            )

        # Range check (only for features that have a range in config.py)
        for name, value in self.inputs.items():
            if name in FEATURE_RANGES:
                low, high = FEATURE_RANGES[name]
                if not (low <= value <= high):
                    raise ValueError(
                        f"{name}={value} is outside the allowed range {low} to {high}"
                    )
        return self

    # Pre-fills Swagger. These numbers are made up, just for testing.
    model_config = {
        "json_schema_extra": {
            "example": {
                "nutrient": "K",
                "inputs": {
                    "Ca": 120,
                    "Na": 15,
                    "SO4": 80,
                    "NO3-N": 40,
                    "P": 20,
                    "Alkalinity": 90,
                    "TDS": 500,
                    "Mn": 0.5,
                },
            }
        }
    }


class PredictionOutput(BaseModel):
    """Data /predict sends back."""

    nutrient: str
    predicted_water_uptake: float
    unit: str
    model_used: str