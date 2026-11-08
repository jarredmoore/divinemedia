import importlib.util,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('route_shell',ROOT/'ops/divinemedia/apply-route-shell.py');shell=importlib.util.module_from_spec(spec);spec.loader.exec_module(shell)
class RouteShellTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)/'app';self.root.mkdir();self.assets=ROOT/'backend/divine-shell';self.backups=pathlib.Path(self.tmp.name)/'backups'
  values={'.htaccess':'# DM_ENTRANCE_INDEX_V1\nRewriteCond %{QUERY_STRING} ^$\nRewriteRule ^$ divine-entrance/landing.php [END]\n','view/include/head.php':'<?php echo "native head"; ?>','divine-entrance/landing.php':'<head><title>Divine Media</title></head><body>Original landing</body>','.compose/encoder/view/localEncoder.php':'<head><title>Local Encoder</title></head><body>Original launcher</body>','.compose/encoder/view/index.header.php':'<meta charset="utf-8"><title>Encoder</title>'}
  for n,s in values.items():p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
  self.original={n:(self.root/n).read_bytes() for n in values}
 def test_exact_rollback_and_theme_root_route(self):
  plan=shell.install(self.root,self.assets,self.backups,apply=True);self.assertIn(b'theme=(?:code-black|cold-black|default)',(self.root/'.htaccess').read_bytes());self.assertIn(b'/divine-shell/head.php',(self.root/'view/include/head.php').read_bytes());shell.rollback(self.root,plan['snapshot']);self.assertFalse((self.root/'divine-shell').exists());self.assertEqual(self.original,{n:(self.root/n).read_bytes() for n in self.original})
 def test_changed_source_refuses_install(self):
  plan=shell.install(self.root,self.assets,self.backups);(self.root/'view/include/head.php').write_text('new native source')
  with self.assertRaises(RuntimeError):shell.install(self.root,self.assets,self.backups,plan['before'],True)
  self.assertFalse((self.root/'divine-shell').exists())
 def test_later_asset_changes_block_rollback(self):
  plan=shell.install(self.root,self.assets,self.backups,apply=True);(self.root/'divine-shell/shell.js').write_text('later release')
  with self.assertRaises(RuntimeError):shell.rollback(self.root,plan['snapshot'])
