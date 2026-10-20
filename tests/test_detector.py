import numpy as np
import pytest

from eraksha.detector import FlowAnomalyDetector, extract_features
from eraksha.simulator import generate_dataset


def test_detector_requires_training_before_prediction():
    detector = FlowAnomalyDetector()
    flows = generate_dataset(10, 5)

    with pytest.raises(RuntimeError):
        detector.predict(flows)


def test_detector_requires_at_least_50_normal_training_flows():
    detector = FlowAnomalyDetector()
    flows = generate_dataset(49, 5)

    normal_flows = [
        flow for flow in flows
        if flow["ground_truth_anomaly"] == 0
    ]

    with pytest.raises(ValueError):
        detector.fit(normal_flows)


def test_detector_identifies_synthetic_anomalies():
    training = generate_dataset(300, 20, seed=42)
    normal_training = [
        flow for flow in training
        if flow["ground_truth_anomaly"] == 0
    ]

    test_flows = generate_dataset(100, 30, seed=2026)
    labels = np.array(
        [flow["ground_truth_anomaly"] for flow in test_flows]
    )

    detector = FlowAnomalyDetector()
    detector.fit(normal_training)
    predictions = detector.predict(test_flows)

    assert len(predictions) == len(test_flows)
    assert set(predictions).issubset({0, 1})

    true_positives = np.sum((labels == 1) & (predictions == 1))
    assert true_positives / np.sum(labels == 1) >= 0.80


def test_detector_is_reproducible():
    training = generate_dataset(200, 20, seed=42)
    normal_training = [
        flow for flow in training
        if flow["ground_truth_anomaly"] == 0
    ]
    test_flows = generate_dataset(50, 15, seed=2026)

    first = FlowAnomalyDetector(random_state=42)
    second = FlowAnomalyDetector(random_state=42)

    first.fit(normal_training)
    second.fit(normal_training)

    np.testing.assert_array_equal(
        first.predict(test_flows),
        second.predict(test_flows),
    )


def test_invalid_features_are_rejected():
    bad_flow = [{
        "bytes_sent": -1,
        "bytes_received": 100,
        "duration_seconds": 1.0,
    }]

    with pytest.raises(ValueError):
        extract_features(bad_flow)