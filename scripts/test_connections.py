"""MySQL ve MongoDB baglanti testi."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "config" / "database.env"


def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def test_mysql():
    import mysql.connector

    conn = mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )
    cur = conn.cursor()
    cur.execute("SELECT VERSION(), DATABASE()")
    version, db = cur.fetchone()
    cur.close()
    conn.close()
    return f"MySQL OK | {version} | db={db}"


def test_mongodb():
    from pymongo import MongoClient

    client = MongoClient(os.environ["MONGODB_URI"], serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[os.environ["MONGODB_DATABASE"]]
    db.list_collection_names()
    client.close()
    return f"MongoDB OK | db={os.environ['MONGODB_DATABASE']}"


def main():
    load_env()
    results = []
    for name, fn in [("MySQL", test_mysql), ("MongoDB", test_mongodb)]:
        try:
            results.append(fn())
        except Exception as exc:
            results.append(f"{name} HATA: {exc}")
            print(results[-1], file=sys.stderr)

    for line in results:
        print(line)

    if any("HATA" in r for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
