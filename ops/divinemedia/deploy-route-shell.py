#!/usr/bin/env python3
"""Deploy the independently staged HTML shell with private backup and exact rollback."""
import argparse,hashlib,importlib.util,json,os,pathlib,subprocess,tarfile,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1'
def run(*a,**kw):return subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=90,**kw).stdout.decode()
def sql(container,q):return run('docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names',input=q.encode()).strip()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def media_hashes():
 out={}
 for p in (ROOT/'.compose/videos').rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.mp3','.mp4']:
   h=hashlib.sha256()
   with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
   out[str(p.relative_to(ROOT/'.compose/videos'))]=h.hexdigest()
 return out
def get(path,host='media.divinemedia.us',partial=False):
 args=['docker','exec',WEB,'curl','--max-time','40','-fsS','--noproxy',host,'--resolve',host+':443:127.0.0.1']
 if partial:args+=['-H','Range: bytes=0-127']
 return run(*args,'https://'+host+path)
def archive(path,paths):
 with tarfile.open(path,'w:gz') as out:
  for p,arc in paths:out.add(p,arcname=arc)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);a=p.parse_args();os.umask(0o077);bundle=pathlib.Path(a.bundle)
 stage=json.loads((bundle/'stage-report.json').read_text());assert stage['result']=='pass' and stage['rollback_reapply_passed'] and stage['media_ranges_and_api_unchanged']
 installer=module('routes',bundle/'apply-route-shell.py');backup=module('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py')
 expected=stage['route_plan'];plan=installer.install(ROOT,bundle/'assets','/srv/divinemedia/backups',expected['before']);assert {k:plan[k] for k in ['before','after','assets']}=={k:expected[k] for k in ['before','after','assets']},'Staged deployment source changed'
 state=pathlib.Path('/srv/divinemedia/backups')/('route-shell-'+uuid.uuid4().hex[:10]);state.mkdir(mode=0o700)
 media=media_hashes();catalog=lambda:sql('app-database-1','SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;');before_catalog=catalog();queue=lambda:sql('app-database_encoder-1','SELECT id,status FROM encoder_queue ORDER BY id;');before_queue=queue()
 assert sql('app-database_encoder-1',"SELECT COUNT(*) FROM encoder_queue WHERE status NOT IN ('done','error');")=='0','Existing Encoder work is active; retry after it completes'
 protected=['objects/login.json.php','objects/userCreate.json.php','objects/userRecoverPass.php','view/userLogin.php','view/mini-upload-form/upload.php','view/mini-upload-form/index.php','.compose/encoder/objects/Login.php','.compose/encoder/objects/Encoder.php','.compose/encoder/view/index.php','.compose/videos/configuration.php','.compose/encoder/videos/configuration.php']
 hashes={n:sha(ROOT/n) for n in protected};uptimes=run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}','app-avideo-1','app-database-1','app-database_encoder-1','app-memcached-1','app-live-1')
 (state/'before-state.json').write_text(json.dumps({'plan':plan,'media':media,'catalog':before_catalog,'queue':before_queue,'protected':hashes,'uptimes':uptimes}));archive(state/'route-before.tar.gz',[(ROOT/n,n) for n in installer.FILES]+[(state/'before-state.json','before-state.json')]);before_backup=backup.off_vm(state/'route-before.tar.gz',state.name)
 report={'result':'pending','state':str(state),'before_backup':before_backup,'no_container_restart':True,'no_database_settings_changed':True};applied=None
 try:
  applied=installer.install(ROOT,bundle/'assets',state,expected['before'],True)
  for name in installer.FILES:
   if name.endswith('.php'):
    runtime='/var/www/html/AVideo/'+name.replace('.compose/encoder/','Encoder/');run('docker','exec',WEB,'php','-l',runtime)
  for name in ['head.php','legacy-entry.php']:run('docker','exec',WEB,'php','-l','/var/www/html/AVideo/divine-shell/'+name)
  run('docker','exec',WEB,'apache2ctl','-t')
  paths=['/','/?theme=code-black','/view/?theme=code-black','/user?theme=code-black','/signUp?theme=code-black','/cat/default?theme=code-black','/view/channels.php?theme=code-black','/channel/admin?theme=code-black','/Encoder/?theme=code-black','/plugin/UserNotifications/embed.php?theme=code-black','/videoEmbed/1?theme=code-black']
  for path in paths:
   body=get(path);assert '/divine-shell/shell.css' in body and 'data-divine-route-critical' in body and 'Fatal error' not in body,path
  assert 'divine-shell' not in get('/plugin/API/get.json.php?APIName=video&rowCount=50&current=1&noRelated=1')
  assert media_hashes()==media and catalog()==before_catalog and queue()==before_queue
  assert {n:sha(ROOT/n) for n in protected}==hashes and run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}','app-avideo-1','app-database-1','app-database_encoder-1','app-memcached-1','app-live-1')==uptimes
  archive(state/'route-after.tar.gz',[(ROOT/n,n) for n in installer.FILES]+[(ROOT/'divine-shell','divine-shell')]);after_backup=backup.off_vm(state/'route-after.tar.gz',state.name)
  report.update({'result':'pass','after_backup':after_backup,'rollback_snapshot':applied['snapshot'],'html_routes_verified':paths,'media_hashes_preserved':len(media),'catalog_and_encoder_queue_unchanged':True,'protected_native_files_unchanged':len(hashes),'all_container_uptimes_unchanged':True,'native_startup_not_run':True})
 except Exception as error:
  if applied:report['rollback']=installer.rollback(ROOT,applied['snapshot'])
  report.update({'result':'fail','error_type':type(error).__name__,'assertion':str(error)[:120] if isinstance(error,AssertionError) else None})
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
