#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export TOLL_DATA_DIR="${TOLL_DATA_DIR:-$(dirname "$here")/data}"
for step in unzip_data extract_data_from_csv extract_data_from_tsv extract_data_from_fixed_width validate_alignment consolidate_data transform_data validate_output load_to_sqlite; do
    echo "=== $step ==="
    bash "$here/etl.sh" "$step"
done
