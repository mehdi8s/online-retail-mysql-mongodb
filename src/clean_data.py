"""Online Retail veri seti temizleme kurallari."""
import pandas as pd

from .config import CSV_RAW


def clean_retail(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = out.columns.str.strip()

    out["InvoiceNo"] = out["InvoiceNo"].astype(str).str.strip()
    out["StockCode"] = out["StockCode"].astype(str).str.strip()
    out["Description"] = out["Description"].astype(str).str.strip()
    out["Country"] = out["Country"].astype(str).str.strip()

    out = out.dropna(subset=["CustomerID"])
    out = out[~out["InvoiceNo"].str.startswith("C")]
    out = out[(out["Quantity"] > 0) & (out["UnitPrice"] > 0)]
    out = out[out["Description"].str.len() > 0]

    out["CustomerID"] = out["CustomerID"].astype(int)
    out["Quantity"] = out["Quantity"].astype(int)
    out["UnitPrice"] = out["UnitPrice"].astype(float)
    out["InvoiceDate"] = pd.to_datetime(out["InvoiceDate"], dayfirst=True, format="mixed")

    return out.reset_index(drop=True)


def load_and_clean(save_clean_path=None) -> pd.DataFrame:
    df = pd.read_csv(CSV_RAW, encoding="utf-8-sig")
    cleaned = clean_retail(df)
    if save_clean_path:
        save_clean_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(save_clean_path, index=False)
    return cleaned
