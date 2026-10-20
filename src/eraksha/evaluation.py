
"""Repeatable evaluation of eRaksha's synthetic-flow detector."""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from eraksha.config import RANDOM_STATE
from eraksha.detector import FlowAnomalyDetector
from eraksha.simulator import generate_dataset


def evaluate_detector() -> dict:
    """Train on normal synthetic traffic and evaluate held-out flows."""

    training_data = generate_dataset(
        normal_count=500,
        suspicious_count=30,
        seed=RANDOM_STATE,
    )
    normal_training = [
        flow for flow in training_data
        if flow["ground_truth_anomaly"] == 0
    ]

    test_data = generate_dataset(
        normal_count=200,
        suspicious_count=60,
        seed=2026,
    )

    y_true = np.array(
        [flow["ground_truth_anomaly"] for flow in test_data],
        dtype=int,
    )

    detector = FlowAnomalyDetector()
    detector.fit(normal_training)
    y_pred = detector.predict(test_data)

    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1]
    ).ravel()

    return {
        "dataset": "held-out synthetic flows",
        "training_samples": len(normal_training),
        "test_samples": len(test_data),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "precision": float(precision_score(
            y_true, y_pred, zero_division=0
        )),
        "recall": float(recall_score(
            y_true, y_pred, zero_division=0
        )),
        "f1_score": float(f1_score(
            y_true, y_pred, zero_division=0
        )),
        "false_positive_rate": float(
            fp / (fp + tn) if fp + tn else 0.0
        ),
        "threshold": float(detector.threshold),
    }


def main() -> None:
    metrics = evaluate_detector()

    print("eRaksha evaluation")
    print(f"Dataset: {metrics['dataset']}")
    print(f"Training samples: {metrics['training_samples']}")
    print(f"Test samples: {metrics['test_samples']}")
    print(
        "Confusion matrix counts: "
        f"TP={metrics['true_positives']}, "
        f"TN={metrics['true_negatives']}, "
        f"FP={metrics['false_positives']}, "
        f"FN={metrics['false_negatives']}"
    )
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"F1 score: {metrics['f1_score']:.3f}")
    print(
        "False-positive rate: "
        f"{metrics['false_positive_rate']:.3f}"
    )
    print("Important: results apply to synthetic data only.")


if __name__ == "__main__":
    main()
