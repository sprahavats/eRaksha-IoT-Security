import eraksha.database as database


def configure_temporary_database(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )


def test_database_initializes_and_has_expected_tables(
    monkeypatch, tmp_path
):
    configure_temporary_database(monkeypatch, tmp_path)
    database.initialize_database()

    with database.get_connection() as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    assert "devices" in tables
    assert "flows" in tables


def test_flow_can_be_inserted_and_retrieved(monkeypatch, tmp_path):
    configure_temporary_database(monkeypatch, tmp_path)
    database.initialize_database()

    with database.get_connection() as connection:
        connection.execute(
            """
            INSERT INTO flows (
                src_ip, dst_ip, protocol, source
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "192.168.1.10",
                "192.168.1.20",
                "TCP",
                "simulated",
            ),
        )

        row = connection.execute(
            "SELECT * FROM flows ORDER BY id DESC LIMIT 1"
        ).fetchone()

    assert row["src_ip"] == "192.168.1.10"
    assert row["dst_ip"] == "192.168.1.20"
    assert row["protocol"] == "TCP"
    assert row["source"] == "simulated"