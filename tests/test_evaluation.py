
from eraksha.evaluation import evaluate_detector


def test_evaluation_returns_valid_metrics():
    metrics = evaluate_detector()

    assert metrics["training_samples"] == 500
    assert metrics["test_samples"] == 260

    assert (
        metrics["true_positives"]
        + metrics["false_negatives"]
        == 60
    )
    assert (
        metrics["true_negatives"]
        + metrics["false_positives"]
        == 200
    )

    for key in (
        "precision",
        "recall",
        "f1_score",
        "false_positive_rate",
    ):
        assert 0.0 <= metrics[key] <= 1.0
