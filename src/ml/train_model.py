import argparse
import json

from src.ml.service import train_service


def train(task_name: str) -> dict:
    return train_service(task_name)


def main():
    parser = argparse.ArgumentParser(description="Train a baseline ML model from marts.")
    parser.add_argument(
        "--task",
        default="product_bestseller",
        help="Task name. Examples: product_bestseller, order_success, geo_high_demand",
    )
    args = parser.parse_args()

    result = train(args.task)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
