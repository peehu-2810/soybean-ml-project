from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
    assert "name" in response.json()
    assert "version" in response.json()


def test_features():
    response = client.get("/features")
    assert response.status_code == 200

    data = response.json()

    assert "K" in data
    assert "Mg" in data
    assert "N" in data


def test_results():
    response = client.get("/results")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_prediction():
    response = client.post(
        "/predict",
        json={
            "nutrient": "K",
            "inputs": {
                "Ca": 120,
                "Na": 15,
                "SO4": 80,
                "NO3-N": 40,
                "P": 20,
                "Alkalinity": 90,
                "TDS": 500,
                "Mn": 0.5
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["nutrient"] == "K"
    assert data["predicted_water_uptake"] == 86.55
    assert data["unit"] == "mL"
    assert data["model_used"] == "mock"


def test_missing_feature():
    response = client.post(
        "/predict",
        json={
            "nutrient": "K",
            "inputs": {
                "Ca": 120,
                "Na": 15,
                "SO4": 80,
                "NO3-N": 40,
                "P": 20,
                "Alkalinity": 90,
                "TDS": 500
            }
        }
    )

    assert response.status_code == 422