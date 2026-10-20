
"""Device discovery with a safe, simulated default."""

from typing import Any

from eraksha.device_inventory import upsert_device


SIMULATED_DEVICES = [
    {
        "ip_address": "192.168.1.10",
        "mac_address": "02:00:00:00:00:10",
        "hostname": "security-camera",
        "vendor": "Example Vendor",
    },
    {
        "ip_address": "192.168.1.11",
        "mac_address": "02:00:00:00:00:11",
        "hostname": "smart-lock",
        "vendor": "Example Vendor",
    },
    {
        "ip_address": "192.168.1.12",
        "mac_address": "02:00:00:00:00:12",
        "hostname": "smart-thermostat",
        "vendor": "Example Vendor",
    },
    {
        "ip_address": "192.168.1.13",
        "mac_address": "02:00:00:00:00:13",
        "hostname": "motion-sensor",
        "vendor": "Example Vendor",
    },
    {
        "ip_address": "192.168.1.14",
        "mac_address": "02:00:00:00:00:14",
        "hostname": "smart-speaker",
        "vendor": "Example Vendor",
    },
]


def discover_simulated_devices() -> list[dict[str, Any]]:
    """Load simulated device records into the inventory."""

    discovered = []

    for device in SIMULATED_DEVICES:
        record = {**device, "source": "simulated"}
        upsert_device(record)
        discovered.append(record)

    return discovered


def main() -> None:
    devices = discover_simulated_devices()

    print("eRaksha device discovery")
    print("Mode: simulated — no network scan performed")
    print(f"Devices discovered: {len(devices)}")

    for device in devices:
        print(
            f"- {device['hostname']}: {device['ip_address']} "
            f"[{device['source']}]"
        )


if __name__ == "__main__":
    main()
