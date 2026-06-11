from __future__ import annotations

from statistics import mean
from typing import Iterable


def precision_recall_f1(
    *,
    retrieved_ids: list[str],
    relevant_ids: set[str],
) -> dict[str, float]:
    retrieved = set(retrieved_ids)
    true_positives = len(retrieved & relevant_ids)
    precision = true_positives / len(retrieved_ids) if retrieved_ids else 0.0
    recall = true_positives / len(relevant_ids) if relevant_ids else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {"precision": precision, "recall": recall, "f1": f1}


def retrieval_metrics(cases: Iterable[dict]) -> dict[str, float]:
    per_case = [
        precision_recall_f1(
            retrieved_ids=list(case["retrieved_ids"]),
            relevant_ids=set(case["relevant_ids"]),
        )
        for case in cases
    ]
    if not per_case:
        return {"macro_precision": 0.0, "macro_recall": 0.0, "macro_f1": 0.0}
    return {
        "macro_precision": mean(item["precision"] for item in per_case),
        "macro_recall": mean(item["recall"] for item in per_case),
        "macro_f1": mean(item["f1"] for item in per_case),
    }


def roc_curve_points(scored_results: list[dict]) -> list[dict[str, float]]:
    """Build ROC points from retrieval scores and boolean relevance labels."""
    if not scored_results:
        return [{"threshold": float("inf"), "tpr": 0.0, "fpr": 0.0}]

    positives = sum(1 for item in scored_results if item["relevant"])
    negatives = len(scored_results) - positives
    sorted_results = sorted(scored_results, key=lambda item: item["score"], reverse=True)

    points = [{"threshold": float("inf"), "tpr": 0.0, "fpr": 0.0}]
    thresholds = sorted({item["score"] for item in sorted_results}, reverse=True)
    for threshold in thresholds:
        predicted_positive = [item for item in sorted_results if item["score"] >= threshold]
        true_positives = sum(1 for item in predicted_positive if item["relevant"])
        false_positives = len(predicted_positive) - true_positives
        tpr = true_positives / positives if positives else 0.0
        fpr = false_positives / negatives if negatives else 0.0
        points.append({"threshold": threshold, "tpr": tpr, "fpr": fpr})
    return points
