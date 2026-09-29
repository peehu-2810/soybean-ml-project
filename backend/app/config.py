# app/config.py
# Central settings for the whole backend.

from pathlib import Path

# ---------------------------------------------------------------
# App info (shown in Swagger docs)
# ---------------------------------------------------------------
APP_NAME = "Soybean Water Uptake API"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = (
    "Backend for the ML project: Machine Learning-Based Analysis of "
    "Nutrient & Water Uptake in Hydroponically Grown Soybeans."
)

# ---------------------------------------------------------------
# Folder paths
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# ---------------------------------------------------------------
# The three models and their inputs (FROM THE ML TEAM)
# The ORDER of each list must match the training order exactly.
# ---------------------------------------------------------------
FEATURES_BY_NUTRIENT = {
    "K":  ["Ca", "Na", "SO4", "NO3-N", "P", "Alkalinity", "TDS", "Mn"],
    "Mg": ["Na", "CO3", "HCO3", "NO3-N", "Hardness", "TDS"],
    "N":  ["TDS", "P", "Alkalinity", "K", "Na", "Ca"],
}

# What every model predicts (FROM THE ML TEAM)
TARGET_NAME = "Water_Uptake_ml"
TARGET_UNIT = "mL"

# ---------------------------------------------------------------
# Model files
# ⚠️ DEPENDS ON ML TEAM: placeholder filenames. Change when they send files.
# ---------------------------------------------------------------
MODEL_PATHS = {
    "K":  MODELS_DIR / "k_model.joblib",
    "Mg": MODELS_DIR / "mg_model.joblib",
    "N":  MODELS_DIR / "n_model.joblib",
}

# ⚠️ DEPENDS ON ML TEAM: result files they will export
RESULTS_PATH = DATA_DIR / "model_comparison.json"
SHAP_PATH = DATA_DIR / "shap_results.json"

# True  = fake predictions (no model files needed yet)
# False = load the real models from MODEL_PATHS
USE_MOCK_MODEL = True

# ---------------------------------------------------------------
# Valid ranges per input
# ⚠️ DEPENDS ON ML TEAM: they are preparing these.
# Leave empty for now (no range checking). Later add entries like:
#     "TDS": (0, 2000),
#     "P": (0, 100),
# Format: "FeatureName": (min, max)
# ---------------------------------------------------------------
FEATURE_RANGES = {}

# ---------------------------------------------------------------
# CORS (used in a later step)
# ⚠️ DEPENDS ON FRONTEND TEAM: add their real address when known.
# ---------------------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]