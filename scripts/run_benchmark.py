"""
MySQL vs MongoDB performans testleri.
Kullanim:
  python scripts/run_benchmark.py          # tum testler (1M dahil, uzun surer)
  python scripts/run_benchmark.py --quick  # 10K ve 100K insert, 1M atlanir
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.benchmark import mongo_tests, mysql_tests  # noqa: E402
from src.benchmark.dataset import load_templates  # noqa: E402
from src.config import load_env  # noqa: E402

RESULTS_DIR = ROOT / "results"
INSERT_SIZES_FULL = [10_000, 100_000, 1_000_000]
INSERT_SIZES_QUICK = [10_000, 100_000]
UPDATE_DELETE_ROWS = 10_000


def save_results(rows: list, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "timestamp",
        "test_name",
        "database",
        "operations",
        "duration_sec",
        "throughput_ops_per_sec",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def result_row(r, ts: str) -> dict:
    return {
        "timestamp": ts,
        "test_name": r.test_name,
        "database": r.database,
        "operations": r.operations,
        "duration_sec": round(r.duration_sec, 4),
        "throughput_ops_per_sec": round(r.throughput, 2),
    }


def print_result(r):
    print(
        f"  [{r.database:7}] {r.test_name:18} | "
        f"{r.duration_sec:8.3f}s | {r.throughput:,.0f} op/s"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quick",
        action="store_true",
        help="1M insert atlanir (daha hizli)",
    )
    args = parser.parse_args()

    load_env()
    sizes = INSERT_SIZES_QUICK if args.quick else INSERT_SIZES_FULL
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_file = RESULTS_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print("Sablon veri yukleniyor...")
    templates = load_templates()
    results = []

    print("\n=== INSERT TESTLERI ===")
    for n in sizes:
        print(f"\nInsert {n:,} kayit...")
        for run in (
            mysql_tests.run_insert(templates, n),
            mongo_tests.run_insert(templates, n),
        ):
            print_result(run)
            results.append(result_row(run, ts))

    print("\n=== SELECT TESTLERI ===")
    for run in (
        mysql_tests.run_select_single(),
        mongo_tests.run_select_single(),
        mysql_tests.run_select_range(),
        mongo_tests.run_select_range(),
    ):
        print_result(run)
        results.append(result_row(run, ts))

    print("\n=== UPDATE TESTI ===")
    for run in (
        mysql_tests.run_update_with_templates(templates, UPDATE_DELETE_ROWS),
        mongo_tests.run_update_with_templates(templates, UPDATE_DELETE_ROWS),
    ):
        print_result(run)
        results.append(result_row(run, ts))

    print("\n=== DELETE TESTI ===")
    for run in (
        mysql_tests.run_delete_with_templates(templates, UPDATE_DELETE_ROWS),
        mongo_tests.run_delete_with_templates(templates, UPDATE_DELETE_ROWS),
    ):
        print_result(run)
        results.append(result_row(run, ts))

    print("\n=== KARMASIK SORGU (JOIN / Aggregation) ===")
    for run in (
        mysql_tests.run_complex_join(),
        mongo_tests.run_complex_aggregation(),
    ):
        print_result(run)
        results.append(result_row(run, ts))

    save_results(results, out_file)
    print(f"\nSonuclar kaydedildi: {out_file}")
    print("Grafik icin: python scripts/plot_results.py")


if __name__ == "__main__":
    main()
