
from eraksha import database
from eraksha.discovery import discover_simulated_devices
from eraksha.device_inventory import list_devices


def test_simulated_discovery_populates_inventory(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )

    discovered = discover_simulated_devices()
    inventory = list_devices()

    assert len(discovered) == 5
    assert len(inventory) == 5
    assert all(
        device["source"] == "simulated"
        for device in discovered
    )


def test_repeated_discovery_does_not_duplicate_devices(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )

    discover_simulated_devices()
    discover_simulated_devices()

    assert len(list_devices()) == 5
