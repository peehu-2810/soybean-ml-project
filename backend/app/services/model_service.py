# app/services/model_service.py

from pathlib import Path
import joblib

from app.config import MODEL_PATHS, USE_MOCK_MODEL
from app.config import FEATURES_BY_NUTRIENT


class ModelService:

    def __init__(self):
        self.models = {}

        if not USE_MOCK_MODEL:
            self.load_models()

    def load_models(self):
        """Load K, Mg and N models."""

        for nutrient, model_path in MODEL_PATHS.items():

            if not Path(model_path).exists():
                raise FileNotFoundError(
                    f"Model file not found: {model_path}"
                )

            self.models[nutrient] = joblib.load(model_path)

    def predict(self, nutrient, inputs):
        """Predict water uptake."""

        if USE_MOCK_MODEL:
            ordered_values = [
                inputs[name]
                for name in FEATURES_BY_NUTRIENT[nutrient]
            ]

            return round(sum(ordered_values) * 0.1, 2)

        model = self.models[nutrient]

        ordered_values = [
            inputs[name]
            for name in FEATURES_BY_NUTRIENT[nutrient]
        ]

        prediction = model.predict([ordered_values])

        return float(prediction[0])


model_service = ModelService()