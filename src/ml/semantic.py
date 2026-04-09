from __future__ import annotations

from typing import Any

import pandas as pd

from src.ml.tasks import TaskConfig


def _score_to_risk_band(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 0.8:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _regression_to_band(task: TaskConfig, value: float | int | None) -> str | None:
    if value is None:
        return None
    numeric_value = float(value)
    if task.name == "delivery_days_regression":
        if numeric_value >= 15:
            return "high"
        if numeric_value >= 7:
            return "medium"
        return "low"
    if task.name == "order_value_regression":
        if numeric_value >= 500:
            return "high"
        if numeric_value >= 150:
            return "medium"
        return "low"
    if task.name == "daily_category_revenue_regression":
        if numeric_value >= 10000:
            return "high"
        if numeric_value >= 3000:
            return "medium"
        return "low"
    return None


def recommend_action(task: TaskConfig, risk_band: str | None) -> str:
    if task.name == "late_delivery":
        actions = {
            "high": "Escalate shipment monitoring and alert the operations team.",
            "medium": "Review seller SLA and track this order more closely.",
            "low": "No action needed beyond normal monitoring.",
        }
    elif task.name == "low_review":
        actions = {
            "high": "Trigger proactive customer care follow-up.",
            "medium": "Review delivery and seller quality signals before delivery completes.",
            "low": "Keep standard service flow.",
        }
    elif task.name == "seller_risk_band":
        actions = {
            "high": "Review seller SLA breaches and prioritize intervention.",
            "medium": "Monitor seller performance trend in the next cycle.",
            "low": "Maintain current seller management cadence.",
        }
    elif task.name == "customer_value_tier":
        actions = {
            "high": "Prioritize retention and premium campaign targeting.",
            "medium": "Use nurture campaigns and watch repeat-purchase behavior.",
            "low": "Use low-cost reactivation and onboarding strategies.",
        }
    else:
        actions = {
            "high": "Flag for business review.",
            "medium": "Monitor with a standard review workflow.",
            "low": "No immediate action required.",
        }
    return actions.get(risk_band or "low", "No immediate action required.")


def make_prediction_output(task: TaskConfig, ids: pd.DataFrame, predictions, scores=None) -> pd.DataFrame:
    output = ids.copy()
    output["prediction"] = predictions

    if task.problem_type == "classification":
        score_series = pd.Series(scores if scores is not None else [None] * len(output))
        output["prediction_score"] = score_series
        output["risk_band"] = output["prediction_score"].apply(_score_to_risk_band)
    else:
        output["prediction_score"] = None
        output["risk_band"] = output["prediction"].apply(lambda value: _regression_to_band(task, value))

    output["prediction_name"] = task.prediction_name
    output["entity_name"] = task.entity_name
    output["business_goal"] = task.business_goal
    output["recommended_action"] = output["risk_band"].apply(lambda band: recommend_action(task, band))
    return output


def summarize_for_genai(task: TaskConfig, output: pd.DataFrame) -> dict[str, Any]:
    preview = output.head(20).to_dict(orient="records")
    band_counts = (
        output["risk_band"].fillna("unknown").value_counts().to_dict()
        if "risk_band" in output.columns
        else {}
    )

    return {
        "task_name": task.name,
        "prediction_name": task.prediction_name,
        "entity_name": task.entity_name,
        "business_goal": task.business_goal,
        "example_questions": list(task.example_questions),
        "risk_band_distribution": band_counts,
        "preview": preview,
    }
