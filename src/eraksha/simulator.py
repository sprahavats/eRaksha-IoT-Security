"""Generate reproducible simulated IoT network flows for testing."""

import random
from typing import Any

from eraksha.config import RANDOM_STATE
from eraksha.database import get_connection, initialize_database


DEVICES = [
    {"ip": "192.168.1.10", "name": "Security Camera"},
    {"ip": "192.168.1.11", "name": "Smart Door Lock"},
    {"ip": "192.168.1.12", "name": "Smart Thermostat"},
    {"ip": "192.168.1.13", "name": "Motion Sensor"},
    {"ip": "192.168.1.14", "name": "Smart Speaker"},
]


def generate_flow(
    rng: random.Random,
    device: dict[str, str],
    suspicious: bool = False,
) -> dict[str, Any]:
    """Generate one synthetic flow with known ground-truth labels."""

    if suspicious:
        # Deliberately unusual transfer volume and duration.
        bytes_sent = rng.randint(150_000, 500_000)
        bytes_received = rng.randint(1_000, 5_000)
        duration = rng.uniform(0.05, 0.3)
        dst_port = rng.choice([4444, 31337, 12345])
    else:
        bytes_sent = rng.randint(200, 8_000)
        bytes_received = rng.randint(200, 10_000)
        duration = rng.uniform(0.5, 15.0)
        dst_port = rng.choice([53, 80, 443, 1883, 5683])

    return {
        "src_ip": device["ip"],
        "dst_ip": f"192.168.1.{rng.randint(100, 200)}",
        "src_port": rng.randint(20_000, 65_535),
        "dst_port": dst_port,
        "protocol": rng.choice(["TCP", "UDP"]),
        "bytes_sent": bytes_sent,
        "bytes_received": bytes_received,
        "duration_seconds": round(duration, 4),
        "source": "simulated",
        # This is the simulator's known label, not the model's prediction.
        "ground_truth_anomaly": int(suspicious),
    }


def generate_dataset(
    normal_count: int = 200,
    suspicious_count: int = 30,
    seed: int = RANDOM_STATE,
) -> list[dict[str, Any]]:
    """Generate a repeatable dataset with known labels."""

    if normal_count < 1 or suspicious_count < 1:
        raise ValueError("Both sample counts must be positive.")

    rng = random.Random(seed)
    flows = []

    for _ in range(normal_count):
        device = rng.choice(DEVICES)
        flows.append(generate_flow(rng, device, suspicious=False))

    for _ in range(suspicious_count):
        device = rng.choice(DEVICES)
        flows.append(generate_flow(rng, device, suspicious=True))

    rng.shuffle(flows)
    return flows


def store_flows(flows: list[dict[str, Any]]) -> int:
    """Insert generated flows into SQLite without storing ground-truth labels."""

    initialize_database()

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO flows (
                src_ip, dst_ip, src_port, dst_port, protocol,
                bytes_sent, bytes_received, duration_seconds, source
            )
            VALUES (
                :src_ip, :dst_ip, :src_port, :dst_port, :protocol,
                :bytes_sent, :bytes_received, :duration_seconds, :source
            )
            """,
            flows,
        )

    return len(flows)


def main() -> None:
    flows = generate_dataset()
    count = store_flows(flows)

    normal = sum(
        flow["ground_truth_anomaly"] == 0 for flow in flows
    )
    suspicious = sum(
        flow["ground_truth_anomaly"] == 1 for flow in flows
    )

    print("eRaksha synthetic traffic generator")
    print(f"Flows stored: {count}")
    print(f"Normal examples: {normal}")
    print(f"Suspicious examples: {suspicious}")
    print("Source: simulated")
    print("Database: initialized successfully")


if __name__ == "__main__":
    main()