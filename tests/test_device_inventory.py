
import pytest

from eraksha import database
from eraksha.device_inventory import list_devices, upsert_device


def use_temporary_database(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )


def test_device_can_be_added(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)

    upsert_device({
        "ip_address": "192.168.1.10",
        "mac_address": "02:00:00:00:00:10",
        "hostname": "security-camera",
        "vendor": "Example Vendor",
    })

    devices = list_devices()

    assert len(devices) == 1
    assert devices[0]["ip_address"] == "192.168.1.10"
    assert devices[0]["hostname"] == "security-camera"
    assert devices[0]["source"] == "simulated"


def test_existing_device_is_updated_not_duplicated(
    monkeypatch, tmp_path
):
    use_temporary_database(monkeypatch, tmp_path)

    upsert_device({
        "ip_address": "192.168.1.10",
        "hostname": "old-name",
    })
    upsert_device({
        "ip_address": "192.168.1.10",
        "hostname": "new-name",
    })

    devices = list_devices()

    assert len(devices) == 1
    assert devices[0]["hostname"] == "new-name"


def test_missing_ip_address_is_rejected():
    with pytest.raises(ValueError):
        upsert_device({"hostname": "unknown-device"})


def test_invalid_source_is_rejected():
    with pytest.raises(ValueError):
        upsert_device({
            "ip_address": "192.168.1.10",
            "source": "unknown",
        })

def test_observed_source_is_persisted(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)

    upsert_device({
        "ip_address": "192.168.1.20",
        "hostname": "observed-device",
        "source": "observed",
    })

    devices = list_devices()

    assert len(devices) == 1
    assert devices[0]["source"] == "observed"
