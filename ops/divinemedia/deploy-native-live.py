#!/usr/bin/env python3
"""Activate staged native Live then PlayLists; preserve existing media and Encoder state."""
import argparse,gzip,importlib.util,json,os,pathlib,subprocess,tarfile,tempfile,time,uuid
import native_live as native
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';DB='app-database-1';VHOST='/etc/apache2/sites-enabled/000-default.conf'
def run(*args,input=None):return subprocess.run(args,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=90).stdout.decode()
def sql(q,container=DB):return run('docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names',input=q.encode()).strip()
ASSETS={'divine-shell/shell.js':'d6712e3823782d01379e40563285ec667a5a312de83beb4786bff85b0106e11c','divine-shell/head.php':'75ceb3c5680b9895f5b56b7b4a9feb7f51d5a395a9fe2204df4f6bb79419fd6b'}
def sha(p):return native.digest(p.read_bytes())
def atomic(path,raw):
 meta=path.stat();fd,temp=tempfile.mkstemp(prefix='.dm-native-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
  os.chmod(temp,meta.st_mode & 0o777);os.chown(temp,meta.st_uid,meta.st_gid);os.replace(temp,path)
 finally:
  if os.path.exists(temp):os.unlink(temp)
def media():
 import hashlib
 out={}
 for p in (ROOT/'.compose/videos').rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.mp3','.mp4']:
   h=hashlib.sha256()
   with p.open('rb') as f:
    for b in iter(lambda:f.read(1048576),b''):h.update(b)
   out[str(p.relative_to(ROOT/'.compose/videos'))]=h.hexdigest()
 return out
def selected():return [json.loads(x) for x in sql("SELECT JSON_OBJECT('id',id,'uuid',uuid,'name',name,'dirName',dirName,'status',status,'object_data',object_data,'pluginversion',pluginversion) FROM plugins WHERE name IN ('Live','PlayLists') ORDER BY name;").splitlines() if x]
def invalidate(proposal):
 # Only feature and enabled-plugin caches, never a global cache flush.
 code="$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';require '/var/www/html/AVideo/videos/configuration.php';foreach(json_decode(stream_get_contents(STDIN),true) as $uuid){Plugin::deletePluginCache($uuid);}"
 run('docker','exec','-i',WEB,'php','-r',code,input=json.dumps([m['uuid'] for m in proposal.values()]).encode())
def put_vhost(raw):
 code='$p=$argv[1];$m=fileperms($p)&0777;$u=fileowner($p);$g=filegroup($p);$t=tempnam(dirname($p),".dm-live-");file_put_contents($t,stream_get_contents(STDIN));chmod($t,$m);chown($t,$u);chgrp($t,$g);if(!rename($t,$p))exit(2);'
 run('docker','exec','-i',WEB,'php','-r',code,VHOST,input=raw)
def reload():run('docker','exec',WEB,'apache2ctl','-t');run('docker','exec',WEB,'apache2ctl','-k','graceful')
def get(path):return run('docker','exec',WEB,'curl','--user-agent','Mozilla/5.0 DivineMediaVerification','--max-time','40','--location','--max-redirs','4','-fsS','--noproxy','media.divinemedia.us','--resolve','media.divinemedia.us:443:127.0.0.1','https://media.divinemedia.us'+path)
def table_schema(table):return sql('SHOW CREATE TABLE `'+table+'`;')
def rollback(state, proposal):
 plan=json.loads((state/'plan.json').read_text());current=selected()
 if current!=plan['rows']:raise RuntimeError('Plugin configuration changed after activation; rollback lease refused')
 if native.digest(run('docker','exec',WEB,'cat',VHOST).encode())!=plan['vhost_after']:raise RuntimeError('Vhost rollback lease refused')
 for name,expected in plan.get('assets',{}).items():
  if sha(ROOT/name)!=expected:raise RuntimeError('Presentation rollback lease refused')
 for table,expected in plan['schema'].items():
  if table_schema(table)!=expected:raise RuntimeError('Feature schema changed; rollback lease refused')
 # Remove only the exact leased feature records. Keep newly used tables rather than discard user data.
 sql('START TRANSACTION;'+''.join('DELETE FROM plugins WHERE id='+str(row['id'])+' AND uuid='+native.literal(row['uuid'])+';' for row in current)+'COMMIT;')
 for name in plan.get('assets',{}):atomic(ROOT/name,(state/'files'/name).read_bytes())
 invalidate(proposal);put_vhost((state/'vhost-before.conf').read_bytes());reload()
 tables=list(plan['schema']);empty=all(sql('SELECT COUNT(*) FROM `'+t+'`;')=='0' for t in tables)
 if empty:sql('SET FOREIGN_KEY_CHECKS=0;'+''.join('DROP TABLE `'+t+'`;' for t in reversed(tables))+'SET FOREIGN_KEY_CHECKS=1;')
 return {'disabled_features':True,'original_vhost_restored':True,'new_empty_tables_removed':empty,'retained_feature_tables_for_user_data':not empty}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--bundle',required=True);parser.add_argument('--apply',action='store_true');parser.add_argument('--rollback');a=parser.parse_args();os.umask(0o077)
 if a.rollback:
  print(json.dumps(rollback(pathlib.Path(a.rollback),native.inspect(ROOT))));raise SystemExit(0)
 bundle=pathlib.Path(a.bundle);stage=json.loads((bundle/'stage-report.json').read_text())
 assert stage['result']=='pass' and stage['authorized_rtmp_to_https_hls'] and stage['invalid_rtmp_rejected'] and stage['native_playlist_player'] and stage['automatic_recording_off']
 proposal=native.inspect(ROOT);assert stage['source_hashes']==native.SOURCE_HASHES;assert not selected(),'Existing plugin records need an upgrade plan'
 schemas={n:native.schema_plan((ROOT/'plugin'/n/'install/install.sql').read_text(),n,sql('SHOW TABLES;').splitlines()) for n in proposal}
 original=run('docker','exec',WEB,'cat',VHOST).encode();updated=native.proxy_vhost(original)
 assert {n:sha(ROOT/n) for n in ASSETS}==ASSETS,'Presentation source changed since audit'
 if not a.apply:print(json.dumps({'result':'plan','plugins':list(proposal),'new_tables':sum([list(v) for v in native.SCHEMAS.values()],[]),'vhost_before':native.digest(original),'vhost_after':native.digest(updated)}));raise SystemExit(0)
 state=pathlib.Path('/srv/divinemedia/backups')/('native-live-deploy-'+uuid.uuid4().hex[:10]);state.mkdir(mode=0o700)
 (state/'vhost-before.conf').write_bytes(original)
 for name in ASSETS:
  dest=state/'files'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
 spec=importlib.util.spec_from_file_location('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
 before_media=media();before_catalog=sql('SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;');before_queue=sql('SELECT JSON_ARRAY(id,status,filename) FROM encoder_queue ORDER BY id;','app-database_encoder-1');before_users=sql('SELECT JSON_ARRAY(id,isAdmin,canStream) FROM users ORDER BY id;')
 protected=['.compose/videos/configuration.php','.compose/encoder/videos/configuration.php','view/mini-upload-form/index.php','.compose/encoder/view/index.php','objects/video.php','objects/user.php'];protected_hashes={p:sha(ROOT/p) for p in protected}
 uptime=run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}',WEB,DB,'app-database_encoder-1','app-memcached-1','app-live-1')
 (state/'before-state.json').write_text(json.dumps({'media':before_media,'catalog':before_catalog,'queue':before_queue,'permissions':before_users,'protected':protected_hashes,'uptime':uptime}))
 # Fresh native database snapshot is private and verified off VM before any DDL.
 dump=subprocess.run(['docker','exec',DB,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb-dump --user="$MYSQL_USER" --single-transaction --hex-blob --routines --triggers "$MYSQL_DATABASE"'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=90).stdout
 (state/'avideo-before.sql.gz').write_bytes(gzip.compress(dump))
 with tarfile.open(state/'before.tar.gz','w:gz') as tar:
  for name in ['vhost-before.conf','before-state.json','avideo-before.sql.gz','files']:tar.add(state/name,arcname=name)
 proof=backup.off_vm(state/'before.tar.gz',state.name)
 plan={'vhost_after':native.digest(original),'rows':[],'schema':{},'assets':{}};report={'result':'pending','state':str(state),'before_backup':proof};created=[];vhost_changed=False
 try:
  for name in ['Live','PlayLists']:
   created+=list(native.SCHEMAS[name]);sql(schemas[name]);plan['schema'].update({t:table_schema(t) for t in native.SCHEMAS[name]})
   sql(native.insert_plugin(name,proposal[name]));plan['rows']=selected();(state/'plan.json').write_text(json.dumps(plan));invalidate({name:proposal[name]})
  for name in ASSETS:
   raw=(bundle/'assets'/name).read_bytes();atomic(ROOT/name,raw);plan['assets'][name]=native.digest(raw);(state/'plan.json').write_text(json.dumps(plan))
  put_vhost(updated);vhost_changed=True;plan['vhost_after']=native.digest(updated);(state/'plan.json').write_text(json.dumps(plan));reload()
  for attempt in range(10):
   rendered=get('/view/?theme=code-black')
   if 'Live Footer Begin' in rendered and 'PlayLists Footer Begin' in rendered:break
   time.sleep(5)
  else:raise AssertionError('Native HTTP plugin discovery did not activate')
  for path in ['/live?theme=code-black','/view/?theme=code-black','/user?theme=code-black','/Encoder/?theme=code-black','/watch-later?theme=code-black','/favorite?theme=code-black']:
   body=get(path);assert '/divine-shell/shell.css' in body and 'Fatal error' not in body,'Native route verification failed: '+path
  # HLS traversal must retain native nginx/key authorization and never expose its control/stats endpoints.
  assert media()==before_media and sql('SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;')==before_catalog
  assert sql('SELECT JSON_ARRAY(id,status,filename) FROM encoder_queue ORDER BY id;','app-database_encoder-1')==before_queue
  assert sql('SELECT JSON_ARRAY(id,isAdmin,canStream) FROM users ORDER BY id;')==before_users
  assert {p:sha(ROOT/p) for p in protected}==protected_hashes
  assert run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}',WEB,DB,'app-database_encoder-1','app-memcached-1','app-live-1')==uptime
  (state/'after.json').write_text(json.dumps({'plan':plan,'options':native.OPTIONS}))
  after=backup.off_vm(state/'after.json',state.name)
  report.update({'result':'pass','after_backup':after,'active_native_plugins':['Live','PlayLists'],'new_tables':created,'media_hashes_preserved':len(before_media),'catalog_and_encoder_queue_unchanged':True,'creator_permissions_unchanged':True,'containers_not_restarted':True,'existing_thumbnail_processing_unchanged':True,'recording_default_off':True,'restreaming_off':True,'playlist_broadcasting_off':True,'public_broadcast_not_started':True})
 except Exception as e:
  # Handle partial activation without treating a whole database restore as a rollback.
  existing=sql('SHOW TABLES;').splitlines();plan['schema']={t:table_schema(t) for t in created if t in existing};(state/'plan.json').write_text(json.dumps(plan))
  try:report['rollback']=rollback(state,proposal)
  except Exception as recovery_error:report['rollback']={'lease_refused':True,'error_type':type(recovery_error).__name__}
  report.update({'result':'fail','error_type':type(e).__name__,'assertion':str(e)[:140] if isinstance(e,AssertionError) else None})
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
