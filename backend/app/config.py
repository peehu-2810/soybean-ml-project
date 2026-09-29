from pathlib import Path

APP_NAME = "Soybean Water Uptake API"
APP_VERSION = "0.1.0"

APP_DESCRIPTION = (
    "Backend for the ML project: Machine Learning-Based Analysis of "
    "Nutrient & Water Uptake in Hydroponically Grown Soybeans."
)

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"


# Features expected by the actual models
FEATURES_BY_NUTRIENT = {
    "K": [
        "Ca",
        "Na",
        "SO4",
        "NO3-N",
        "P",
        "Alkalinity",
        "TDS",
        "Mn",
    ],

    "Mg": [
        "Na",
        "CO3",
        "HCO3",
        "NO3-N",
        "Hardness",
        "TDS",
    ],

    "N": [
        "TDS",
        "P",
        "Alkalinity",
        "K",
        "Na",
        "Ca",
    ],
}


# Prediction target
TARGET_NAME = "Water_Uptake_ml"
TARGET_UNIT = "mL"


# Actual model files
MODEL_PATHS = {
    "K": MODELS_DIR / "K_best_model.joblib",
    "Mg": MODELS_DIR / "Mg_best_model.joblib",
    "N": MODELS_DIR / "N_best_model.joblib",
}


# Result files
RESULTS_PATH = DATA_DIR / "model_comparison.json"
SHAP_PATH = DATA_DIR / "shap_feature_importance.json"


# IMPORTANT:
# False = use the actual ML models
USE_MOCK_MODEL = False


# Allowed ranges for model inputs
FEATURE_RANGES_BY_NUTRIENT = {

    "K": {
        "Ca": (68.7643691016326, 84.22804232055674),
        "Na": (25.57772938198423, 34.5977962472385),
        "SO4": (102.959934404581, 149.3231229022185),
        "NO3-N": (123.36084454755, 140.6248038138131),
        "P": (0.4003542998440269, 0.5272007940974959),
        "Alkalinity": (152.9624415264109, 169.0622427899847),
        "TDS": (530.8798156062609, 905.0690735068822),
        "Mn": (0.1871003910025895, 0.3042961821913259),
    },

    "Mg": {
        "Na": (29.60383131700535, 42.42945026583278),
        "CO3": (1.086511579992025, 1.694314190190871),
        "HCO3": (188.4077788937378, 213.0314640460722),
        "NO3-N": (111.6529735943931, 129.5470832023506),
        "Hardness": (256.1235021706705, 424.2882877968141),
        "TDS": (482.6063560710902, 626.2125005006513),
    },

    "N": {
        "TDS": (506.3796388671818, 882.1591613398799),
        "P": (0.3608065975224045, 0.7206493052110229),
        "Alkalinity": (156.9012744795513, 216.7889368017414),
        "K": (8.679543386915723, 11.52302985640802),
        "Na": (21.89867313786774, 29.62931713334702),
        "Ca": (52.53093922963301, 69.85296844994114),
    },
}


# Frontend URLs
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]