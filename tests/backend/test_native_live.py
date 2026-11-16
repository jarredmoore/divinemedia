import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[2]/'ops/divinemedia/native_live.py'
s=importlib.util.spec_from_file_location('native_live',p);n=importlib.util.module_from_spec(s);s.loader.exec_module(n)
class NativeLiveSafety(unittest.TestCase):
 def test_rejects_existing_schema_and_destructive_sql(self):
  raw='CREATE TABLE IF NOT EXISTS `playlists_schedules` (id INT);'
  self.assertIn('CREATE',n.schema_plan(raw,'PlayLists',[]))
  for bad in [raw+'DROP TABLE videos;',raw+'UPDATE users SET isAdmin=1;',raw.replace('playlists_schedules','videos')]:
   with self.assertRaises(RuntimeError):n.schema_plan(bad,'PlayLists',[])
  with self.assertRaises(RuntimeError):n.schema_plan(raw,'PlayLists',['playlists_schedules'])
 def test_proxy_is_https_only_and_excludes_control_routes(self):
  src=b'<VirtualHost *:80>\n</VirtualHost>\n<VirtualHost *:443>\n</VirtualHost>'
  out=n.proxy_vhost(src).decode();self.assertNotIn('ProxyPass',out.split('<VirtualHost *:443>')[0]);self.assertIn('"/hls/live/" "http://live:8080/live/"',out)
  with self.assertRaises(RuntimeError):n.proxy_vhost(out.encode())
 def test_no_recording_restream_or_playlist_broadcast_defaults(self):
  self.assertFalse(n.OPTIONS['Live']['saveLiveIsTheDefault']);self.assertTrue(n.OPTIONS['Live']['disableRestream']);self.assertFalse(n.OPTIONS['Live']['enableRestreamWatchdog']);self.assertFalse(n.OPTIONS['PlayLists']['showPlayLiveButton'])
if __name__=='__main__':unittest.main()
