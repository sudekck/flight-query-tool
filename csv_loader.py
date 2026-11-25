import csv
import os
from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen = set()

    for path in paths:
        with open(path, encoding="utf-8", newline="") as file:
            for number, line in enumerate(file, start=1):

                if number == 1:
                    continue

                if not line.strip():
                    continue

                if line.strip().startswith("#"):
                    continue

                fields = next(csv.reader([line]))
                error = validate_row(fields, airports)

                if error is None:
                    record = to_record(fields)

                    key = (
                        record["flight_id"],
                        record["departure_datetime"]
                    )

                    if key in seen:
                        error = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(record)

                if error is not None:
                    filename = os.path.basename(path)

                    errors.append(
                        f"{filename}:{number}: {error} | {line.strip()}"
                    )

    return records, errors