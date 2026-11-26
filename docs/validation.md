# Verification notes

The original uploaded archive contained a six-task Airflow DAG and its source, intermediate and transformed files. The refactored pipeline was executed using the original `tolldata.tgz` in a temporary directory via `scripts/run_local.sh`. The full data is not included in this repository.

Observed results:

- 10,000 input rows in each source; all source fields used for matching aligned.
- 10,000 transformed records, nine fields each, no empty fields or duplicate IDs.
- Transformed CSV exactly matched the original transformed file byte-for-byte.
- SQLite row count and distinct row ID count: 10,000 each; integrity check: `ok`.
- Earliest timestamp: 2021-07-29 11:27:55; latest: 2021-08-22 18:42:11 (source timezone unspecified).
- CAR: 6,438; TRUCK: 2,368; VAN: 1,194.

Automated synthetic checks: end-to-end execution and repeat load, misaligned input rejection, invalid transformation rejection. These verify the shared Bash/Python implementation. The original full-data verification did not include Airflow scheduler execution. GitHub Actions configuration is included but has not run on GitHub.

## Live local Airflow execution

Screenshots supplied from the local Airflow UI document a successful manual run on 2026-11-26 at 08:32:36 UTC using the three-record synthetic dataset:

- [DAG graph](screenshots/airflow-graph.png): all nine tasks, with three extraction branches converging at the alignment check.
- [Grid and run details](screenshots/airflow-grid.png): green task statuses and explicit DAG run status `success`; displayed duration approximately 13 seconds.
- [Loading task logs](screenshots/airflow-load-logs-updated.png): three validated rows (one CAR, one TRUCK, one VAN), three records loaded into `toll.db`, and command return code zero.

This demonstrates local Airflow orchestration of the synthetic dataset. It does not establish scheduler execution on the 10,000-record dataset or production-scale performance. SQL-results screenshots have not been captured. The older `airflow-load-logs.png` shows audit events; the updated screenshot linked above contains the actual processing output.
