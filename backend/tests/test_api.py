import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


K_INPUT = {
    "nutrient": "K",
    "inputs": {
        "Ca": 68.7643691016326,
        "Na": 29.02478755185501,
        "SO4": 103.2697672487215,
        "NO3-N": 132.3667128542698,
        "P": 0.4373704655753921,
        "Alkalinity": 161.4488742844821,
        "TDS": 554.9048095837453,
        "Mn": 0.2087112470343169
    }
}

MG_INPUT = {
    "nutrient": "Mg",
    "inputs": {
        "Na": 35.38254657813223,
        "CO3": 1.212827569764112,
        "HCO3": 197.8158187607748,
        "NO3-N": 120.0511653050979,
        "Hardness": 258.5000525934982,
        "TDS": 495.985895433602
    }
}

N_INPUT = {
    "nutrient": "N",
    "inputs": {
        "TDS": 527.4507122951685,
        "P": 0.3972347139765763,
        "Alkalinity": 173.2384426905035,
        "K": 11.52302985640802,
        "Na": 24.53169325055333,
        "Ca": 59.06345217220328
    }
}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_info():
    response = client.get("/info")
    assert response.status_code == 200


def test_features():
    response = client.get("/features")
    assert response.status_code == 200

    data = response.json()

    assert data["K"]["feature_count"] == 8
    assert data["Mg"]["feature_count"] == 6
    assert data["N"]["feature_count"] == 6


def test_results():
    response = client.get("/results")
    assert response.status_code == 200


def test_shap():
    response = client.get("/shap")
    assert response.status_code == 200


def test_predict_k():
    response = client.post("/predict", json=K_INPUT)

    assert response.status_code == 200
    assert response.json()["nutrient"] == "K"
    assert response.json()["unit"] == "mL"
    assert response.json()["predicted_water_uptake"] == pytest.approx(
        67.19450405785652
    )


def test_predict_mg():
    response = client.post("/predict", json=MG_INPUT)

    assert response.status_code == 200
    assert response.json()["nutrient"] == "Mg"
    assert response.json()["unit"] == "mL"
    assert response.json()["predicted_water_uptake"] == pytest.approx(
        55.04666666666666
    )


def test_predict_n():
    response = client.post("/predict", json=N_INPUT)

    assert response.status_code == 200
    assert response.json()["nutrient"] == "N"
    assert response.json()["unit"] == "mL"
    assert response.json()["predicted_water_uptake"] == pytest.approx(
        59.86574548148543
    )


def test_missing_feature():
    data = K_INPUT.copy()
    data["inputs"] = K_INPUT["inputs"].copy()
    del data["inputs"]["Mn"]

    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_extra_feature():
    data = K_INPUT.copy()
    data["inputs"] = K_INPUT["inputs"].copy()
    data["inputs"]["WrongFeature"] = 10

    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_out_of_range():
    data = K_INPUT.copy()
    data["inputs"] = K_INPUT["inputs"].copy()
    data["inputs"]["Ca"] = 999

    response = client.post("/predict", json=data)

    assert response.status_code == 422


def test_invalid_nutrient():
    data = K_INPUT.copy()
    data["nutrient"] = "X"

    response = client.post("/predict", json=data)

    assert response.status_code == 422