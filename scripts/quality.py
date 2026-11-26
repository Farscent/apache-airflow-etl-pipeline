"""Validate row alignment and load a typed snapshot using Python's standard library."""
import csv
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from itertools import zip_longest
from pathlib import Path


def rows(path, delimiter=','):
    with path.open(newline='', encoding='utf-8') as f:
        yield from csv.reader(f, delimiter=delimiter)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_alignment(work):
    seen = set()
    with (work / 'payment-data.txt').open(encoding='utf-8') as f:
        for i, (a, b, raw, x, y, z) in enumerate(zip_longest(
            rows(work / 'vehicle-data.csv'), rows(work / 'tollplaza-data.tsv', '\t'), f,
            rows(work / 'csv_data.csv'), rows(work / 'tsv_data.csv'),
            rows(work / 'fixed_width_data.csv')), 1):
            require(all(v is not None for v in (a,b,raw,x,y,z)), f'Row {i}: unequal file lengths')
            p = raw.rstrip('\r\n')
            require(len(a)==6 and len(b)==7 and len(p)==67, f'Row {i}: invalid source width')
            require(a[0] not in seen, f'Row {i}: duplicate row ID')
            seen.add(a[0])
            require(a[:5] == b[:5], f'Row {i}: CSV/TSV mismatch')
            require([a[0],a[1],a[2],b[5],b[6],a[5]] ==
                    [p[:6].strip(),p[7:31].strip(),p[32:42].strip(),p[43:47].strip(),p[48:58].strip(),p[62:67].strip()],
                    f'Row {i}: fixed-width source mismatch')
            require(x==a[:4] and y==b[4:7] and z==[p[58:61],p[62:67]], f'Row {i}: extraction mismatch')
    require(bool(seen), 'Empty input')
    print(f'Alignment verified: {len(seen):,} rows')


def validated_records(work):
    seen = set()
    counts = Counter()
    for i, (raw, out, x, y, z) in enumerate(zip_longest(
            rows(work/'extracted_data.csv'), rows(work/'transformed_data.csv'),
            rows(work/'csv_data.csv'), rows(work/'tsv_data.csv'),
            rows(work/'fixed_width_data.csv')), 1):
        require(all(v is not None for v in (raw,out,x,y,z)), f'Row {i}: output length mismatch')
        require(raw == x + y + z, f'Row {i}: consolidation mismatch')
        require(len(raw)==len(out)==9 and all(v.strip() for v in out), f'Row {i}: invalid schema or empty field')
        expected = raw.copy()
        expected[3] = expected[3].upper()
        require(out == expected, f'Row {i}: unexpected transformation')
        rid, ts, vehicle, kind, axles, plaza, plaza_code, payment, vehicle_code = out
        key = int(rid)
        require(key > 0 and key not in seen, f'Row {i}: invalid/duplicate row ID')
        require(kind in {'CAR','TRUCK','VAN'}, f'Row {i}: unknown vehicle type')
        require(int(axles)>0 and int(plaza)>0, f'Row {i}: invalid axle/plaza value')
        seen.add(key)
        counts[kind] += 1
        yield (key, datetime.strptime(ts, '%a %b %d %H:%M:%S %Y').isoformat(sep=' '),
               vehicle, kind, int(axles), int(plaza), plaza_code, payment, vehicle_code)
    require(bool(seen), 'Empty output')
    print(f'Validated {len(seen):,} output rows; vehicle types: {dict(counts)}')


def load(work, db_path):
    records = list(validated_records(work))
    with sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS toll_transactions (
            row_id INTEGER PRIMARY KEY, event_timestamp TEXT NOT NULL,
            vehicle_number TEXT NOT NULL, vehicle_type TEXT NOT NULL,
            axle_count INTEGER NOT NULL CHECK(axle_count > 0),
            tollplaza_id INTEGER NOT NULL, tollplaza_code TEXT NOT NULL,
            payment_code TEXT NOT NULL, vehicle_code TEXT NOT NULL)''')
        # Replace the snapshot atomically; retries do not append duplicates.
        conn.execute('DELETE FROM toll_transactions')
        conn.executemany('INSERT INTO toll_transactions VALUES (?,?,?,?,?,?,?,?,?)', records)
        count = conn.execute('SELECT COUNT(*) FROM toll_transactions').fetchone()[0]
        require(count == len(records), 'Database row count mismatch')
    print(f'Loaded {count:,} records into {db_path}')


if __name__ == '__main__':
    action, work = sys.argv[1:3]
    work = Path(work)
    if action == 'alignment':
        validate_alignment(work)
    elif action == 'output':
        for _ in validated_records(work):
            pass
    elif action == 'load':
        load(work, Path(sys.argv[3]))
    else:
        raise SystemExit(f'Unknown action: {action}')
