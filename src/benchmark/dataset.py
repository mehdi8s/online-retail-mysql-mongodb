from pathlib import Path

import pandas as pd

from ..config import CSV_CLEAN, ROOT


def load_templates(max_rows: int = 10000) -> list[dict]:
    path = CSV_CLEAN
    if not path.exists():
        from ..clean_data import load_and_clean

        path = ROOT / "data" / "retail_clean.csv"
        df = load_and_clean(save_clean_path=path)
    else:
        df = pd.read_csv(path, parse_dates=["InvoiceDate"])

    df = df.head(max_rows)
    return [
        {
            "invoice_no": r.InvoiceNo,
            "stock_code": r.StockCode,
            "quantity": int(r.Quantity),
            "invoice_date": r.InvoiceDate.to_pydatetime(),
            "unit_price": float(r.UnitPrice),
            "customer_id": int(r.CustomerID),
            "country": r.Country,
        }
        for r in df.itertuples(index=False)
    ]


def expand_rows(templates: list[dict], count: int) -> list[dict]:
    rows = []
    for i in range(count):
        row = templates[i % len(templates)].copy()
        if i >= len(templates):
            row["invoice_no"] = f"{row['invoice_no']}-B{i}"
        rows.append(row)
    return rows
