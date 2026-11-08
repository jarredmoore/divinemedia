import importlib.util,os,pathlib,stat,tempfile,unittest
spec=importlib.util.spec_from_file_location('installer',pathlib.Path(__file__).with_name('apply-entrance.py'))
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
ASSETS=pathlib.Path(__file__).resolve().parents[2]/'backend/divine-entrance'
class InstallerChecks(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)/'avideo';(self.root/'view').mkdir(parents=True)
  self.originals={'.htaccess':b'RewriteEngine On\nRewriteRule ^user$ view/user.php [L]\n','view/userLogin.php':b'<form id="loginForm"><input id="inputUser"></form>\n'}
  for name,data in self.originals.items():(self.root/name).write_bytes(data)
  self.backups=pathlib.Path(self.temp.name)/'backups'
 def tearDown(self):self.temp.cleanup()
 def test_private_umask_keeps_public_assets_readable_and_rolls_back_exactly(self):
  previous=os.umask(0o077)
  try:plan=installer.install(self.root,ASSETS,self.backups,apply=True)
  finally:os.umask(previous)
  self.assertEqual(stat.S_IMODE((self.root/'divine-entrance').stat().st_mode),0o755)
  self.assertEqual(stat.S_IMODE(pathlib.Path(plan['rollback_snapshot']).stat().st_mode),0o700)
  for file in (self.root/'divine-entrance').iterdir():self.assertEqual(stat.S_IMODE(file.stat().st_mode),0o644)
  installer.rollback(self.root,plan['rollback_snapshot'])
  for name,data in self.originals.items():self.assertEqual((self.root/name).read_bytes(),data)
  self.assertFalse((self.root/'divine-entrance').exists())
 def test_source_lease_rejects_changed_files_without_writes(self):
  expected={name:installer.digest(data) for name,data in self.originals.items()};expected['.htaccess']='stale'
  with self.assertRaises(RuntimeError):installer.install(self.root,ASSETS,self.backups,expected,True)
  self.assertFalse((self.root/'divine-entrance').exists())
  for name,data in self.originals.items():self.assertEqual((self.root/name).read_bytes(),data)
 def test_rollback_preserves_later_edits(self):
  plan=installer.install(self.root,ASSETS,self.backups,apply=True)
  changed=(self.root/'.htaccess').read_bytes()+b'# Later owner change\n';(self.root/'.htaccess').write_bytes(changed)
  with self.assertRaises(RuntimeError):installer.rollback(self.root,plan['rollback_snapshot'])
  self.assertEqual((self.root/'.htaccess').read_bytes(),changed)
  self.assertTrue((self.root/'divine-entrance').exists())
if __name__=='__main__':unittest.main()
