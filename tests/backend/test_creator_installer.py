"""Checks reversible source edits and restrictive-umask file permissions."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('creator', Path(__file__).resolve().parents[2] / 'ops/divinemedia/apply-creator.py')
creator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(creator)
ASSETS = Path(__file__).resolve().parents[2] / 'backend/divine-creator'

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'app'
        self.originals = {}
        for name in ['view/mini-upload-form/index.php', '.compose/encoder/view/index.php']:
            path = self.root / name
            path.parent.mkdir(parents=True)
            data = b'<html><body><form method="post"></form></body></html>\n'
            path.write_bytes(data)
            self.originals[name] = data
        self.backups = Path(self.temp.name) / 'snapshots'

    def test_install_and_exact_rollback_with_private_umask(self):
        previous = os.umask(0o077)
        try:
            plan = creator.install(self.root, ASSETS, self.backups, apply=True)
        finally:
            os.umask(previous)
        self.assertEqual((self.root / 'divine-creator').stat().st_mode & 0o777, 0o755)
        self.assertEqual(Path(plan['rollback_snapshot']).stat().st_mode & 0o777, 0o700)
        for asset in (self.root / 'divine-creator').iterdir():
            self.assertEqual(asset.stat().st_mode & 0o777, 0o644)
        for name in self.originals:
            self.assertEqual((self.root / name).read_bytes().count(b'DM_CREATOR_V1'), 1)
        creator.rollback(self.root, plan['rollback_snapshot'])
        for name, data in self.originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        self.assertFalse((self.root / 'divine-creator').exists())

    def test_changed_source_refuses_install(self):
        expected = {name: '0' * 64 for name in self.originals}
        with self.assertRaises(RuntimeError):
            creator.install(self.root, ASSETS, self.backups, expected, True)
        self.assertFalse((self.root / 'divine-creator').exists())

    def test_rollback_refuses_to_destroy_later_edits(self):
        plan = creator.install(self.root, ASSETS, self.backups, apply=True)
        path = self.root / next(iter(self.originals))
        path.write_bytes(path.read_bytes() + b'new work')
        with self.assertRaises(RuntimeError):
            creator.rollback(self.root, plan['rollback_snapshot'])
        self.assertTrue(path.read_bytes().endswith(b'new work'))

if __name__ == '__main__':
    unittest.main()
