#!/usr/bin/env python3
"""Lease-checked presentation-only native skin update; never run Encoder or native startup."""
import argparse,base64,hashlib,importlib.util,json,os,pathlib,stat,subprocess,tarfile,tempfile,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';VERSION='34-glass-1'
NAMES=('divine-shell/head.php','divine-shell/shell.css','divine-shell/shell.js','divine-shell/mark.svg','divine-entrance/entrance.css','divine-entrance/login-theme.php','divine-entrance/login-theme.js','divine-entrance/mark.svg','divine-entrance/landing.php','divine-creator/creator.css','divine-creator/creator.js','divine-creator/theme.php','divine-creator/mark.svg')
PROTECTED=('.htaccess','view/include/head.php','.compose/encoder/view/index.header.php','.compose/encoder/view/localEncoder.php','objects/user.php','objects/login.json.php','view/mini-upload-form/index.php','view/mini-upload-form/upload.php','.compose/encoder/objects/Encoder.php','.compose/encoder/objects/Login.php','divine-api/index.php','divine-api/native.php','divine-api/read.php','plugin/DivineThumbnails/DivineThumbnails.php')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(*args,data=None):return subprocess.run(args,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=120).stdout
def atomic(path,data):
 meta=path.stat();fd,tmp=tempfile.mkstemp(prefix='.dm-glass-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.chmod(tmp,stat.S_IMODE(meta.st_mode))
  if os.geteuid()==0:os.chown(tmp,meta.st_uid,meta.st_gid)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def changes(root,assets,lease):
 assert set(lease)==set(NAMES),'Unexpected presentation file set'
 assert {n:sha(root/n) for n in NAMES}==lease,'Presentation changed since audit'
 out={n:(assets/n).read_bytes() for n in NAMES}
 # This live installation intentionally omits the optional public-redirect bridge.
 # Preserve its existing routing rather than introduce a dormant source-only hook.
 bridge=b"    $dmFrontendRedirect=dirname(__DIR__).'/divine-api/public-redirect.php';\n    if(is_file($dmFrontendRedirect)){require_once $dmFrontendRedirect;}\n\n"
 original=(root/'divine-shell/head.php').read_bytes()
 if b'$dmFrontendRedirect' not in original:
  out['divine-shell/head.php']=out['divine-shell/head.php'].replace(bridge,b'');assert b'$dmFrontendRedirect' not in out['divine-shell/head.php']
 # Keep all live head hooks and template behavior; only replace branding literals.
 landing=(root/'divine-entrance/landing.php').read_bytes()
 for old,new in [(b'33-entrance-3',VERSION.encode()),(b'mark.svg"',b'mark.svg?v='+VERSION.encode()+b'"'),(b'content="#09090c"',b'content="#000000"'),(b'A golden spotlight illuminating the Divine Media monogram',b'A cool glass Divine Media monogram')]:landing=landing.replace(old,new)
 out['divine-entrance/landing.php']=landing
 for n in ['divine-entrance/login-theme.js','divine-creator/creator.js']:
  old=(root/n).read_bytes();expected=old.replace(b'mark.svg"',b'mark.svg?v='+VERSION.encode()+b'"').replace(b"mark.svg'",b"mark.svg?v="+VERSION.encode()+b"'")
  assert out[n]==expected,'Creator/login behavior must remain unchanged'
 return out
def sql(container,query):return run('docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names',data=query.encode()).decode().strip()
def snapshot():
 media={}
 for p in (ROOT/'.compose/videos').rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.mp4','.mp3','.jpg','.jpeg','.png','.webp','.gif']:
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(1048576),b''):h.update(b)
   media[str(p.relative_to(ROOT/'.compose/videos'))]=h.hexdigest()
 return {'media':media,'protected':{n:sha(ROOT/n)for n in PROTECTED if(ROOT/n).is_file()},'catalog':sql('app-database-1','SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;'),'queue':sql('app-database_encoder-1','SELECT JSON_ARRAY(id,status,filename) FROM encoder_queue ORDER BY id;'),'uptimes':run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}','app-avideo-1','app-database-1','app-database_encoder-1','app-memcached-1','app-live-1').decode()}
def archive(path,items):
 with tarfile.open(path,'w:gz') as tar:
  for src,name in items:tar.add(src,arcname=name)
def backup_module():
 spec=importlib.util.spec_from_file_location('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def rollback(root,state,after):
 assert {n:sha(root/n)for n in after}==after,'Later changes prevent automatic presentation rollback'
 for n in after:atomic(root/n,(state/'files'/n).read_bytes())
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--rollback');a=p.parse_args();os.umask(0o077);bundle=pathlib.Path(a.bundle)
 if a.rollback:
  state=pathlib.Path(a.rollback);plan=json.loads((state/'after-hashes.json').read_text());rollback(ROOT,state,plan);print(json.dumps({'result':'rolled_back','state':str(state)}));raise SystemExit(0)
 lease=json.loads((bundle/'lease.json').read_text());desired=changes(ROOT,bundle/'assets',lease)
 for n,data in desired.items():
  if n.endswith('.php'):run('docker','exec','-i',WEB,'php','-l',data=data)
 staged={n:hashlib.sha256(b).hexdigest()for n,b in desired.items()}
 if not a.apply:
  (bundle/'stage-hashes.json').write_text(json.dumps(staged));print(json.dumps({'result':'pass','phase':'prepare','files':len(staged),'native_handlers_changed':False,'php_lint':'pass','routing_bridge_preserved':True}));raise SystemExit(0)
 assert staged==json.loads((bundle/'stage-hashes.json').read_text()),'Staged payload changed'
 browser=json.loads((bundle/'browser-stage.json').read_text());assert browser['result']=='pass' and browser['read_only'] and browser['new_assets_used'],'Staged browser checks required'
 state=pathlib.Path('/srv/divinemedia/backups')/('native-glass-'+uuid.uuid4().hex[:12]);state.mkdir(mode=0o700);before=snapshot();backup=backup_module()
 for n in NAMES:dest=state/'files'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
 (state/'before-state.json').write_text(json.dumps(before));archive(state/'before.tar.gz',[(state/'files','files'),(state/'before-state.json','before-state.json')]);proof=backup.off_vm(state/'before.tar.gz',state.name)
 report={'result':'pending','state':str(state),'before_backup':proof};written={}
 try:
  assert {n:sha(ROOT/n)for n in NAMES}==lease,'Presentation changed during backup'
  for n,raw in desired.items():atomic(ROOT/n,raw);written[n]=staged[n]
  (state/'after-hashes.json').write_text(json.dumps(written))
  for path in ['/?theme=code-black','/user?theme=code-black','/Encoder/?theme=code-black','/view/?theme=code-black']:
   body=run('docker','exec',WEB,'curl','-fsS','--max-time','35','--noproxy','media.divinemedia.us','--resolve','media.divinemedia.us:443:127.0.0.1','https://media.divinemedia.us'+path).decode()
   assert VERSION in body and 'Fatal error' not in body,'HTML smoke failed'
  after=snapshot();assert before==after,'Media/catalog/queue/native source or uptime changed concurrently; presentation rollback required'
  archive(state/'after.tar.gz',[(ROOT/n,n)for n in NAMES]+[(state/'after-hashes.json','after-hashes.json')]);after_proof=backup.off_vm(state/'after.tar.gz',state.name)
  report.update({'result':'pass','after_backup':after_proof,'files':list(NAMES),'media_artwork_files_preserved':len(before['media']),'catalog_queue_native_handlers_and_uptimes_unchanged':True,'database_or_plugin_settings_written':False,'jobs_or_native_startup_invoked':False,'routing_bridge_preserved':True,'after_hashes':written})
 except Exception as e:
  if written:rollback(ROOT,state,written)
  report.update({'result':'fail','rolled_back':bool(written),'error_type':type(e).__name__,'assertion':str(e)[:160]if isinstance(e,AssertionError)else None})
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass'else 1)
