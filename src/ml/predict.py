import argparse
import json

from src.ml.service import predict_service


def predict(task_name: str, limit: int) -> dict:
    return predict_service(task_name, limit)


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
    args = parser.parse_args()

    result = predict(args.task, args.limit)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
