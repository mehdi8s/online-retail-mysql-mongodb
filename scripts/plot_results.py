"""
Benchmark CSV sonuclarindan grafik uretir.
Kullanim: python scripts/plot_results.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"


def latest_csv() -> Path:
    files = sorted(RESULTS_DIR.glob("benchmark_*.csv"))
    if not files:
        raise FileNotFoundError("results/ altinda benchmark CSV yok. Once run_benchmark.py calistirin.")
    return files[-1]


def main():
    path = latest_csv()
    df = pd.read_csv(path)
    print(f"Grafik kaynagi: {path.name}")

    insert_df = df[df["test_name"].str.startswith("insert_")].copy()
    if not insert_df.empty:
        insert_df["size"] = insert_df["test_name"].str.replace("insert_", "", regex=False).astype(int)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        for db, color in [("MySQL", "#00758f"), ("MongoDB", "#4db33d")]:
            sub = insert_df[insert_df["database"] == db]
            axes[0].plot(sub["size"], sub["duration_sec"], marker="o", label=db, color=color)
            axes[1].plot(sub["size"], sub["throughput_ops_per_sec"], marker="o", label=db, color=color)

        axes[0].set_xscale("log")
        axes[0].set_xlabel("Kayit sayisi")
        axes[0].set_ylabel("Sure (sn)")
        axes[0].set_title("Insert - Sure")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].set_xscale("log")
        axes[1].set_xlabel("Kayit sayisi")
        axes[1].set_ylabel("Throughput (islem/sn)")
        axes[1].set_title("Insert - Throughput")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        out = RESULTS_DIR / "chart_insert.png"
        plt.savefig(out, dpi=150)
        print(f"Kaydedildi: {out}")
        plt.close()

    other_tests = ["select_single", "select_range", "update", "delete", "complex_join"]
    plot_df = df[df["test_name"].isin(other_tests)]
    if not plot_df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        x_labels = plot_df["test_name"].unique()
        x_pos = range(len(x_labels))
        width = 0.35

        for i, db in enumerate(["MySQL", "MongoDB"]):
            sub = plot_df[plot_df["database"] == db].set_index("test_name").reindex(x_labels)
            vals = sub["duration_sec"].values
            offset = [-width / 2, width / 2][i]
            ax.bar([p + offset for p in x_pos], vals, width, label=db)

        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(x_labels, rotation=25, ha="right")
        ax.set_ylabel("Sure (sn)")
        ax.set_title("Diger testler - Sure karsilastirmasi")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)
        plt.tight_layout()
        out = RESULTS_DIR / "chart_other.png"
        plt.savefig(out, dpi=150)
        print(f"Kaydedildi: {out}")


if __name__ == "__main__":
    main()
