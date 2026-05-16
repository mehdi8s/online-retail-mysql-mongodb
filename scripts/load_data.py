"""
Temiz veriyi MySQL ve MongoDB'ye yukler.
Kullanim: python scripts/load_data.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import CSV_CLEAN, DATA_DIR, load_env  # noqa: E402
from src.clean_data import load_and_clean  # noqa: E402

BATCH = 5000


def mysql_connect():
    import mysql.connector

    load_env()
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )


def mongo_db():
    from pymongo import MongoClient

    load_env()
    client = MongoClient(os.environ["MONGODB_URI"])
    return client, client[os.environ["MONGODB_DATABASE"]]


def apply_mysql_schema(conn):
    schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    cur = conn.cursor()
    for stmt in schema.split(";"):
        sql = stmt.strip()
        if sql:
            cur.execute(sql)
    conn.commit()
    cur.close()


def load_mysql(df):
    conn = mysql_connect()
    apply_mysql_schema(conn)
    cur = conn.cursor()

    customers = (
        df.groupby("CustomerID", as_index=False)["Country"]
        .first()
        .rename(columns={"CustomerID": "customer_id", "Country": "country"})
    )
    products = (
        df.groupby("StockCode", as_index=False)["Description"]
        .first()
        .rename(columns={"StockCode": "stock_code", "Description": "description"})
    )

    cur.executemany(
        "INSERT INTO customers (customer_id, country) VALUES (%s, %s)",
        customers.itertuples(index=False, name=None),
    )
    cur.executemany(
        "INSERT INTO products (stock_code, description) VALUES (%s, %s)",
        products.itertuples(index=False, name=None),
    )

    line_rows = [
        (
            row.InvoiceNo,
            row.StockCode,
            int(row.Quantity),
            row.InvoiceDate.to_pydatetime(),
            float(row.UnitPrice),
            int(row.CustomerID),
            row.Country,
        )
        for row in df.itertuples(index=False)
    ]
    sql = """
        INSERT INTO invoice_lines
        (invoice_no, stock_code, quantity, invoice_date, unit_price, customer_id, country)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for i in range(0, len(line_rows), BATCH):
        cur.executemany(sql, line_rows[i : i + BATCH])
        conn.commit()
        print(f"  MySQL satir: {min(i + BATCH, len(line_rows))}/{len(line_rows)}")

    cur.close()
    conn.close()
    return len(customers), len(products), len(line_rows)


def load_mongodb(df):
    client, db = mongo_db()

    for name in ("transactions", "customers", "products"):
        db[name].drop()

    customers = [
        {"_id": int(r.customer_id), "country": r.country}
        for r in df.groupby("CustomerID", as_index=False)["Country"]
        .first()
        .rename(columns={"CustomerID": "customer_id", "Country": "country"})
        .itertuples(index=False)
    ]
    products = [
        {"_id": r.stock_code, "description": r.description}
        for r in df.groupby("StockCode", as_index=False)["Description"]
        .first()
        .rename(columns={"StockCode": "stock_code", "Description": "description"})
        .itertuples(index=False)
    ]
    db.customers.insert_many(customers)
    db.products.insert_many(products)

    docs = [
        {
            "invoice_no": r.InvoiceNo,
            "stock_code": r.StockCode,
            "description": r.Description,
            "quantity": int(r.Quantity),
            "invoice_date": r.InvoiceDate.to_pydatetime(),
            "unit_price": float(r.UnitPrice),
            "customer_id": int(r.CustomerID),
            "country": r.Country,
        }
        for r in df.itertuples(index=False)
    ]
    for i in range(0, len(docs), BATCH):
        db.transactions.insert_many(docs[i : i + BATCH])
        print(f"  MongoDB dokuman: {min(i + BATCH, len(docs))}/{len(docs)}")

    db.transactions.create_index("invoice_no")
    db.transactions.create_index("customer_id")
    db.transactions.create_index("invoice_date")
    db.transactions.create_index("unit_price")

    client.close()
    return len(customers), len(products), len(docs)


def main():
    load_env()
    print("Veri temizleniyor...")
    df = load_and_clean(save_clean_path=CSV_CLEAN)
    print(f"Temiz kayit: {len(df):,} (kaydedildi: {CSV_CLEAN})")

    print("\nMySQL yukleniyor...")
    c, p, lines = load_mysql(df)
    print(f"MySQL tamam: {c} musteri, {p} urun, {lines} satis satiri")

    print("\nMongoDB yukleniyor...")
    c2, p2, docs = load_mongodb(df)
    print(f"MongoDB tamam: {c2} musteri, {p2} urun, {docs} islem")

    print("\nOzet:")
    print(f"  MySQL  -> customers, products, invoice_lines")
    print(f"  MongoDB -> customers, products, transactions")


if __name__ == "__main__":
    main()
