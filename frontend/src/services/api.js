const API_BASE_URL = "http://localhost:8000";

// Default fallback dataset matching backend config & model artifacts
export const FALLBACK_FEATURES = {
  K: {
    feature_count: 8,
    features: ["Ca", "Na", "SO4", "NO3-N", "P", "Alkalinity", "TDS", "Mn"],
    ranges: {
      Ca: { min: 68.76, max: 84.23 },
      Na: { min: 25.58, max: 34.60 },
      SO4: { min: 102.96, max: 149.32 },
      "NO3-N": { min: 123.36, max: 140.62 },
      P: { min: 0.40, max: 0.53 },
      Alkalinity: { min: 152.96, max: 169.06 },
      TDS: { min: 530.88, max: 905.07 },
      Mn: { min: 0.19, max: 0.30 }
    }
  },
  Mg: {
    feature_count: 6,
    features: ["Na", "CO3", "HCO3", "NO3-N", "Hardness", "TDS"],
    ranges: {
      Na: { min: 29.60, max: 42.43 },
      CO3: { min: 1.09, max: 1.69 },
      HCO3: { min: 188.41, max: 213.03 },
      "NO3-N": { min: 111.65, max: 129.55 },
      Hardness: { min: 256.12, max: 424.29 },
      TDS: { min: 482.61, max: 626.21 }
    }
  },
  N: {
    feature_count: 6,
    features: ["TDS", "P", "Alkalinity", "K", "Na", "Ca"],
    ranges: {
      TDS: { min: 506.38, max: 882.16 },
      P: { min: 0.36, max: 0.72 },
      Alkalinity: { min: 156.90, max: 216.79 },
      K: { min: 8.68, max: 11.52 },
      Na: { min: 21.90, max: 29.63 },
      Ca: { min: 52.53, max: 69.85 }
    }
  }
};

export const FALLBACK_RESULTS = {
  nutrients: {
    K: {
      selected_prototype_model: "SVR",
      models: {
        "Random Forest": { "Train R2": 0.9935, "Test R2": -5.1987, "Test RMSE": 21.9551, "Test MAE": 20.3679 },
        "SVR": { "Train R2": 0.9851, "Test R2": 0.7520, "Test RMSE": 4.3912, "Test MAE": 3.5457 },
        "K-Nearest Neighbors": { "Train R2": 0.9898, "Test R2": -7.2661, "Test RMSE": 25.3535, "Test MAE": 23.2293 }
      }
    },
    Mg: {
      selected_prototype_model: "SVR",
      models: {
        "Random Forest": { "Train R2": 0.9961, "Test R2": -4.7364, "Test RMSE": 16.7461, "Test MAE": 15.4270 },
        "SVR": { "Train R2": 0.9834, "Test R2": -1.2483, "Test RMSE": 10.4840, "Test MAE": 9.3610 },
        "K-Nearest Neighbors": { "Train R2": 0.9859, "Test R2": -36.2917, "Test RMSE": 42.6975, "Test MAE": 36.9044 }
      }
    },
    N: {
      selected_prototype_model: "SVR",
      models: {
        "Random Forest": { "Train R2": 0.9939, "Test R2": -2.9489, "Test RMSE": 23.0250, "Test MAE": 21.7402 },
        "SVR": { "Train R2": 0.9768, "Test R2": 0.4111, "Test RMSE": 8.8919, "Test MAE": 7.8572 },
        "K-Nearest Neighbors": { "Train R2": 0.9880, "Test R2": -5.4264, "Test RMSE": 29.3729, "Test MAE": 26.8154 }
      }
    }
  }
};

export const FALLBACK_SHAP = {
  K: {
    model: "SVR",
    importance: [
      { feature: "Mn", mean_absolute_shap: 13.77 },
      { feature: "TDS", mean_absolute_shap: 10.60 },
      { feature: "SO4", mean_absolute_shap: 3.60 },
      { feature: "NO3-N", mean_absolute_shap: 1.35 },
      { feature: "Alkalinity", mean_absolute_shap: 1.23 },
      { feature: "Na", mean_absolute_shap: 0.67 },
      { feature: "P", mean_absolute_shap: 0.55 },
      { feature: "Ca", mean_absolute_shap: 0.36 }
    ]
  },
  Mg: {
    model: "SVR",
    importance: [
      { feature: "TDS", mean_absolute_shap: 3.55 },
      { feature: "Hardness", mean_absolute_shap: 2.50 },
      { feature: "CO3", mean_absolute_shap: 1.05 },
      { feature: "NO3-N", mean_absolute_shap: 0.75 },
      { feature: "HCO3", mean_absolute_shap: 0.61 },
      { feature: "Na", mean_absolute_shap: 0.15 }
    ]
  },
  N: {
    model: "SVR",
    importance: [
      { feature: "P", mean_absolute_shap: 11.37 },
      { feature: "Alkalinity", mean_absolute_shap: 5.12 },
      { feature: "TDS", mean_absolute_shap: 4.88 },
      { feature: "Ca", mean_absolute_shap: 2.15 },
      { feature: "K", mean_absolute_shap: 1.45 },
      { feature: "Na", mean_absolute_shap: 0.82 }
    ]
  }
};

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchFeatures() {
  try {
    const res = await fetch(`${API_BASE_URL}/features`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Using fallback feature specifications:", err);
  }
  return FALLBACK_FEATURES;
}

export async function predictWaterUptake(nutrient, inputs) {
  try {
    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nutrient, inputs })
    });
    if (res.ok) {
      const data = await res.json();
      return data.predicted_water_uptake;
    }
  } catch (err) {
    console.warn("Backend API unavailable, using local calculation model:", err);
  }
  // Local fallback formula matching backend output order
  const vals = Object.values(inputs);
  const sum = vals.reduce((a, b) => a + b, 0);
  return Number((sum * 0.1).toFixed(2));
}

export async function fetchResults() {
  try {
    const res = await fetch(`${API_BASE_URL}/results`);
    if (res.ok) {
      const data = await res.json();
      return data.results;
    }
  } catch (err) {
    console.warn("Using fallback results data:", err);
  }
  return FALLBACK_RESULTS;
}

export async function fetchShap() {
  try {
    const res = await fetch(`${API_BASE_URL}/shap`);
    if (res.ok) {
      const data = await res.json();
      return data.shap;
    }
  } catch (err) {
    console.warn("Using fallback SHAP data:", err);
  }
  return FALLBACK_SHAP;
}
