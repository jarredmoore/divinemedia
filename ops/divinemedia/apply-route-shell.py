#!/usr/bin/env python3
"""Lease-checked HTML presentation hooks; native handlers/configuration are untouched."""
import argparse,datetime,hashlib,json,os,pathlib,shutil,stat,tempfile,uuid
MARKER='DM_ROUTE_SHELL_V1'
FILES=['.htaccess','view/include/head.php','.compose/encoder/view/index.header.php','.compose/encoder/view/localEncoder.php','divine-entrance/landing.php']
ASSETS={'head.php','legacy-entry.php','shell.css','shell.js','mark.svg'}
LEGACY='''# DM_ROUTE_SHELL_V1: canonical browser entries only; keep media/API/POST routes.
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTP_HOST} ^media[.]divinecreativegroup[.]com(?::[0-9]+)?$ [NC]
RewriteCond %{REQUEST_METHOD} ^(GET|HEAD)$
RewriteRule ^(?:index[.]php|view/(?:index[.]php|channels[.]php|user[.]php|userSignUp[.]php|managerVideos[.]php|managerCategories[.]php|myComments[.]php|modeYoutube[.]php)?|user|signUp|channels(?:/[^?]*)?|channel/[^?]*|cat/[^?]*|categories|mvideos|subscribes|myComments|admin/?|live/?|video/[^?]*|audio/[^?]*|Encoder/(?:view/index[.]php|index[.]php)?)?$ divine-shell/legacy-entry.php [END,NC]
</IfModule>

'''
def digest(data):return hashlib.sha256(data).hexdigest()
def atomic(path,data,meta):
 fd,tmp=tempfile.mkstemp(prefix='.dm-routes-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.chmod(tmp,stat.S_IMODE(meta.st_mode))
  if os.geteuid()==0:os.chown(tmp,meta.st_uid,meta.st_gid)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def hook(level):return ("\n<?php /* DM_ROUTE_SHELL_V1 */ if (is_file(dirname(__DIR__, "+str(level)+") . '/divine-shell/head.php')) require_once dirname(__DIR__, "+str(level)+") . '/divine-shell/head.php'; ?>\n").encode()
def install(root,assets,backups,expected=None,apply=False):
 root=pathlib.Path(root).resolve();assets=pathlib.Path(assets).resolve();target=root/'divine-shell'
 if target.exists():raise RuntimeError('Route shell already exists; refusing overwrite')
 if {p.name for p in assets.iterdir() if p.is_file()}!=ASSETS:raise RuntimeError('Unexpected route asset set')
 originals={};changes={};metadata={}
 for name in FILES:
  p=root/name
  if p.is_symlink():raise RuntimeError('Refusing symlink source')
  data=p.read_bytes()
  if MARKER.encode() in data:raise RuntimeError('Already patched source')
  if expected and digest(data)!=expected[name]:raise RuntimeError('Source lease changed: '+name)
  originals[name]=data;metadata[name]=p.stat()
 apache=originals['.htaccess'];needle=b'RewriteCond %{QUERY_STRING} ^$'
 if b'DM_ENTRANCE_INDEX_V1' not in apache[:500] or needle not in apache[:500]:raise RuntimeError('Unexpected entrance contract')
 changes['.htaccess']=LEGACY.encode()+apache.replace(needle,b'RewriteCond %{QUERY_STRING} ^(?:theme=(?:code-black|cold-black|default))?$',1)
 changes['view/include/head.php']=originals['view/include/head.php']+hook(2)
 changes['.compose/encoder/view/index.header.php']=originals['.compose/encoder/view/index.header.php']+hook(2)
 for name,level in [('divine-entrance/landing.php',1),('.compose/encoder/view/localEncoder.php',2)]:
  data=originals[name]
  if data.lower().count(b'</head>')!=1:raise RuntimeError('Unexpected HTML head')
  at=data.lower().index(b'</head>');changes[name]=data[:at]+hook(level)+data[at:]
 plan={'before':{n:digest(b) for n,b in originals.items()},'after':{n:digest(b) for n,b in changes.items()},'assets':{n:digest((assets/n).read_bytes()) for n in sorted(ASSETS)}}
 if not apply:return plan
 snapshot=pathlib.Path(backups)/('routes-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]);snapshot.mkdir(mode=0o700,parents=True,exist_ok=False)
 for name,data in originals.items():
  p=snapshot/name;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o600)
 (snapshot/'plan.json').write_text(json.dumps(plan,indent=2));staging=root/('.divine-shell-'+uuid.uuid4().hex[:8]);staging.mkdir(mode=0o755);staging.chmod(0o755)
 try:
  for name in ASSETS:shutil.copyfile(assets/name,staging/name);(staging/name).chmod(0o644)
  os.replace(staging,target)
  for name,data in changes.items():atomic(root/name,data,metadata[name])
 except Exception:
  for name,data in originals.items():atomic(root/name,data,metadata[name])
  shutil.rmtree(target,ignore_errors=True);shutil.rmtree(staging,ignore_errors=True);raise
 plan['snapshot']=str(snapshot);return plan
def rollback(root,snapshot):
 root=pathlib.Path(root).resolve();snapshot=pathlib.Path(snapshot).resolve();plan=json.loads((snapshot/'plan.json').read_text());target=root/'divine-shell'
 for name,sha in plan['after'].items():
  if digest((root/name).read_bytes())!=sha:raise RuntimeError('Later source edit blocks rollback')
 if {p.name for p in target.iterdir()}!=ASSETS:raise RuntimeError('Unowned assets block rollback')
 for name,sha in plan['assets'].items():
  if digest((target/name).read_bytes())!=sha:raise RuntimeError('Later asset edit blocks rollback')
 for name,sha in plan['before'].items():
  if digest((snapshot/name).read_bytes())!=sha:raise RuntimeError('Snapshot checksum mismatch')
 for name in plan['before']:atomic(root/name,(snapshot/name).read_bytes(),(root/name).stat())
 shutil.rmtree(target);return {'rolled_back':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--assets');p.add_argument('--backups');p.add_argument('--expected');p.add_argument('--apply',action='store_true');p.add_argument('--rollback');a=p.parse_args()
 if a.rollback:r=rollback(a.root,a.rollback)
 else:r=install(a.root,a.assets,a.backups,json.loads(pathlib.Path(a.expected).read_text()) if a.expected else None,a.apply)
 print(json.dumps(r,indent=2))
