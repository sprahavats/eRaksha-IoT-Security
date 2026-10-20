
from eraksha import database
from eraksha.dashboard import app
from eraksha.discovery import discover_simulated_devices
from eraksha.simulator import generate_dataset, store_flows


def test_dashboard_displays_inventory_and_metrics(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )

    discover_simulated_devices()
    store_flows(generate_dataset(20, 5, seed=42))

    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"eRaksha IoT Security" in response.data
    assert b"security-camera" in response.data
    assert b"simulated" in response.data


def test_status_api_returns_inventory_counts(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )

    discover_simulated_devices()
    store_flows(generate_dataset(20, 5, seed=42))

    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/api/status")

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["device_count"] == 5
    assert payload["flow_count"] == 25
    assert payload["device_sources"]["simulated"] == 5
    assert payload["device_sources"]["observed"] == 0
    assert payload["mode"] == "prototype"
