import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


INPUT_FILE = "soybean_hybrid_nasa_mock_dataset.xlsx"
SHEET_NAME = "training_data"
NUTRIENTS = ["N", "K", "Mg"]
FEATURES = ["DAP", "Concentration_ppm", "NASA_ET_L_m2_day"]
TARGET_COLUMN = "Water_Uptake_L_m2_day"
DATA_PROVENANCE = (
    "HYBRID PROTOTYPE: NASA Table 3 provides real soybean daily "
    "evapotranspiration baseline; N/K/Mg concentration treatment effects are "
    "synthetic/mock and are not direct NASA experimental treatments."
)


def chronological_split(dataframe, nutrient):
    """Split by unique DAP values so rows on the same day stay together."""
    unique_dap = sorted(dataframe["DAP"].unique())
    split_index = int(len(unique_dap) * 0.8)
    if split_index == 0 or split_index == len(unique_dap):
        raise ValueError(
            f"{nutrient} needs at least two unique DAP values for an 80/20 split."
        )

    training_dap = set(unique_dap[:split_index])
    training_data = dataframe[dataframe["DAP"].isin(training_dap)].copy()
    testing_data = dataframe[~dataframe["DAP"].isin(training_dap)].copy()
    if set(training_data["DAP"]).intersection(testing_data["DAP"]):
        raise ValueError(f"{nutrient} has DAP values shared between train and test.")
    return training_data, testing_data


def calculate_metrics(actual, predicted):
    """Calculate all requested regression metrics."""
    mse = mean_squared_error(actual, predicted)
    return {
        "R2": float(r2_score(actual, predicted)),
        "MSE": float(mse),
        "RMSE": float(np.sqrt(mse)),
        "MAE": float(mean_absolute_error(actual, predicted)),
    }


def build_models():
    """Create the three requested model candidates."""
    return {
        "Random Forest": RandomForestRegressor(random_state=42),
        "SVR": GridSearchCV(
            estimator=Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("svr", SVR()),
                ]
            ),
            param_grid={
                "svr__C": [0.1, 1, 10, 100],
                "svr__kernel": ["linear", "rbf"],
                "svr__gamma": ["scale", "auto"],
            },
            cv=5,
            scoring="neg_mean_squared_error",
        ),
        "KNN": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("knn", KNeighborsRegressor()),
            ]
        ),
    }


def evaluate_model(model, X_train, y_train, X_test, y_test, nutrient, model_name):
    """Fit on training data and score train/test predictions."""
    model.fit(X_train, y_train)

    # Keep named columns and verify that model inputs preserve the feature contract.
    if list(X_train.columns) != FEATURES or list(X_test.columns) != FEATURES:
        raise ValueError(f"{nutrient} {model_name} input feature order is incorrect.")

    train_predictions = np.asarray(model.predict(X_train), dtype=float)
    test_predictions = np.asarray(model.predict(X_test), dtype=float)
    if not np.isfinite(train_predictions).all() or not np.isfinite(
        test_predictions
    ).all():
        raise ValueError(f"{nutrient} {model_name} produced non-finite predictions.")

    train_metrics = calculate_metrics(y_train, train_predictions)
    test_metrics = calculate_metrics(y_test, test_predictions)
    return train_metrics, test_metrics


def train_nutrient(dataframe, nutrient, models_folder):
    """Train, compare, and save the best test-RMSE model for one nutrient."""
    nutrient_data = dataframe[dataframe["Nutrient"] == nutrient].copy()
    if nutrient_data.empty:
        raise ValueError(f"No rows found for nutrient {nutrient}.")

    nutrient_data = nutrient_data.sort_values("DAP").reset_index(drop=True)
    training_data, testing_data = chronological_split(nutrient_data, nutrient)
    if len(training_data) < 5:
        raise ValueError(
            f"{nutrient} has fewer than 5 training rows; SVR GridSearchCV cv=5 "
            "cannot run."
        )

    X_train = training_data.loc[:, FEATURES]
    y_train = training_data[TARGET_COLUMN]
    X_test = testing_data.loc[:, FEATURES]
    y_test = testing_data[TARGET_COLUMN]

    if list(X_train.columns) != FEATURES or list(X_test.columns) != FEATURES:
        raise ValueError(f"{nutrient} input feature order does not match {FEATURES}.")

    result_rows = []
    fitted_models = {}
    model_candidates = build_models()

    for model_name, model in model_candidates.items():
        train_metrics, test_metrics = evaluate_model(
            model,
            X_train,
            y_train,
            X_test,
            y_test,
            nutrient,
            model_name,
        )
        fitted_models[model_name] = model
        best_parameters = (
            model.best_params_ if isinstance(model, GridSearchCV) else {}
        )
        result_rows.append(
            {
                "Nutrient": nutrient,
                "Model": model_name,
                **{f"Train_{key}": value for key, value in train_metrics.items()},
                **{f"Test_{key}": value for key, value in test_metrics.items()},
                "Best_Parameters": json.dumps(best_parameters, sort_keys=True),
                "Train_DAP_Start": float(training_data["DAP"].min()),
                "Train_DAP_End": float(training_data["DAP"].max()),
                "Test_DAP_Start": float(testing_data["DAP"].min()),
                "Test_DAP_End": float(testing_data["DAP"].max()),
                "Train_Rows": len(training_data),
                "Test_Rows": len(testing_data),
                "Feature_Order": json.dumps(FEATURES),
            }
        )

    # The mean-only dummy is included as context and is not a selectable model.
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(np.zeros((len(training_data), 1)), y_train)
    dummy_train_predictions = dummy.predict(np.zeros((len(training_data), 1)))
    dummy_test_predictions = dummy.predict(np.zeros((len(testing_data), 1)))
    if not np.isfinite(dummy_train_predictions).all() or not np.isfinite(
        dummy_test_predictions
    ).all():
        raise ValueError(f"{nutrient} dummy baseline produced non-finite predictions.")
    dummy_train_metrics = calculate_metrics(y_train, dummy_train_predictions)
    dummy_test_metrics = calculate_metrics(y_test, dummy_test_predictions)
    result_rows.append(
        {
            "Nutrient": nutrient,
            "Model": "Dummy Mean Baseline",
            **{
                f"Train_{key}": value
                for key, value in dummy_train_metrics.items()
            },
            **{f"Test_{key}": value for key, value in dummy_test_metrics.items()},
            "Best_Parameters": "{}",
            "Train_DAP_Start": float(training_data["DAP"].min()),
            "Train_DAP_End": float(training_data["DAP"].max()),
            "Test_DAP_Start": float(testing_data["DAP"].min()),
            "Test_DAP_End": float(testing_data["DAP"].max()),
            "Train_Rows": len(training_data),
            "Test_Rows": len(testing_data),
            "Feature_Order": json.dumps([]),
        }
    )

    # Choose among the three requested ML models by test RMSE.
    selected_row = min(
        (row for row in result_rows if row["Model"] in fitted_models),
        key=lambda row: row["Test_RMSE"],
    )
    selected_model_name = selected_row["Model"]
    selected_model = fitted_models[selected_model_name]
    model_path = models_folder / f"{nutrient}_model.joblib"
    joblib.dump(selected_model, model_path)

    metadata = {
        "nutrient": nutrient,
        "feature_order": FEATURES,
        "target": TARGET_COLUMN,
        "target_unit": "L/m2/day",
        "model_type": selected_model_name,
        "train_DAP_range": {
            "start": float(training_data["DAP"].min()),
            "end": float(training_data["DAP"].max()),
        },
        "test_DAP_range": {
            "start": float(testing_data["DAP"].min()),
            "end": float(testing_data["DAP"].max()),
        },
        "train_rows": len(training_data),
        "test_rows": len(testing_data),
        "train_R2": selected_row["Train_R2"],
        "test_R2": selected_row["Test_R2"],
        "test_MSE": selected_row["Test_MSE"],
        "test_RMSE": selected_row["Test_RMSE"],
        "test_MAE": selected_row["Test_MAE"],
        "data_provenance": DATA_PROVENANCE,
    }
    metadata_path = models_folder / f"{nutrient}_metadata.json"
    with metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=4, allow_nan=False)

    print(f"\n{nutrient} model comparison")
    comparison = pd.DataFrame(result_rows)
    print(
        comparison[
            ["Model", "Train_R2", "Test_R2", "Test_RMSE", "Test_MAE"]
        ].to_string(index=False, float_format=lambda value: f"{value:.4f}")
    )
    print(f"Selected model: {selected_model_name}")
    print(
        f"Test R2={selected_row['Test_R2']:.4f}, "
        f"Test RMSE={selected_row['Test_RMSE']:.4f}, "
        f"Test MAE={selected_row['Test_MAE']:.4f}"
    )
    print(f"Saved model: {model_path}")
    print(f"Saved metadata: {metadata_path}")
    return result_rows, metadata


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = (
        project_root
        / "data"
        / "hybrid"
        / INPUT_FILE
    )
    models_folder = project_root / "models" / "hybrid"
    results_folder = project_root / "results"
    models_folder.mkdir(parents=True, exist_ok=True)
    results_folder.mkdir(parents=True, exist_ok=True)

    planned_outputs = [
        *(models_folder / f"{nutrient}_{suffix}" for nutrient in NUTRIENTS for suffix in ("model.joblib", "metadata.json")),
        results_folder / "hybrid_model_comparison.csv",
    ]
    existing_outputs = [path for path in planned_outputs if path.exists()]
    if existing_outputs:
        raise FileExistsError(
            "Refusing to overwrite existing hybrid model/output files: "
            + ", ".join(str(path) for path in existing_outputs)
        )

    dataframe = pd.read_excel(input_path, sheet_name=SHEET_NAME)
    required_columns = [
        "DAP",
        "Nutrient",
        "Concentration_ppm",
        "NASA_ET_L_m2_day",
        "Mock_Treatment_Factor",
        TARGET_COLUMN,
        "Source_Description",
        "Source_Type",
        "Is_Mock",
    ]
    missing_columns = set(required_columns).difference(dataframe.columns)
    if missing_columns:
        raise ValueError(
            f"{INPUT_FILE} sheet {SHEET_NAME!r} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    # Target leakage and provenance fields are validated but never selected as X.
    if dataframe[TARGET_COLUMN].isna().any():
        raise ValueError(f"{TARGET_COLUMN} contains missing values.")
    duplicate_keys = dataframe.duplicated(
        subset=["DAP", "Nutrient", "Concentration_ppm"]
    )
    if duplicate_keys.any():
        raise ValueError(
            "Dataset contains duplicate DAP + Nutrient + Concentration_ppm rows: "
            f"{int(duplicate_keys.sum())}"
        )

    for column in ["DAP", "Concentration_ppm", "NASA_ET_L_m2_day", TARGET_COLUMN]:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="raise")
    if not np.isfinite(
        dataframe[["DAP", "Concentration_ppm", "NASA_ET_L_m2_day", TARGET_COLUMN]]
        .to_numpy(dtype=float)
    ).all():
        raise ValueError("The required numeric dataset columns contain NaN or infinity.")

    all_rows = []
    selected_metadata = {}
    for nutrient in NUTRIENTS:
        rows, metadata = train_nutrient(dataframe, nutrient, models_folder)
        all_rows.extend(rows)
        selected_metadata[nutrient] = metadata

    comparison_path = results_folder / "hybrid_model_comparison.csv"
    pd.DataFrame(all_rows).to_csv(comparison_path, index=False)
    print(f"\nSaved evaluation comparison to {comparison_path}")

    print("\nSelected hybrid prototype models")
    for nutrient in NUTRIENTS:
        metadata = selected_metadata[nutrient]
        print(
            f"{nutrient}: {metadata['model_type']} | "
            f"Test R2={metadata['test_R2']:.4f} | "
            f"Test RMSE={metadata['test_RMSE']:.4f} | "
            f"Test MAE={metadata['test_MAE']:.4f}"
        )
    print(
        "\nHYBRID PROTOTYPE: NASA Table 3 provides real soybean daily "
        "evapotranspiration baseline; N/K/Mg concentration treatment effects "
        "are synthetic/mock and are not direct NASA experimental treatments."
    )


if __name__ == "__main__":
    main()
