import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('import_hold', ROOT/'ops/divinemedia/import_draft_hold.py')
hold = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hold)

class ImportHoldTests(unittest.TestCase):
    def test_model_contract_and_idempotency(self):
        originals = [(ROOT/'objects/video.php').read_text(), '<?php class Video { public function setStatus($status, $ignoreGroups=false): bool { return true; }}']
        for original in originals:
            patched = hold.patch(original)
            self.assertEqual(patched.count('DM_IMPORT_DRAFT_HOLD'), 1)
            self.assertIn('DivineImportHold::status($this, $status)', patched)
            self.assertEqual(hold.patch(patched), patched)
    def test_unknown_native_contract_rejected(self):
        with self.assertRaises(ValueError):
            hold.patch('<?php echo "different receiver";')

if __name__ == '__main__':
    unittest.main()
