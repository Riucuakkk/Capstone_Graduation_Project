from __future__ import annotations

import argparse
import json

from src.ml.service import predict_service


def predict(
    task_name: str,
    limit: int,
    write_output: bool = False,
    run_id: str | None = None,
    source_run_id: str | None = None,
) -> dict:
    return predict_service(
        task_name,
        limit,
        write_output=write_output,
        run_id=run_id,
        source_run_id=source_run_id,
    )


def main():
    parser = argparse.ArgumentParser(description="Run baseline predictions from marts.")
    parser.add_argument(
        "--task",
        default="product_bestseller",
        help="Task name. Examples: product_bestseller, order_success, geo_high_demand",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Limit rows loaded for scoring preview. Use 0 for all rows.",
    )
    parser.add_argument(
        "--write-output",
        action="store_true",
        help="Write batch prediction output to Postgres schema ml.predictions.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional external prediction run id for orchestration tools such as Airflow.",
    )
    parser.add_argument(
        "--source-run-id",
        default=None,
        help="Optional training run id linked to this prediction batch.",
    )
    args = parser.parse_args()

    result = predict(
        args.task,
        args.limit,
        write_output=args.write_output,
        run_id=args.run_id,
        source_run_id=args.source_run_id,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
