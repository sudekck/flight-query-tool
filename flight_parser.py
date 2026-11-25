import argparse
import json
import logging
import os
import sys
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries


STUDENT_ID = "251ADB136"
FIRST_NAME = "Sude"
LAST_NAME = "Kucukoglu"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i")
    source.add_argument("-d")
    source.add_argument("-j")

    parser.add_argument("-a")
    parser.add_argument("-o")
    parser.add_argument("-q")
    parser.add_argument("-r", default=".")

    args = parser.parse_args(argv)

    if (args.i is not None or args.d is not None) and args.a is None:
        parser.error("-a is required")

    if args.j is not None and args.o is not None:
        parser.error("-o cannot be used with -j")

    try:
        if args.j is not None:
            with open(args.j, encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list):
                raise ValueError("Invalid database")

            if not all(isinstance(item, dict) for item in db):
                raise ValueError("Invalid database records")

        else:
            airports = load_airports(args.a)

            if args.i is not None:
                paths = [args.i]
            else:
                paths = [
                    os.path.join(args.d, name)
                    for name in sorted(os.listdir(args.d))
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                ]

                if not paths:
                    raise ValueError("No CSV files found")

            db, errors = parse_files(paths, airports)

            output = args.o if args.o is not None else "db.json"

            with open(output, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

            log_path = os.path.join(
                os.path.dirname(output), "errors.log"
            )

            logger = logging.getLogger("flight_parser")
            logger.setLevel(logging.INFO)

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            try:
                for error in errors:
                    logger.warning(error)
            finally:
                logger.removeHandler(handler)
                handler.close()

        if args.q is not None:
            with open(args.q, encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, (dict, list)):
                raise ValueError("Invalid query file")

            if isinstance(queries, list):
                if not all(isinstance(q, dict) for q in queries):
                    raise ValueError("Invalid query file")

            results = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            path = os.path.join(args.r, filename)

            with open(path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=2)

        return 0

    except (OSError, ValueError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())