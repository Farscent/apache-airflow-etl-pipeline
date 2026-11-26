#!/usr/bin/env bash
set -euo pipefail
step=${1:?provide a step}
root=${TOLL_DATA_DIR:?set TOLL_DATA_DIR to an absolute data directory}
scripts=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
work="$root/staging"
mkdir -p "$work" "$root/output"
case "$step" in
  unzip_data)
    # Keep extraction timestamps: Windows-mounted WSL drives may reject utime.
    tar -xmzf "$root/raw/tolldata.tgz" -C "$work" vehicle-data.csv tollplaza-data.tsv payment-data.txt ;;
  extract_data_from_csv)
    cut -d ',' -f1-4 "$work/vehicle-data.csv" > "$work/csv_data.csv" ;;
  extract_data_from_tsv)
    cut -f5-7 "$work/tollplaza-data.tsv" | tr '\t' ',' | tr -d '\r' > "$work/tsv_data.csv" ;;
  extract_data_from_fixed_width)
    cut -c59-67 "$work/payment-data.txt" | tr ' ' ',' | tr -d '\r' > "$work/fixed_width_data.csv" ;;
  validate_alignment)
    python3 "$scripts/quality.py" alignment "$work" ;;
  consolidate_data)
    paste -d ',' "$work/csv_data.csv" "$work/tsv_data.csv" "$work/fixed_width_data.csv" > "$work/extracted_data.csv" ;;
  transform_data)
    awk -F',' 'BEGIN {OFS=","} {$4=toupper($4); print}' "$work/extracted_data.csv" > "$work/transformed_data.csv" ;;
  validate_output)
    python3 "$scripts/quality.py" output "$work" ;;
  load_to_sqlite)
    python3 "$scripts/quality.py" load "$work" "$root/output/toll.db" ;;
  *) echo "Unknown step: $step" >&2; exit 2 ;;
esac
