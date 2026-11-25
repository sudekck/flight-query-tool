from validator import valid_datetime


def run_query(db: list[dict], query: dict) -> dict:
    invalid = {
        "query": query,
        "error": "INVALID_QUERY",
        "matches": []
    }

    if not isinstance(query, dict):
        return invalid

    string_keys = ["flight_id", "origin", "destination"]
    date_keys = ["departure_datetime", "arrival_datetime"]
    record_keys = string_keys + date_keys + ["price"]

    for key, value in query.items():
        if key in string_keys:
            if not isinstance(value, str):
                return invalid

        elif key in date_keys:
            if not isinstance(value, str) or not valid_datetime(value):
                return invalid

        elif key in ["price", "min_price"]:
            if type(value) not in (int, float):
                return invalid

        elif key == "sort_by":
            if value not in record_keys:
                return invalid

        elif key == "order":
            if value not in ["asc", "desc"] or "sort_by" not in query:
                return invalid

        elif key == "limit":
            if type(value) is not int or value < 0:
                return invalid

        else:
            return invalid

    matches = []

    for flight in db:
        match = True

        for key, value in query.items():
            if key in string_keys and flight[key] != value:
                match = False

            elif key == "departure_datetime" and flight[key] < value:
                match = False

            elif key == "arrival_datetime" and flight[key] > value:
                match = False

            elif key == "price" and flight["price"] > value:
                match = False

            elif key == "min_price" and flight["price"] < value:
                match = False

        if match:
            matches.append(flight)

    if "sort_by" in query:
        matches.sort(
            key=lambda flight: flight[query["sort_by"]],
            reverse=query.get("order") == "desc"
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]