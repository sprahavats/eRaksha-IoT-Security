from eraksha import database
from eraksha.analysis_service import analyze_stored_flows
from eraksha.simulator import generate_dataset, store_flows


def test_analysis_persists_scores_and_explanations(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        database, "DATABASE_PATH", tmp_path / "test.db"
    )

    flows = generate_dataset(
        normal_count=80,
        suspicious_count=20,
        seed=42,
    )
    store_flows(flows)

    analyzed = analyze_stored_flows()

    assert analyzed == 100

    with database.get_connection() as connection:
        rows = connection.execute(
            """
            SELECT anomaly_score, is_anomaly, explanation
            FROM flows
            """
        ).fetchall()

    assert len(rows) == 100
    assert all(row["anomaly_score"] is not None for row in rows)
    assert all(row["is_anomaly"] in (0, 1) for row in rows)
    assert all(row["explanation"] for row in rows)