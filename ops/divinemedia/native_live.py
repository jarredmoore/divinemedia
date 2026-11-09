"""Native Live/PlayLists configuration. No media, accounts or Encoder migrations."""
import hashlib, json, pathlib, re
LIVE_TABLES = ('live_transmitions', 'live_transmitions_has_users_groups', 'live_transmitions_history',
               'live_transmition_history_log', 'live_servers', 'live_restreams', 'live_schedule', 'live_restreams_logs')
SCHEMAS = {'Live': LIVE_TABLES, 'PlayLists': ('playlists_schedules',)}
SOURCE_HASHES = {
 'plugin/Live/Live.php': '48a8ae84434a0e61cb0f2ee47ca5324d038d04a1f31f8d557d35b10253ab13fc',
 'plugin/Live/install/install.sql': '2c4ec6e41050f1cc4f67b6208e64139aabc6b341d780f582f60dfc0dc8fedec5',
 'plugin/PlayLists/PlayLists.php': '9456ffc5b3811879653e1c1fee878f43c0811fc8e59e41741224e141b0674192',
 'plugin/PlayLists/install/install.sql': '8b2ec767620923ee8beb56f931f3258f18d4f2d02867beb382700829f0fab8e6',
 'plugin/PlayLists/run.php': '1e76a3452cb01b55b19f265b42629dd6182353c59f62d3d46a95c6a8a94e3c21',
}
OPTIONS = {
 'Live': {'server':'rtmp://media.divinemedia.us/live', 'playerServer':'https://media.divinemedia.us/hls/live',
          'stats':'http://live:8080/stat', 'controlServer':'http://live:8080/', 'disableRestream':True,
          'enableRestreamWatchdog':False, 'saveLiveIsTheDefault':False, 'disableDVR':True,
          'disableGifThumbs':True, 'disableLiveThumbs':True, 'useAadaptiveMode':False,
          'disableMeetCamera':True, 'allowMultipleLivesPerUser':False, 'disable_live_schedule':True,
          'publicListedIsTheDefault':False, 'controllButtonsShowOnlyToAdmin_record_start':True,
          'controllButtonsShowOnlyToAdmin_record_stop':True, 'controllButtonsShowOnlyToAdmin_save_dvr':True},
 'PlayLists': {'name':'Playlist', 'showPlayLiveButton':False, 'showTVFeatures':False,
               'showFeed':False, 'usePlaylistPlayerForSeries':False},
}
PROXY = '''
    # DM_NATIVE_LIVE_HLS_V1: stream files only; no stats or control proxy.
    ProxyPass "/hls/live/" "http://live:8080/live/" connectiontimeout=3 timeout=30
    ProxyPassReverse "/hls/live/" "http://live:8080/live/"
'''
MODULES = '''# DM_NATIVE_LIVE_MODULES_V1
<IfModule !proxy_module>
    LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
</IfModule>
<IfModule !proxy_http_module>
    LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so
</IfModule>
'''
def digest(raw): return hashlib.sha256(raw).hexdigest()
def inspect(root):
 root=pathlib.Path(root)
 actual={name:digest((root/name).read_bytes()) for name in SOURCE_HASHES}
 if actual != SOURCE_HASHES: raise RuntimeError('Installed native source differs from audited source')
 result={}
 for name in SCHEMAS:
  text=(root/'plugin'/name/(name+'.php')).read_text()
  def metadata(method):
   match=re.search(r'function\s+'+method+r'\s*\(\).*?return\s+[\'\"]([^\'\"]+)',text,re.S)
   if not match:raise RuntimeError('Missing native plugin metadata')
   return match.group(1)
  result[name]={'uuid':metadata('getUUID'),'version':metadata('getPluginVersion'),'options':OPTIONS[name]}
 return result

def schema_plan(raw, name, existing):
 """Execute only native CREATEs for wholly absent feature tables, never ALTER core tables."""
 expected=SCHEMAS[name]
 if set(expected)&set(existing):raise RuntimeError('Feature schema already exists; separate upgrade review required')
 text=re.sub(r'--[^\n]*','',raw)
 statements=[s.strip() for s in text.split(';') if s.strip()]
 found=[]
 for statement in statements:
  match=re.match(r'CREATE TABLE IF NOT EXISTS `([a-z_]+)`\s*\(',statement,re.I)
  if match:found.append(match.group(1))
  elif not re.match(r'^SET (?:@OLD_(?:UNIQUE_CHECKS|FOREIGN_KEY_CHECKS|SQL_MODE)=|(?:UNIQUE_CHECKS|FOREIGN_KEY_CHECKS|SQL_MODE)=@OLD_)',statement):
   raise RuntimeError('Unexpected native schema operation')
 if tuple(found)!=expected:raise RuntimeError('Unexpected native feature tables or order')
 return text

def proxy_vhost(raw):
 text=raw.decode()
 if 'DM_NATIVE_LIVE_' in text:raise RuntimeError('Live proxy already installed')
 matches=list(re.finditer(r'<VirtualHost\s+[^>]*:443\s*>',text,re.I))
 if len(matches)!=1:raise RuntimeError('Unexpected HTTPS virtual hosts')
 at=matches[0].end()
 return (MODULES+text[:at]+PROXY+text[at:]).encode()

def literal(text):return "CONVERT(UNHEX('"+text.encode().hex()+"') USING utf8mb4)"
def insert_plugin(name, meta):
 values=[meta['uuid'],'active',json.dumps(meta['options'],sort_keys=True),name,name,meta['version']]
 return 'INSERT INTO plugins (uuid,status,object_data,name,dirName,pluginversion,created,modified) VALUES ('+','.join(literal(v) for v in values)+',NOW(),NOW());'
