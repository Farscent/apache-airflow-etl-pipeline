"""Generate a small, synthetic archive; no IBM source records are distributed."""
import io
import os
import tarfile
from pathlib import Path

root = Path(os.environ.get('TOLL_DATA_DIR', Path(__file__).resolve().parents[1] / 'data'))
target = root / 'raw' / 'tolldata.tgz'
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    raise SystemExit(f'Refusing to overwrite {target}')
files = {name: [] for name in ('vehicle-data.csv', 'tollplaza-data.tsv', 'payment-data.txt')}
for i, (kind, axles) in enumerate([('car', 2), ('truck', 4), ('van', 2)], 1):
    ts = f'Mon Jan  5 12:00:0{i} 2026'
    vehicle, plaza, code, pay, vc = f'90000{i}', f'600{i}', f'PX000000{i}', 'PTE', f'VX00{i}'
    common = [str(i), ts, vehicle, kind, str(axles)]
    files['vehicle-data.csv'].append(','.join(common + [vc]))
    files['tollplaza-data.tsv'].append('\t'.join(common + [plaza, code]))
    files['payment-data.txt'].append(f'{i:>6} {ts:24} {vehicle:10} {plaza:4} {code:9} {pay:3} {vc:5}')
with tarfile.open(target, 'w:gz') as archive:
    for name, lines in files.items():
        b = ('\n'.join(lines)+'\n').encode()
        info = tarfile.TarInfo(name)
        info.size = len(b)
        archive.addfile(info, io.BytesIO(b))
print(f'Created synthetic archive: {target}')
