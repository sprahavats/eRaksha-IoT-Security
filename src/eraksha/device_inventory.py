
"""Device inventory operations for the eRaksha prototype."""

from typing import Any

from eraksha.database import get_connection, initialize_database


def upsert_device(device: dict[str, Any]) -> None:
    """Insert a device or update its latest observed details."""

    ip_address = device.get("ip_address")
    if not isinstance(ip_address, str) or not ip_address.strip():
        raise ValueError("Device must have a non-empty IP address.")

    source = device.get("source", "simulated")
    if source not in {"simulated", "observed"}:
        raise ValueError("Source must be 'simulated' or 'observed'.")

    initialize_database()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO devices (
                ip_address, mac_address, hostname, vendor, source
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(ip_address) DO UPDATE SET
                mac_address = COALESCE(
                    excluded.mac_address, devices.mac_address
                ),
                hostname = COALESCE(
                    excluded.hostname, devices.hostname
                ),
                vendor = COALESCE(
                    excluded.vendor, devices.vendor
                ),
                source = excluded.source,
                last_seen = CURRENT_TIMESTAMP
            """,
            (
                ip_address.strip(),
                device.get("mac_address"),
                device.get("hostname"),
                device.get("vendor"),
                source,
            ),
        )



def list_devices() -> list[dict[str, Any]]:
    """Return the inventory in a stable order."""

    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, ip_address, mac_address, hostname, vendor, source,
                   first_seen, last_seen
            FROM devices
            ORDER BY ip_address
            """
        ).fetchall()

    return [dict(row) for row in rows]
