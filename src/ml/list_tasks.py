import json

from src.ml.service import task_catalog


def main():
    print(json.dumps(task_catalog(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
