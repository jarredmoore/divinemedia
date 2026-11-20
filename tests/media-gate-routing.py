import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'ops/divinemedia/media_gate.py'
s=importlib.util.spec_from_file_location('gate',p);gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate)
class Routing(unittest.TestCase):
 def test_all_live_proxies_removed_and_both_vhosts_guarded(self):
  raw=b'<VirtualHost *:80>\nProxyPass "/hls/live/" "http://live:8080/live/"\nProxyPassReverse "/hls/live/" "http://live:8080/live/"\n</VirtualHost>\n<VirtualHost *:443>\nXSendFile on\n</VirtualHost>\n'
  updated=gate.vhost(raw);self.assertNotIn(b'http://live:8080/live/',updated);self.assertEqual(updated.count(b'|hls/live/.*)$ /divine-delivery/media.php [END]'),2);self.assertEqual(updated.count(b'XSendFilePath /HLS/live/'),2)
  with self.assertRaises(RuntimeError):gate.vhost(updated)
 def test_unexpected_topology_refused(self):
  with self.assertRaises(RuntimeError):gate.vhost(b'<VirtualHost *:443>\n</VirtualHost>')
 def test_root_rule_precedes_native_and_preserves_it(self):
  original=b'# existing private config deny\n';updated=gate.root_rules(original);self.assertTrue(updated.endswith(original));self.assertIn(b'view/(?:xsendfile|hls)',updated)
  with self.assertRaises(RuntimeError):gate.root_rules(updated)
class LiveOrigin(unittest.TestCase):
 def test_raw_locations_closed_without_changing_ingest_or_stats(self):
  original=b'rtmp { server {\n listen 1935;\n application live { on_publish http://avideo/publish; } } } http { server {\n location /live { root /HLS; location ~ \"m3u8$\" { add_header X \"{hello}\"; } # } in a comment\n }\n location /audio { root /HLS; }\n location /stat { rtmp_stat all; } } }'
  updated=gate.nginx_origin(original);self.assertIn(b'on_publish http://avideo/publish;',updated);self.assertIn(b'location /stat',updated);self.assertIn(b'deny play all;',updated);self.assertIn(b'allow play 127.0.0.1;',updated);self.assertEqual(updated.count(b'return 403;'),2);self.assertNotIn(b'root /HLS;',updated)
  with self.assertRaises(RuntimeError):gate.nginx_origin(updated)
 def test_existing_public_play_rules_closed_in_all_three_scopes(self):
  raw=b'rtmp { server {\nlisten 1935;\nallow play all;\napplication live {\nallow play all;\n} application audio {\nallow play all;\n} } } http { server {\nlocation /live {root /HLS;}\nlocation /audio {root /HLS;} } }'
  result=gate.nginx_origin(raw);self.assertEqual(result.count(b'deny play all;'),3);self.assertNotIn(b'allow play all;',result)
 def test_unexpected_nginx_refused(self):
  with self.assertRaises(RuntimeError):gate.nginx_origin(b'http { server { location /live { root /HLS; } } }')
if __name__=='__main__':unittest.main()
