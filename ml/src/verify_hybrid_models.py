import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


INPUT_FILE = "soybean_hybrid_nasa_mock_dataset.xlsx"
SHEET_NAME = "training_data"
NUTRIENTS = ["N", "K", "Mg"]
EXPECTED_FEATURES = ["DAP", "Concentration_ppm", "NASA_ET_L_m2_day"]
TARGET_COLUMN = "Water_Uptake_L_m2_day"
FORBIDDEN_FEATURES = {
    "Mock_Treatment_Factor",
    TARGET_COLUMN,
    "Source_Description",
    "Source_Type",
    "Is_Mock",
}
METRIC_METADATA_KEYS = {
    "R2": "test_R2",
    "MSE": "test_MSE",
    "RMSE": "test_RMSE",
    "MAE": "test_MAE",
}
METRIC_TOLERANCE = 1e-4


def chronological_split(dataframe):
    """Recreate the original 80/20 split over unique DAP values."""
    unique_dap = sorted(dataframe["DAP"].unique())
    split_index = int(len(unique_dap) * 0.8)
    if split_index == 0 or split_index == len(unique_dap):
        raise ValueError("At least two unique DAP values are required.")

    training_dap = set(unique_dap[:split_index])
    training_data = dataframe[dataframe["DAP"].isin(training_dap)].copy()
    testing_data = dataframe[~dataframe["DAP"].isin(training_dap)].copy()
    return training_data, testing_data


def get_fitted_feature_names(model):
    """Return available fitted input names from an estimator or wrapped estimator."""
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)

    best_estimator = getattr(model, "best_estimator_", None)
    if best_estimator is not None and hasattr(best_estimator, "feature_names_in_"):
        return list(best_estimator.feature_names_in_)

    return None


def metrics_for(actual, predicted):
    """Calculate the holdout metrics independently from the saved predictions."""
    mse = mean_squared_error(actual, predicted)
    return {
        "R2": float(r2_score(actual, predicted)),
        "MSE": float(mse),
        "RMSE": float(np.sqrt(mse)),
        "MAE": float(mean_absolute_error(actual, predicted)),
    }


def print_report(nutrient, checks):
    """Print all verification checks for one nutrient."""
    print(f"\n{'=' * 72}")
    print(f"{nutrient} VERIFICATION")
    for check_name in [
        "MODEL LOAD",
        "FEATURE ORDER",
        "LEAKAGE CHECK",
        "DATA QUALITY",
        "TIME SPLIT",
        "METRIC REPRODUCTION",
        "FINITE PREDICTIONS",
        "BEATS DUMMY BASELINE",
    ]:
        status = "PASS" if checks.get(check_name, False) else "FAIL"
        print(f"{check_name}: {status}")


def verify_nutrient(nutrient, dataset, models_folder):
    """Verify the saved model for one nutrient without fitting it."""
    checks = {
        "MODEL LOAD": False,
        "FEATURE ORDER": False,
        "LEAKAGE CHECK": False,
        "DATA QUALITY": False,
        "TIME SPLIT": False,
        "METRIC REPRODUCTION": False,
        "FINITE PREDICTIONS": False,
        "BEATS DUMMY BASELINE": False,
    }
    model_path = models_folder / f"{nutrient}_model.joblib"
    metadata_path = models_folder / f"{nutrient}_metadata.json"

    try:
        with metadata_path.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
        model = joblib.load(model_path)
        checks["MODEL LOAD"] = True
    except Exception as error:
        print(f"\n{nutrient}: unable to load model/metadata: {error}")
        print_report(nutrient, checks)
        return False

    metadata_features = metadata.get("feature_order")
    feature_order_ok = metadata_features == EXPECTED_FEATURES
    fitted_features = get_fitted_feature_names(model)
    if fitted_features is not None:
        feature_order_ok = feature_order_ok and fitted_features == EXPECTED_FEATURES
    checks["FEATURE ORDER"] = feature_order_ok

    forbidden_in_metadata = set(metadata_features or []).intersection(
        FORBIDDEN_FEATURES
    )
    forbidden_in_model = (
        set(fitted_features or []).intersection(FORBIDDEN_FEATURES)
    )
    checks["LEAKAGE CHECK"] = not forbidden_in_metadata and not forbidden_in_model

    required_columns = EXPECTED_FEATURES + [TARGET_COLUMN, "Nutrient"]
    missing_columns = set(required_columns).difference(dataset.columns)
    if missing_columns:
        print(
            f"{nutrient}: dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )
        print_report(nutrient, checks)
        return False

    nutrient_data = dataset[dataset["Nutrient"] == nutrient].copy()
    missing_target = nutrient_data[TARGET_COLUMN].isna().any()
    missing_features = nutrient_data[EXPECTED_FEATURES].isna().any().any()
    duplicate_rows = nutrient_data.duplicated(
        subset=["DAP", "Nutrient", "Concentration_ppm"]
    ).any()
    numeric_columns = nutrient_data.select_dtypes(include="number")
    finite_values = np.isfinite(numeric_columns.to_numpy(dtype=float)).all()
    checks["DATA QUALITY"] = (
        not nutrient_data.empty
        and not missing_target
        and not missing_features
        and not duplicate_rows
        and finite_values
    )

    if not checks["FEATURE ORDER"]:
        print(
            f"{nutrient}: expected metadata/model feature order "
            f"{EXPECTED_FEATURES}; metadata has {metadata_features!r}, "
            f"model has {fitted_features!r}."
        )
    if not checks["LEAKAGE CHECK"]:
        print(
            f"{nutrient}: forbidden input columns detected: "
            f"{sorted(forbidden_in_metadata.union(forbidden_in_model))}"
        )
    if not checks["DATA QUALITY"]:
        print(
            f"{nutrient}: data quality issues "
            f"(rows={len(nutrient_data)}, missing_target={missing_target}, "
            f"missing_features={missing_features}, "
            f"duplicate_keys={duplicate_rows}, finite={finite_values})."
        )

    if nutrient_data.empty or not checks["DATA QUALITY"]:
        print_report(nutrient, checks)
        return False

    try:
        training_data, testing_data = chronological_split(nutrient_data)
    except ValueError as error:
        print(f"{nutrient}: unable to recreate chronological split: {error}")
        print_report(nutrient, checks)
        return False
    train_dap_values = set(training_data["DAP"])
    test_dap_values = set(testing_data["DAP"])
    checks["TIME SPLIT"] = (
        not train_dap_values.intersection(test_dap_values)
        and training_data["DAP"].max() < testing_data["DAP"].min()
    )
    if not checks["TIME SPLIT"]:
        print(f"{nutrient}: recreated train/test DAP split is not chronological.")
        print_report(nutrient, checks)
        return False

    X_test = testing_data.loc[:, EXPECTED_FEATURES]
    if list(X_test.columns) != EXPECTED_FEATURES:
        checks["FEATURE ORDER"] = False

    try:
        predictions = np.asarray(model.predict(X_test), dtype=float)
        actual = testing_data[TARGET_COLUMN].to_numpy(dtype=float)
        prediction_shape_ok = predictions.ndim == 1 and len(predictions) == len(
            testing_data
        )
        finite_predictions = (
            prediction_shape_ok
            and np.isfinite(predictions).all()
            and not np.all(predictions == predictions[0])
        )
        checks["FINITE PREDICTIONS"] = bool(finite_predictions)

        if prediction_shape_ok and np.isfinite(predictions).all():
            independent_metrics = metrics_for(actual, predictions)
            metric_matches = True
            for metric_name, metadata_key in METRIC_METADATA_KEYS.items():
                saved_value = metadata.get(metadata_key)
                if saved_value is None or not np.isclose(
                    independent_metrics[metric_name],
                    float(saved_value),
                    atol=METRIC_TOLERANCE,
                    rtol=0,
                ):
                    metric_matches = False
                    print(
                        f"{nutrient} {metric_name} mismatch: "
                        f"independent={independent_metrics[metric_name]:.10f}, "
                        f"metadata={saved_value!r}"
                    )
            checks["METRIC REPRODUCTION"] = metric_matches

            baseline = DummyRegressor(strategy="mean")
            baseline.fit(
                np.zeros((len(training_data), 1)),
                training_data[TARGET_COLUMN],
            )
            baseline_predictions = baseline.predict(
                np.zeros((len(testing_data), 1))
            )
            baseline_metrics = metrics_for(actual, baseline_predictions)
            checks["BEATS DUMMY BASELINE"] = (
                independent_metrics["R2"] > baseline_metrics["R2"]
                and independent_metrics["RMSE"] < baseline_metrics["RMSE"]
            )

            print(f"\n{nutrient} independently calculated metrics:")
            print(
                f"R2={independent_metrics['R2']:.8f}, "
                f"MSE={independent_metrics['MSE']:.8f}, "
                f"RMSE={independent_metrics['RMSE']:.8f}, "
                f"MAE={independent_metrics['MAE']:.8f}"
            )
            print(
                f"Dummy baseline: R2={baseline_metrics['R2']:.8f}, "
                f"RMSE={baseline_metrics['RMSE']:.8f}"
            )

            examples = testing_data[
                ["DAP", "Concentration_ppm", "NASA_ET_L_m2_day"]
            ].copy()
            examples["Actual"] = actual
            examples["Predicted"] = predictions
            examples["Absolute_Error"] = np.abs(actual - predictions)
            print("\nFirst 5 test predictions:")
            print(examples.head(5).to_string(index=False))
        else:
            print(
                f"{nutrient}: prediction count mismatch or predictions are "
                "non-finite/all identical."
            )
    except Exception as error:
        print(f"{nutrient}: saved model prediction failed: {error}")

    print_report(nutrient, checks)
    return all(checks.values())


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = (
        project_root
        / "data"
        / "hybrid"
        / INPUT_FILE
    )
    models_folder = project_root / "models" / "hybrid"

    try:
        dataset = pd.read_excel(input_path, sheet_name=SHEET_NAME)
        required_columns = EXPECTED_FEATURES + [
            "Nutrient",
            TARGET_COLUMN,
            "Mock_Treatment_Factor",
            "Source_Description",
            "Source_Type",
            "Is_Mock",
        ]
        missing_columns = set(required_columns).difference(dataset.columns)
        if missing_columns:
            raise ValueError(f"Dataset is missing columns: {sorted(missing_columns)}")

        numeric_columns = EXPECTED_FEATURES + [
            TARGET_COLUMN,
            "Mock_Treatment_Factor",
        ]
        for column in numeric_columns:
            dataset[column] = pd.to_numeric(dataset[column], errors="coerce")
    except Exception as error:
        print(f"Could not load hybrid verification dataset: {error}")
        print("\nOVERALL VERIFICATION: FAIL")
        return

    overall_pass = True
    for nutrient in NUTRIENTS:
        nutrient_pass = verify_nutrient(nutrient, dataset, models_folder)
        overall_pass = nutrient_pass and overall_pass

    print(
        "\nOVERALL VERIFICATION: "
        f"{'PASS' if overall_pass else 'FAIL'}"
    )


if __name__ == "__main__":
    main()
