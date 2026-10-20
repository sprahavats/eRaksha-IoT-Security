"""Unsupervised anomaly detection and evaluation for eRaksha."""

import numpy as np
from sklearn.ensemble import IsolationForest

from eraksha.config import RANDOM_STATE
from eraksha.simulator import generate_dataset


FEATURES = ("bytes_sent", "bytes_received", "duration_seconds")


def extract_features(flows: list[dict]) -> np.ndarray:
    """Extract numeric traffic features and reduce scale differences."""

    values = np.array(
        [
            [
                flow["bytes_sent"],
                flow["bytes_received"],
                flow["duration_seconds"],
            ]
            for flow in flows
        ],
        dtype=float,
    )

    if values.ndim != 2 or values.shape[1] != len(FEATURES):
        raise ValueError("Unexpected flow feature dimensions.")

    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Flow features must be finite and non-negative.")

    return np.log1p(values)


class FlowAnomalyDetector:
    """Isolation Forest trained exclusively on normal reference flows."""

    def __init__(self, random_state: int = RANDOM_STATE) -> None:
        self.model = IsolationForest(
            n_estimators=200,
            contamination="auto",
            random_state=random_state,
        )
        self.threshold: float | None = None
        self.is_fitted = False

    def fit(
        self,
        normal_flows: list[dict],
        false_positive_percent: float = 5.0,
    ) -> None:
        """Fit on normal traffic and calibrate a score threshold."""

        if len(normal_flows) < 50:
            raise ValueError("At least 50 normal training flows are required.")

        if not 0 < false_positive_percent < 50:
            raise ValueError("False-positive percentage must be between 0 and 50.")

        X_train = extract_features(normal_flows)
        self.model.fit(X_train)

        # Higher decision_function values indicate more typical observations.
        training_scores = self.model.decision_function(X_train)
        self.threshold = float(
            np.percentile(training_scores, false_positive_percent)
        )
        self.is_fitted = True

    def score(self, flows: list[dict]) -> np.ndarray:
        """Return Isolation Forest decision scores; lower means more unusual."""

        if not self.is_fitted:
            raise RuntimeError("Fit the detector before scoring flows.")

        return self.model.decision_function(extract_features(flows))

    def predict(self, flows: list[dict]) -> np.ndarray:
        """Return 1 for flagged anomalies and 0 otherwise."""

        scores = self.score(flows)
        return (scores < self.threshold).astype(int)


def evaluate() -> None:
    """Evaluate on held-out synthetic flows with known labels."""

    training_data = generate_dataset(
        normal_count=500,
        suspicious_count=30,
        seed=RANDOM_STATE,
    )
    normal_training_data = [
        flow for flow in training_data
        if flow["ground_truth_anomaly"] == 0
    ]

    test_data = generate_dataset(
        normal_count=200,
        suspicious_count=60,
        seed=2026,
    )

    detector = FlowAnomalyDetector()
    detector.fit(normal_training_data)

    y_true = np.array(
        [flow["ground_truth_anomaly"] for flow in test_data],
        dtype=int,
    )
    y_pred = detector.predict(test_data)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    false_positive_rate = fp / (fp + tn) if fp + tn else 0.0

    print("eRaksha Isolation Forest evaluation")
    print("Dataset: held-out synthetic flows")
    print(f"Training samples (normal only): {len(normal_training_data)}")
    print(f"Test samples: {len(test_data)}")
    print(f"Threshold: {detector.threshold:.6f}")
    print()
    print(f"True positives:  {tp}")
    print(f"True negatives:  {tn}")
    print(f"False positives: {fp}")
    print(f"False negatives: {fn}")
    print()
    print(f"Precision:           {precision:.3f}")
    print(f"Recall:              {recall:.3f}")
    print(f"F1 score:            {f1:.3f}")
    print(f"False-positive rate: {false_positive_rate:.3f}")
    print()
    print("Note: These metrics measure synthetic-data performance only.")


if __name__ == "__main__":
    evaluate()