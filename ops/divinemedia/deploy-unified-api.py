#!/usr/bin/env python3
"""Install only the verified JSON adapter. Public HTML cutover remains separately disabled."""
import argparse,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,tarfile,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';KEY='/var/www/tmp/divine-frontend-gateway.key'
def run(*args,data=None):
 return subprocess.run(args,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=120).stdout.decode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sql(container,q):
 return run('docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names',data=q.encode()).strip()
def media():
 result={}
 for p in (ROOT/'.compose/videos').rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.mp3','.mp4']:
   h=hashlib.sha256()
   with p.open('rb') as f:
    for block in iter(lambda:f.read(1048576),b''):h.update(block)
   result[str(p.relative_to(ROOT))]=h.hexdigest()
 return result
def state():
 return {'media':media(),
 'videos':sql('app-database-1','SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;'),
 'permissions':sql('app-database-1','SELECT JSON_ARRAY(id,user,isAdmin,canUpload,canStream) FROM users ORDER BY id;'),
 'queue':sql('app-database_encoder-1','SELECT JSON_ARRAY(id,status,filename) FROM encoder_queue ORDER BY id;'),
 'uptimes':run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}',WEB,'app-database-1','app-database_encoder-1','app-memcached-1','app-live-1'),
 'configs':{p:sha(ROOT/p) for p in ['.compose/videos/configuration.php','.compose/encoder/videos/configuration.php','divine-shell/head.php']}}
def call(action,key,method='GET',body=None):
 # Secrets are stdin to curl, never command arguments or output.
 config=['url = "https://media.divinemedia.us/divine-api/index.php?action='+action+'"',
 'resolve = "media.divinemedia.us:443:127.0.0.1"','noproxy = "media.divinemedia.us"',
 'header = '+json.dumps('X-Divine-Gateway-Key: '+key),'header = "X-Divine-Frontend-Origin: https://divinemedia.us"',
 'user-agent = "Mozilla/5.0 DivineMediaReadOnlyVerification"','silent','show-error','max-time = 30',
 'write-out = "\\n%{http_code}"']
 if method=='POST':config+=['request = "POST"','header = "Content-Type: application/json"','data = '+json.dumps(json.dumps({'payload':body or {}}))]
 raw=run('docker','exec','-i',WEB,'curl','--config','-',data=('\n'.join(config)+'\n').encode());text,status=raw.rsplit('\n',1)
 return int(status),json.loads(text)
def archive(path,files):
 with tarfile.open(path,'w:gz') as tar:
  for p,n in files:tar.add(p,arcname=n)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--bundle',required=True);parser.add_argument('--key-file',required=True);parser.add_argument('--apply',action='store_true');args=parser.parse_args();os.umask(0o077)
 bundle=pathlib.Path(args.bundle);stage=json.loads((bundle/'stage-report.json').read_text())
 assert stage['result']=='pass' and all(stage['checks'].values()),'Native rehearsal must pass'
 assert stage['original_restored_media_preserved']>=52 and stage['scratch_containers_removed']
 expected=stage['api_source_hashes'];assert {p.name:sha(p) for p in (bundle/'api').glob('*.php')}==expected,'Staged adapter source changed'
 manifest=bundle/'native-source-hashes.json';assert sha(manifest)==stage['native_source_manifest_sha256']
 native=json.loads(manifest.read_text());assert all(sha(ROOT/n)==h for n,h in native.items()),'Native source changed after rehearsal'
 target=ROOT/'divine-api';assert not target.exists(),'An existing adapter needs an explicit upgrade lease'
 assert run('docker','exec',WEB,'sh','-c','set -eu; test ! -e '+KEY+'; test ! -e /var/www/tmp/divine-frontend-public.enabled; printf clean').strip()=='clean'
 key=pathlib.Path(args.key_file).read_text().strip();assert len(key)==64 and all(c in '0123456789abcdef' for c in key)
 if not args.apply:print(json.dumps({'result':'plan','api_files':sorted(expected),'native_source_files_verified':len(native),'public_html_redirects_enabled':False}));raise SystemExit(0)
 backup_spec=importlib.util.spec_from_file_location('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');backup=importlib.util.module_from_spec(backup_spec);backup_spec.loader.exec_module(backup)
 snapshot=pathlib.Path('/srv/divinemedia/backups')/('unified-api-deploy-'+uuid.uuid4().hex[:12]);snapshot.mkdir(mode=0o700)
 before=state();(snapshot/'before-state.json').write_text(json.dumps(before));archive(snapshot/'before.tar.gz',[(snapshot/'before-state.json','before-state.json')]);before_proof=backup.off_vm(snapshot/'before.tar.gz',snapshot.name)
 report={'result':'pending','state':str(snapshot),'before_backup':before_proof};installed=False;key_written=False
 try:
  temp=ROOT/('.divine-api-'+uuid.uuid4().hex);shutil.copytree(bundle/'api',temp);temp.chmod(0o755)
  for p in temp.glob('*.php'):p.chmod(0o644)
  temp.rename(target);installed=True
  run('docker','exec','-i',WEB,'sh','-c','umask 077; cat > '+KEY+'; chown www-data:www-data '+KEY,data=key.encode());key_written=True
  assert call('session','invalid')[0]==404
  status,data=call('session',key);assert status==200 and data['user'] is None and data.get('csrf')
  assert call('login',key,'POST',{})[0]==403,'Missing CSRF must be refused'
  assert call('catalog',key)[0]==200
  assert state()==before,'Existing application state changed during installation'
  assert all(sha(ROOT/n)==h for n,h in native.items())
  (snapshot/'installed-hashes.json').write_text(json.dumps(expected));(snapshot/'gateway-key.private').write_text(key)
  archive(snapshot/'after.tar.gz',[(target,'divine-api'),(snapshot/'installed-hashes.json','installed-hashes.json'),(snapshot/'gateway-key.private','gateway-key.private')]);after_proof=backup.off_vm(snapshot/'after.tar.gz',snapshot.name)
  report.update({'result':'pass','after_backup':after_proof,'api_files':sorted(expected),'media_hashes_preserved':len(before['media']),'catalog_queue_permissions_unchanged':True,'containers_not_restarted':True,'public_html_redirects_enabled':False,'native_source_files_unchanged':len(native),'anonymous_and_csrf_checks_passed':True})
 except Exception as error:
  # Roll back only our newly installed adapter; never restore the application database.
  if installed and {p.name:sha(p) for p in target.glob('*.php')}==expected:shutil.rmtree(target)
  if key_written:run('docker','exec',WEB,'rm','-f',KEY)
  report.update({'result':'fail','error_type':type(error).__name__,'rollback':'new adapter and key removed; existing application data retained'})
 (snapshot/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
