from src.rag.evaluation import (
    precision_recall_f1,
    retrieval_metrics,
    roc_curve_points,
)


def test_precision_recall_f1_for_retrieved_ids():
    metrics = precision_recall_f1(
        retrieved_ids=["quickstart", "advanced", "api"],
        relevant_ids={"quickstart", "api", "auth"},
    )

    assert metrics["precision"] == 2 / 3
    assert metrics["recall"] == 2 / 3
    assert metrics["f1"] == 2 / 3


def test_retrieval_metrics_averages_multiple_queries():
    results = retrieval_metrics(
        [
            {
                "question": "How do I set a timeout?",
                "retrieved_ids": ["quickstart", "advanced"],
                "relevant_ids": {"quickstart"},
            },
            {
                "question": "How do sessions work?",
                "retrieved_ids": ["advanced"],
                "relevant_ids": {"advanced", "api"},
            },
        ]
    )

    assert results["macro_precision"] == 0.75
    assert results["macro_recall"] == 0.75
    assert round(results["macro_f1"], 4) == 0.6667


def test_roc_curve_points_orders_thresholds_by_score():
    points = roc_curve_points(
        [
            {"score": 0.95, "relevant": True},
            {"score": 0.80, "relevant": False},
            {"score": 0.70, "relevant": True},
            {"score": 0.20, "relevant": False},
        ]
    )

    assert points[0] == {"threshold": float("inf"), "tpr": 0.0, "fpr": 0.0}
    assert points[-1] == {"threshold": 0.2, "tpr": 1.0, "fpr": 1.0}
    assert any(point["threshold"] == 0.7 and point["tpr"] == 1.0 for point in points)
