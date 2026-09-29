from typing import Dict, Literal

from pydantic import BaseModel, model_validator

from app.config import (
    FEATURES_BY_NUTRIENT,
    FEATURE_RANGES_BY_NUTRIENT,
)


class PredictionInput(BaseModel):
    nutrient: Literal["K", "Mg", "N"]
    inputs: Dict[str, float]

    @model_validator(mode="after")
    def check_inputs(self):
        expected = FEATURES_BY_NUTRIENT[self.nutrient]
        ranges = FEATURE_RANGES_BY_NUTRIENT[self.nutrient]

        # Check missing features
        missing = [
            name for name in expected
            if name not in self.inputs
        ]

        if missing:
            raise ValueError(
                f"Missing inputs for {self.nutrient} model: {missing}"
            )

        # Check extra features
        extra = [
            name for name in self.inputs
            if name not in expected
        ]

        if extra:
            raise ValueError(
                f"Unexpected inputs for {self.nutrient} model: {extra}. "
                f"Allowed: {expected}"
            )

        # Check valid ranges
        for name, value in self.inputs.items():
            low, high = ranges[name]

            if not (low <= value <= high):
                raise ValueError(
                    f"{name}={value} is outside the allowed range "
                    f"{low} to {high}"
                )

        return self


class PredictionOutput(BaseModel):
    nutrient: str
    predicted_water_uptake: float
    unit: str
    model_used: str