"""Narrow player-only plugin proposal; no migrations or media processing."""
import hashlib,pathlib,re
NAMES=('Hotkeys','NextButton','SeekButton','TheaterButton')
def inspect_sources(app):
 result={}
 for name in NAMES:
  path=pathlib.Path(app)/'plugin'/name/(name+'.php');raw=path.read_bytes();text=raw.decode()
  # These utilities must stay free of lifecycle, database and background hooks.
  for hook in ['getStart','updateScript','executeEveryMinute','onNewVideo','onUploadIsDone']:
   if re.search(r'function\s+'+hook+r'\s*\(',text):raise RuntimeError('Unexpected plugin lifecycle hook: '+name)
  def value(method):
   match=re.search(r'function\s+'+method+r'\s*\(\).*?return\s+[\'\"]([^\'\"]+)',text,re.S)
   if not match:raise RuntimeError('Missing plugin metadata: '+name)
   return match.group(1)
  result[name]={'uuid':value('getUUID'),'version':value('getPluginVersion'),'sha256':hashlib.sha256(raw).hexdigest(),'options':'{"hideOnMobile":false}' if name=='SeekButton' else '{}'}
 return result
def sql_literal(value):return "CONVERT(UNHEX('"+value.encode().hex()+"') USING utf8mb4)"
def insert_statement(name,meta):
 values=[meta['uuid'],'active',meta['options'],name,name,meta['version']]
 return 'INSERT INTO plugins (uuid,status,object_data,name,dirName,pluginversion,created,modified) VALUES ('+','.join(sql_literal(v) for v in values)+',NOW(),NOW());'
