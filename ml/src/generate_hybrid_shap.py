import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


INPUT_FILE = "soybean_hybrid_nasa_mock_dataset.xlsx"
SHEET_NAME = "training_data"
NUTRIENTS = ["N", "K", "Mg"]
FEATURES = ["DAP", "Concentration_ppm", "NASA_ET_L_m2_day"]
TARGET_COLUMN = "Water_Uptake_L_m2_day"
BACKGROUND_SIZE = 20
EXPLANATION_SIZE = 30
RANDOM_STATE = 42
TITLE_PREFIX = "HYBRID PROTOTYPE SHAP"


def load_nutrient_data(dataset, nutrient):
    """Filter one nutrient and return its finite, ordered feature matrix."""
    nutrient_data = dataset.loc[dataset["Nutrient"] == nutrient].copy()
    if nutrient_data.empty:
        raise ValueError(f"No rows found for nutrient {nutrient}.")

    missing_features = [feature for feature in FEATURES if feature not in dataset]
    if missing_features:
        raise ValueError(
            f"Dataset is missing required input features: {missing_features}"
        )

    feature_data = nutrient_data.loc[:, FEATURES].copy()
    if list(feature_data.columns) != FEATURES:
        raise ValueError(f"{nutrient} input feature order is incorrect.")
    values = feature_data.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(
            f"{nutrient} input features contain NaN or infinite values."
        )
    return feature_data


def load_model(models_folder, nutrient):
    """Load the saved estimator and inspect metadata for preprocessing details."""
    model_path = models_folder / f"{nutrient}_model.joblib"
    model = joblib.load(model_path)
    print(
        f"{nutrient} loaded model Python type: "
        f"{type(model).__module__}.{type(model).__name__}"
    )

    metadata_path = models_folder / f"{nutrient}_metadata.json"
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)
    if metadata.get("feature_order") != FEATURES:
        raise ValueError(
            f"{metadata_path.name} feature_order does not match {FEATURES}."
        )
    preprocessing_info = {
        key: value
        for key, value in metadata.items()
        if "scaler" in key.casefold() or "preprocess" in key.casefold()
    }

    fitted_features = getattr(model, "feature_names_in_", None)
    if fitted_features is not None and list(fitted_features) != FEATURES:
        raise ValueError(
            f"{model_path.name} expects {list(fitted_features)}, "
            f"not {FEATURES}."
        )
    return model, metadata, preprocessing_info


def explain_model(nutrient, model, feature_data):
    """Calculate model-agnostic SHAP using the verified predict input path."""
    background = feature_data.sample(
        n=min(BACKGROUND_SIZE, len(feature_data)),
        random_state=RANDOM_STATE,
    )
    explanation_data = feature_data.sample(
        n=min(EXPLANATION_SIZE, len(feature_data)),
        random_state=RANDOM_STATE,
    )

    # Rebuild a named frame if SHAP supplies an ndarray to the prediction callable.
    def predict_saved_model(values):
        if isinstance(values, pd.DataFrame):
            model_input = values.loc[:, FEATURES].copy()
        else:
            model_input = pd.DataFrame(values, columns=FEATURES)
        if list(model_input.columns) != FEATURES:
            raise ValueError(f"{nutrient} prediction feature order changed.")
        # Match verify_hybrid_models.py: pass the raw, named DataFrame directly
        # to the saved object's predict method without adding preprocessing.
        return model.predict(model_input)

    masker = shap.maskers.Independent(background)
    explainer = shap.Explainer(
        predict_saved_model,
        masker,
        algorithm="permutation",
        feature_names=FEATURES,
        seed=RANDOM_STATE,
    )
    explanation = explainer(explanation_data)
    shap_values = np.asarray(explanation.values, dtype=float)

    expected_shape = (len(explanation_data), len(FEATURES))
    if shap_values.shape != expected_shape:
        raise ValueError(
            f"{nutrient} SHAP returned shape {shap_values.shape}; "
            f"expected {expected_shape}."
        )
    if not np.isfinite(shap_values).all():
        raise ValueError(f"{nutrient} SHAP values contain NaN or infinity.")

    mean_absolute_values = np.abs(shap_values).mean(axis=0)
    return sorted(
        [
            {
                "feature": feature,
                "mean_absolute_shap": float(value),
            }
            for feature, value in zip(FEATURES, mean_absolute_values)
        ],
        key=lambda item: item["mean_absolute_shap"],
        reverse=True,
    )


def save_importance_plot(nutrient, importance, plot_folder):
    """Save a simple ranked mean-absolute-SHAP horizontal bar chart."""
    ordered_importance = list(reversed(importance))
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.barh(
        [item["feature"] for item in ordered_importance],
        [item["mean_absolute_shap"] for item in ordered_importance],
    )
    axis.set_title(f"{TITLE_PREFIX}: {nutrient}")
    axis.set_xlabel("Mean Absolute SHAP Value")
    axis.set_ylabel("Feature")
    axis.grid(axis="x", alpha=0.3)
    figure.tight_layout()
    plot_path = plot_folder / f"{nutrient}_shap_importance.png"
    figure.savefig(plot_path, dpi=150)
    plt.close(figure)
    return plot_path


def main():
    project_root = Path(__file__).resolve().parent.parent
    dataset_path = (
        project_root
        / "data"
        / "hybrid"
        / INPUT_FILE
    )
    models_folder = project_root / "models" / "hybrid"
    results_folder = project_root / "results"
    plot_folder = project_root / "results" / "shap"
    results_folder.mkdir(parents=True, exist_ok=True)
    plot_folder.mkdir(parents=True, exist_ok=True)

    dataset = pd.read_excel(dataset_path, sheet_name=SHEET_NAME)
    required_columns = ["Nutrient"] + FEATURES + [TARGET_COLUMN]
    missing_columns = set(required_columns).difference(dataset.columns)
    if missing_columns:
        raise ValueError(
            f"{INPUT_FILE} sheet {SHEET_NAME!r} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    json_results = {}
    csv_rows = []
    for nutrient in NUTRIENTS:
        feature_data = load_nutrient_data(dataset, nutrient)
        model, metadata, preprocessing_info = load_model(models_folder, nutrient)
        print(
            f"{nutrient} preprocessing metadata: "
            f"{preprocessing_info or 'not specified'}"
        )
        importance = explain_model(nutrient, model, feature_data)
        json_results[nutrient] = {
            "model": metadata.get("model_type", type(model).__name__),
            "method": "model-agnostic SHAP",
            "label": TITLE_PREFIX,
            "importance": importance,
        }

        print(f"\n{TITLE_PREFIX} - {nutrient}")
        for rank, item in enumerate(importance, start=1):
            print(
                f"{rank}. {item['feature']}: "
                f"{item['mean_absolute_shap']:.8f}"
            )
            csv_rows.append(
                {
                    "Nutrient": nutrient,
                    "Feature": item["feature"],
                    "Mean_Absolute_SHAP": item["mean_absolute_shap"],
                    "Rank": rank,
                }
            )
        save_importance_plot(nutrient, importance, plot_folder)
        print(f"{nutrient} SHAP: PASS")

    json_path = results_folder / "hybrid_shap_feature_importance.json"
    with json_path.open("w", encoding="utf-8") as output_file:
        json.dump(json_results, output_file, indent=4, allow_nan=False)

    csv_path = results_folder / "hybrid_shap_feature_importance.csv"
    pd.DataFrame(
        csv_rows,
        columns=["Nutrient", "Feature", "Mean_Absolute_SHAP", "Rank"],
    ).to_csv(csv_path, index=False)

    print(f"\nSaved SHAP JSON: {json_path}")
    print(f"Saved SHAP CSV: {csv_path}")
    print("SHAP GENERATION: COMPLETE")


if __name__ == "__main__":
    main()
