"""Daily batch ETL for toll transactions from three file formats."""
import os
import shlex
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get('TOLL_DATA_DIR', PROJECT / 'data')).resolve()
SCRIPT = PROJECT / 'scripts' / 'etl.sh'

with DAG(
    dag_id='ETL_toll_data',
    description='Extract, validate, transform and load toll transactions',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule='@daily',
    catchup=False,
    max_active_runs=1,
    default_args={'owner': 'data-engineering', 'retries': 1,
                  'retry_delay': timedelta(minutes=5)},
    tags=['etl', 'batch', 'data-quality'],
) as dag:
    def task(name):
        return BashOperator(
            task_id=name,
            bash_command=f'bash {shlex.quote(str(SCRIPT))} {name}',
            env={'TOLL_DATA_DIR': str(DATA_DIR)},
            append_env=True,
            do_xcom_push=False,
        )

    unzip_data = task('unzip_data')
    extract_data_from_csv = task('extract_data_from_csv')
    extract_data_from_tsv = task('extract_data_from_tsv')
    extract_data_from_fixed_width = task('extract_data_from_fixed_width')
    validate_alignment = task('validate_alignment')
    consolidate_data = task('consolidate_data')
    transform_data = task('transform_data')
    validate_output = task('validate_output')
    load_to_sqlite = task('load_to_sqlite')

    extracts = [extract_data_from_csv, extract_data_from_tsv, extract_data_from_fixed_width]
    unzip_data >> extracts >> validate_alignment >> consolidate_data >> transform_data >> validate_output >> load_to_sqlite
