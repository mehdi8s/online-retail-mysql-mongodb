# Online Retail DB Benchmark

Comparative performance analysis of **MySQL** (relational) vs **MongoDB** (document store) on the [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) e-commerce dataset.

## Highlights

- **397K** cleaned transaction records
- Workloads: bulk insert (10K / 100K / 1M), point & range reads, update, delete, JOIN vs aggregation
- Metrics: response time, throughput (ops/sec)
- Reproducible Python benchmark suite with charts

## Stack

- Python 3.12, pandas, mysql-connector-python, pymongo, matplotlib
- MySQL 8.4, MongoDB 7.0

## Quick start

```bash
pip install -r requirements.txt
cp config/database.env.example config/database.env
# Edit database.env with your credentials

python scripts/test_connections.py
python scripts/load_data.py
python scripts/run_benchmark.py
python scripts/plot_results.py
```

## Project structure

```
config/          # DB connection settings
data/            # Cleaned dataset (retail_clean.csv)
scripts/         # Load, benchmark, plots, setup helpers
src/             # Cleaning logic & benchmark modules
sql/             # MySQL schemas
results/         # CSV metrics & charts
rapor/           # Report (PDF/DOCX)
```

## Sample results

| Workload | MySQL | MongoDB |
|----------|-------|---------|
| Insert 1M | ~101s | ~57s |
| Complex query (JOIN / aggregation) | ~3.2s | ~48.5s |

See `results/` for full benchmark output and graphs.

## Dataset

- **Source:** UCI Machine Learning Repository — Online Retail  
- **License:** CC BY 4.0  
- Cleaning: remove missing customers, returns (`InvoiceNo` starting with `C`), non-positive quantity/price

## License

MIT (code). Dataset subject to UCI / original publisher terms.
