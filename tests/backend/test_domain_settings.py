import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('settings',Path(__file__).resolve().parents[2]/'ops/divinemedia/domain_settings.py')
settings=importlib.util.module_from_spec(spec);spec.loader.exec_module(settings)
class DomainSettingsTests(unittest.TestCase):
 def test_empty_streamer_policy_remains_empty(self):
  result=settings.desired_settings({'main':settings.OLD+'Encoder/','encoder':''})
  self.assertEqual(result,{'main':settings.NEW+'Encoder/','encoder':''})
 def test_old_streamer_policy_retains_old_and_adds_new(self):
  before={'main':settings.OLD+'Encoder/','encoder':settings.OLD+'\nhttps://other.example/'}
  after=settings.desired_settings(before)
  self.assertEqual(after['encoder'],before['encoder']+'\n'+settings.NEW)
 def test_existing_new_entry_is_not_duplicated(self):
  before={'main':settings.NEW+'Encoder/','encoder':settings.OLD+'\n'+settings.NEW}
  self.assertEqual(settings.desired_settings(before),before)
 def test_loopback_encoder_moves_to_public_domain(self):
  self.assertEqual(settings.desired_settings({'main':'https://localhost/Encoder/','encoder':''})['main'],settings.NEW+'Encoder/')
 def test_existing_streamer_policies_are_preserved(self):
  self.assertEqual(settings.desired_settings({'main':settings.OLD+'Encoder/','encoder':'https://other.example/'})['encoder'],'https://other.example/\n'+settings.NEW)
 def test_unrelated_encoder_refuses_migration(self):
  with self.assertRaises(RuntimeError):settings.desired_settings({'main':'https://other.example/','encoder':''})
if __name__=='__main__':unittest.main()
