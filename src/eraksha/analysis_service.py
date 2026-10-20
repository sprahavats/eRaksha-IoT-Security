"""Run anomaly detection on flows already stored in SQLite."""

import math

from eraksha.database import get_connection, initialize_database
from eraksha.detector import FlowAnomalyDetector
from eraksha.simulator import generate_dataset


def explain_flow(flow: dict) -> str:
    """Describe unusual observable features without claiming an attack."""

    signals = []

    if flow["bytes_sent"] > 100_000:
        signals.append("unusually high outbound byte count")

    if flow["bytes_received"] > 100_000:
        signals.append("unusually high inbound byte count")

    if 0 < flow["duration_seconds"] < 0.4:
        signals.append("very short flow duration")

    if flow["dst_port"] in {4444, 12345, 31337}:
        signals.append("destination port warrants investigation")

    if not signals:
        return "Flagged by the statistical model; inspect flow context"

    return "; ".join(signals)


def analyze_stored_flows() -> int:
    """Score stored flows and persist predictions and explanations."""

    initialize_database()

    # Build a normal-only reference set for the demonstration model.
    reference = generate_dataset(
        normal_count=500,
        suspicious_count=30,
        seed=42,
    )
    normal_reference = [
        flow for flow in reference
        if flow["ground_truth_anomaly"] == 0
    ]

    detector = FlowAnomalyDetector()
    detector.fit(normal_reference)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, src_ip, dst_ip, src_port, dst_port, protocol,
                   bytes_sent, bytes_received, duration_seconds, source
            FROM flows
            WHERE source = 'simulated'
            ORDER BY id
            """
        ).fetchall()

    if not rows:
        print("No simulated flows found. Run the simulator first.")
        return 0

    flows = [dict(row) for row in rows]
    predictions = detector.predict(flows)
    decision_scores = detector.score(flows)

    with get_connection() as connection:
        for flow, prediction, decision_score in zip(
            flows, predictions, decision_scores
        ):
            # Convert the model's decision score into an anomaly-strength
            # score: higher means more unusual, not a probability of attack.
            anomaly_strength = 1.0 / (
                1.0 + math.exp(max(-60.0, min(60.0, float(decision_score) * 10)))
            )

            explanation = (
                explain_flow(flow)
                if prediction == 1
                else "Not flagged by the current model threshold"
            )

            connection.execute(
                """
                UPDATE flows
                SET anomaly_score = ?,
                    is_anomaly = ?,
                    explanation = ?
                WHERE id = ?
                """,
                (
                    round(anomaly_strength, 4),
                    int(prediction),
                    explanation,
                    flow["id"],
                ),
            )

    flagged = int(predictions.sum())

    print("eRaksha stored-flow analysis")
    print(f"Flows analyzed: {len(flows)}")
    print(f"Flows flagged: {flagged}")
    print(f"Flows not flagged: {len(flows) - flagged}")
    print("Results saved to SQLite.")
    print("Scores indicate anomaly strength, not attack probability.")

    return len(flows)


if __name__ == "__main__":
    analyze_stored_flows()