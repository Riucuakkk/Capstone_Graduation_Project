from __future__ import annotations

import argparse
import json

from src.ml.service import train_service


def train(task_name: str, persist_run: bool = False, run_id: str | None = None) -> dict:
    return train_service(task_name, persist_run=persist_run, run_id=run_id)


def main():
    parser = argparse.ArgumentParser(description="Train a baseline ML model from marts.")
    parser.add_argument(
        "--task",
        default="product_bestseller",
        help="Task name. Examples: product_bestseller, order_success, geo_high_demand",
    )
    parser.add_argument(
        "--persist-run",
        action="store_true",
        help="Write training metadata to Postgres schema ml.training_runs.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional external run id for orchestration tools such as Airflow.",
    )
    args = parser.parse_args()

    result = train(args.task, persist_run=args.persist_run, run_id=args.run_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
