from datetime import datetime

from ..db import mongo_client
from .dataset import expand_rows
from .timer import TimedResult, measure

BATCH = 5000
BENCH_COLL = "bench_transactions"


def setup_bench_collection(db):
    db[BENCH_COLL].drop()
    db[BENCH_COLL].create_index("invoice_no")
    db[BENCH_COLL].create_index("customer_id")
    db[BENCH_COLL].create_index("invoice_date")
    db[BENCH_COLL].create_index("unit_price")


def _insert_rows(db, rows: list[dict]):
    docs = [{**r} for r in rows]
    for i in range(0, len(docs), BATCH):
        db[BENCH_COLL].insert_many(docs[i : i + BATCH])


def run_insert(templates: list[dict], count: int) -> TimedResult:
    client, db = mongo_client()
    setup_bench_collection(db)
    rows = expand_rows(templates, count)

    def _run():
        _insert_rows(db, rows)

    result = measure(f"insert_{count}", "MongoDB", count, _run)
    client.close()
    return result


def run_select_single() -> TimedResult:
    client, db = mongo_client()

    def _run():
        list(db.transactions.find({"invoice_no": "536365"}).limit(1))

    result = measure("select_single", "MongoDB", 1, _run)
    client.close()
    return result


def run_select_range() -> TimedResult:
    client, db = mongo_client()

    def _run():
        list(
            db.transactions.find(
                {
                    "unit_price": {"$gte": 3.0, "$lte": 15.0},
                    "invoice_date": {
                        "$gte": datetime(2011, 1, 1),
                        "$lte": datetime(2011, 6, 30, 23, 59, 59),
                    },
                }
            )
        )

    result = measure("select_range", "MongoDB", 1, _run)
    client.close()
    return result


def run_update_with_templates(templates: list[dict], count: int = 10000) -> TimedResult:
    client, db = mongo_client()
    setup_bench_collection(db)
    _insert_rows(db, expand_rows(templates, count))

    def _run():
        db[BENCH_COLL].update_many(
            {"unit_price": {"$gte": 2.0, "$lte": 10.0}},
            {"$inc": {"quantity": 1}},
        )

    result = measure("update", "MongoDB", count, _run)
    client.close()
    return result


def run_delete_with_templates(templates: list[dict], count: int = 10000) -> TimedResult:
    client, db = mongo_client()
    setup_bench_collection(db)
    _insert_rows(db, expand_rows(templates, count))

    def _run():
        db[BENCH_COLL].delete_many({"customer_id": 17850})

    result = measure("delete", "MongoDB", count, _run)
    client.close()
    return result


def run_complex_aggregation() -> TimedResult:
    client, db = mongo_client()
    start = datetime(2011, 1, 1)
    end = datetime(2011, 6, 30, 23, 59, 59)

    pipeline = [
        {"$match": {"invoice_date": {"$gte": start, "$lte": end}}},
        {
            "$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "cust",
            }
        },
        {"$unwind": "$cust"},
        {
            "$lookup": {
                "from": "products",
                "localField": "stock_code",
                "foreignField": "_id",
                "as": "prod",
            }
        },
        {"$unwind": "$prod"},
        {
            "$group": {
                "_id": {
                    "country": "$cust.country",
                    "description": "$prod.description",
                },
                "revenue": {"$sum": {"$multiply": ["$quantity", "$unit_price"]}},
            }
        },
        {"$match": {"revenue": {"$gt": 500}}},
        {"$sort": {"revenue": -1}},
        {"$limit": 100},
    ]

    def _run():
        list(db.transactions.aggregate(pipeline, allowDiskUse=True))

    result = measure("complex_join", "MongoDB", 1, _run)
    client.close()
    return result
