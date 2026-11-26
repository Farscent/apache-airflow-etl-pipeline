import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.env = dict(os.environ, TOLL_DATA_DIR=str(self.data))
        self.run_command('python3', 'scripts/make_sample.py')

    def tearDown(self):
        self.tmp.cleanup()

    def run_command(self, *args, check=True):
        return subprocess.run(args, cwd=ROOT, env=self.env, check=check, capture_output=True, text=True)

    def test_end_to_end_and_retry(self):
        for _ in range(2):
            self.run_command('bash', 'scripts/run_local.sh')
        with sqlite3.connect(self.data/'output/toll.db') as db:
            self.assertEqual(db.execute('SELECT row_id, vehicle_type FROM toll_transactions ORDER BY row_id').fetchall(), [(1,'CAR'),(2,'TRUCK'),(3,'VAN')])

    def test_misaligned_source_rejected(self):
        self.run_command('bash', 'scripts/run_local.sh')
        tsv = self.data/'staging/tollplaza-data.tsv'
        lines = tsv.read_text().splitlines()
        tsv.write_text('\n'.join(reversed(lines))+'\n')
        result = self.run_command('bash','scripts/etl.sh','validate_alignment',check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('mismatch',result.stderr)

    def test_invalid_output_rejected(self):
        self.run_command('bash','scripts/run_local.sh')
        out = self.data/'staging/transformed_data.csv'
        out.write_text(out.read_text().replace(',CAR,',',car,',1))
        result = self.run_command('bash','scripts/etl.sh','validate_output',check=False)
        self.assertNotEqual(result.returncode,0)

if __name__ == '__main__':
    unittest.main()
