import hashlib,importlib.util,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_glass',ROOT/'ops/divinemedia/deploy-native-glass.py');skin=importlib.util.module_from_spec(spec);spec.loader.exec_module(skin)
class NativeGlassTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)/'root';self.assets=pathlib.Path(self.tmp.name)/'assets'
  for name in skin.NAMES:
   for folder in [self.root,self.assets]:p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'old'if folder==self.root else b'new')
  for name in ['divine-entrance/login-theme.js','divine-creator/creator.js']:
   (self.root/name).write_bytes(b"const img='mark.svg'; // preserve listeners");(self.assets/name).write_bytes(b"const img='mark.svg?v=34-glass-1'; // preserve listeners")
  self.bridge=b"    $dmFrontendRedirect=dirname(__DIR__).'/divine-api/public-redirect.php';\n    if(is_file($dmFrontendRedirect)){require_once $dmFrontendRedirect;}\n\n"
  (self.root/'divine-shell/head.php').write_bytes(b'<?php // no redirect bridge\n');(self.assets/'divine-shell/head.php').write_bytes(b'<?php\n'+self.bridge+b'// new styles\n')
  (self.root/'divine-entrance/landing.php').write_bytes(b'<head><!-- native runtime hook --><link href="entrance.css?v=33-entrance-3"><img src="mark.svg"></head>')
  self.lease={n:skin.sha(self.root/n)for n in skin.NAMES}
 def test_preserves_runtime_head_bridge_and_landing_hook(self):
  result=skin.changes(self.root,self.assets,self.lease);self.assertNotIn(b'$dmFrontendRedirect',result['divine-shell/head.php']);self.assertIn(b'<!-- native runtime hook -->',result['divine-entrance/landing.php']);self.assertIn(b'34-glass-1',result['divine-entrance/landing.php']);self.assertEqual(set(result),set(skin.NAMES))
 def test_source_drift_prevents_any_plan(self):
  (self.root/'divine-shell/shell.css').write_bytes(b'concurrent change')
  with self.assertRaises(AssertionError):skin.changes(self.root,self.assets,self.lease)
 def test_rejects_creator_behavior_changes(self):
  (self.assets/'divine-creator/creator.js').write_bytes(b'new submit handler')
  with self.assertRaises(AssertionError):skin.changes(self.root,self.assets,self.lease)
 def test_exact_rollback_and_later_write_guard(self):
  state=pathlib.Path(self.tmp.name)/'backup';original={n:(self.root/n).read_bytes()for n in skin.NAMES};desired=skin.changes(self.root,self.assets,self.lease)
  for n in skin.NAMES:p=state/'files'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(original[n]);skin.atomic(self.root/n,desired[n])
  after={n:skin.sha(self.root/n)for n in skin.NAMES};skin.rollback(self.root,state,after);self.assertEqual({n:(self.root/n).read_bytes()for n in skin.NAMES},original)
  for n in skin.NAMES:skin.atomic(self.root/n,desired[n])
  (self.root/'divine-shell/mark.svg').write_bytes(b'future logo')
  with self.assertRaises(AssertionError):skin.rollback(self.root,state,after)
  self.assertEqual((self.root/'divine-shell/mark.svg').read_bytes(),b'future logo')
