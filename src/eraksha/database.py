"""SQLite storage for discovered devices and network-flow observations."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from eraksha.config import DATA_DIR, DATABASE_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL UNIQUE,
    mac_address TEXT,
    hostname TEXT,
    vendor TEXT, source TEXT NOT NULL DEFAULT 'simulated',
    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    src_ip TEXT NOT NULL,
    dst_ip TEXT NOT NULL,
    src_port INTEGER,
    dst_port INTEGER,
    protocol TEXT NOT NULL,
    bytes_sent INTEGER NOT NULL DEFAULT 0,
    bytes_received INTEGER NOT NULL DEFAULT 0,
    duration_seconds REAL NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'simulated',
    anomaly_score REAL,
    is_anomaly INTEGER,
    explanation TEXT
);

CREATE INDEX IF NOT EXISTS idx_flows_timestamp
    ON flows(timestamp);

CREATE INDEX IF NOT EXISTS idx_flows_src_ip
    ON flows(src_ip);

CREATE INDEX IF NOT EXISTS idx_flows_anomaly
    ON flows(is_anomaly);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Open a database connection and close it reliably."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10.0,
    )
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()



def initialize_database() -> None:
    """Create the schema and apply safe additive migrations."""

    with get_connection() as connection:
        connection.executescript(SCHEMA)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(devices)"
            )
        }

        if "source" not in columns:
            connection.execute(
                """
                ALTER TABLE devices
                ADD COLUMN source TEXT NOT NULL DEFAULT 'simulated'
                """
            )
