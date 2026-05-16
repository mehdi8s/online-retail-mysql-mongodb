from pathlib import Path

from ..config import ROOT
from ..db import mysql_connect
from .dataset import expand_rows
from .timer import TimedResult, measure

BATCH = 5000
INSERT_SQL = """
    INSERT INTO bench_lines
    (invoice_no, stock_code, quantity, invoice_date, unit_price, customer_id, country)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


def setup_bench_table():
    conn = mysql_connect()
    cur = conn.cursor()
    schema = (ROOT / "sql" / "benchmark_schema.sql").read_text(encoding="utf-8")
    for stmt in schema.split(";"):
        sql = stmt.strip()
        if sql:
            cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def _insert_rows(rows: list[dict]):
    conn = mysql_connect()
    cur = conn.cursor()
    tuples = [
        (
            r["invoice_no"],
            r["stock_code"],
            r["quantity"],
            r["invoice_date"],
            r["unit_price"],
            r["customer_id"],
            r["country"],
        )
        for r in rows
    ]
    for i in range(0, len(tuples), BATCH):
        cur.executemany(INSERT_SQL, tuples[i : i + BATCH])
    conn.commit()
    cur.close()
    conn.close()


def run_insert(templates: list[dict], count: int) -> TimedResult:
    setup_bench_table()
    rows = expand_rows(templates, count)
    return measure(f"insert_{count}", "MySQL", count, lambda: _insert_rows(rows))


def run_select_single() -> TimedResult:
    conn = mysql_connect()
    cur = conn.cursor()

    def _run():
        cur.execute(
            "SELECT * FROM invoice_lines WHERE invoice_no = %s LIMIT 1",
            ("536365",),
        )
        cur.fetchall()

    result = measure("select_single", "MySQL", 1, _run)
    cur.close()
    conn.close()
    return result


def run_select_range() -> TimedResult:
    conn = mysql_connect()
    cur = conn.cursor()

    def _run():
        cur.execute(
            """
            SELECT id, invoice_no, unit_price, quantity
            FROM invoice_lines
            WHERE unit_price BETWEEN %s AND %s
              AND invoice_date BETWEEN %s AND %s
            """,
            (3.0, 15.0, "2011-01-01", "2011-06-30"),
        )
        cur.fetchall()

    rows = measure("select_range", "MySQL", 1, _run)
    cur.close()
    conn.close()
    return rows


def run_update_with_templates(templates: list[dict], count: int = 10000) -> TimedResult:
    setup_bench_table()
    _insert_rows(expand_rows(templates, count))
    conn = mysql_connect()
    cur = conn.cursor()

    def _run():
        cur.execute(
            """
            UPDATE bench_lines
            SET quantity = quantity + 1
            WHERE unit_price BETWEEN %s AND %s
            """,
            (2.0, 10.0),
        )
        conn.commit()

    result = measure("update", "MySQL", count, _run)
    cur.close()
    conn.close()
    return result


def run_delete_with_templates(templates: list[dict], count: int = 10000) -> TimedResult:
    setup_bench_table()
    _insert_rows(expand_rows(templates, count))
    conn = mysql_connect()
    cur = conn.cursor()

    def _run():
        cur.execute("DELETE FROM bench_lines WHERE customer_id = %s", (17850,))
        conn.commit()

    result = measure("delete", "MySQL", count, _run)
    cur.close()
    conn.close()
    return result


def run_complex_join() -> TimedResult:
    conn = mysql_connect()
    cur = conn.cursor()

    def _run():
        cur.execute(
            """
            SELECT c.country, p.description,
                   SUM(l.quantity * l.unit_price) AS revenue
            FROM invoice_lines l
            INNER JOIN customers c ON l.customer_id = c.customer_id
            INNER JOIN products p ON l.stock_code = p.stock_code
            WHERE l.invoice_date BETWEEN %s AND %s
            GROUP BY c.country, p.description
            HAVING revenue > 500
            ORDER BY revenue DESC
            LIMIT 100
            """,
            ("2011-01-01", "2011-06-30"),
        )
        cur.fetchall()

    result = measure("complex_join", "MySQL", 1, _run)
    cur.close()
    conn.close()
    return result
