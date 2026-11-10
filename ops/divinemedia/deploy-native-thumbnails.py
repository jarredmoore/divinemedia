#!/usr/bin/env python3
"""Install the verified native still-cover hook and generate only the requested video cover."""
import argparse,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,tarfile,time,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';NAME='DivineThumbnails';UUID='dbdb9ef6-71f0-48e4-b512-67cf98f50b1d'
def run(*args,data=None):return subprocess.run(args,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=120).stdout.decode()
def sql(container,q):return run('docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names',data=q.encode()).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def state():
 files={str(p.relative_to(ROOT/'.compose/videos')):sha(p) for p in (ROOT/'.compose/videos').rglob('*') if p.is_file() and p.suffix.lower() in ['.mp4','.mp3','.jpg','.png','.webp','.gif']}
 return {'files':files,'catalog':sql('app-database-1','SELECT JSON_ARRAY(id,title,filename,status,users_id,modified) FROM videos ORDER BY id;'),'queue':sql('app-database_encoder-1','SELECT JSON_ARRAY(id,status,filename) FROM encoder_queue ORDER BY id;'),'permissions':sql('app-database-1','SELECT JSON_ARRAY(id,isAdmin,canUpload,canStream) FROM users ORDER BY id;'),'uptimes':run('docker','inspect','--format','{{.Name}} {{.State.StartedAt}}',WEB,'app-database-1','app-database_encoder-1','app-memcached-1','app-live-1')}
def invalidate():
 code="$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';require '/var/www/html/AVideo/videos/configuration.php';Plugin::deletePluginCache('"+UUID+"');"
 run('docker','exec',WEB,'php','-r',code)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--video',type=int,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();os.umask(0o077)
 assert a.video==19,'This reviewed deployment covers only requested video 19'
 bundle=pathlib.Path(a.bundle);stage=json.loads((bundle/'stage-report.json').read_text())
 assert stage['result']=='pass' and stage['checks']['automatic_thumbnail_on_native_video_upload'] and stage['checks']['existing_covers_and_audio_artwork_preserved']
 expected=stage['thumbnail_source_hashes'];assert {f.name:sha(f) for f in (bundle/'thumbnail-plugin').glob('*.php')}==expected
 manifest=bundle/'native-source-hashes.json';assert sha(manifest)==stage['native_source_manifest_sha256'];native=json.loads(manifest.read_text());assert all(sha(ROOT/n)==h for n,h in native.items()),'Installed native source changed after rehearsal'
 target=ROOT/'plugin'/NAME;assert not target.exists(),'Existing plugin requires an upgrade lease'
 assert sql('app-database-1',"SELECT COUNT(*) FROM plugins WHERE name='"+NAME+"' OR uuid='"+UUID+"';")=='0'
 filename=sql('app-database-1','SELECT filename FROM videos WHERE id='+str(a.video)+" AND type='video';");assert filename and '/' not in filename and '..' not in filename
 covers=list((ROOT/'.compose/videos').rglob(filename+'.jpg'));assert not covers,'Requested video already has a cover; do not replace it'
 if not a.apply:print(json.dumps({'result':'plan','new_native_plugin':NAME,'target_video':a.video,'preserve_existing_covers':True,'encoder_queue_dispatch':False}));raise SystemExit(0)
 snapshot=pathlib.Path('/srv/divinemedia/backups')/('native-thumbnail-deploy-'+uuid.uuid4().hex[:12]);snapshot.mkdir(mode=0o700)
 before=state();(snapshot/'before-state.json').write_text(json.dumps(before))
 with tarfile.open(snapshot/'before.tar.gz','w:gz') as tar:tar.add(snapshot/'before-state.json',arcname='before-state.json')
 spec=importlib.util.spec_from_file_location('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup);proof=backup.off_vm(snapshot/'before.tar.gz',snapshot.name)
 installed=False;registered=False;report={'result':'pending','state':str(snapshot),'before_backup':proof}
 try:
  temp=ROOT/'plugin'/('.divine-thumb-'+uuid.uuid4().hex);shutil.copytree(bundle/'thumbnail-plugin',temp);temp.chmod(0o755)
  for f in temp.glob('*.php'):f.chmod(0o644)
  temp.rename(target);installed=True
  for f in expected:run('docker','exec',WEB,'php','-l','/var/www/html/AVideo/plugin/'+NAME+'/'+f)
  sql('app-database-1',"INSERT INTO plugins (uuid,status,object_data,name,dirName,pluginversion,created,modified) VALUES ('"+UUID+"','active','{}','"+NAME+"','"+NAME+"','1.0',NOW(),NOW());");registered=True;invalidate()
  code="$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';require '/var/www/html/AVideo/videos/configuration.php';AVideoPlugin::loadPlugin('DivineThumbnails');echo json_encode(['queued'=>DivineThumbnails::enqueue(19)]);"
  raw=run('docker','exec','--user','www-data',WEB,'php','-r',code);assert json.loads(raw.strip().splitlines()[-1])['queued'],'Cover job was not queued'
  for attempt in range(60):
   covers=list((ROOT/'.compose/videos').rglob(filename+'.jpg'))
   if covers and covers[0].stat().st_size>100:break
   time.sleep(0.5)
  assert covers and covers[0].stat().st_size>100,'Cover was not generated'
  new=state();added=set(new['files'])-set(before['files']);relative=str(covers[0].relative_to(ROOT/'.compose/videos'))
  assert added=={relative} and all(new['files'].get(n)==h for n,h in before['files'].items()),'Unexpected media/artwork change'
  assert all(new[k]==before[k] for k in ['catalog','queue','permissions','uptimes']),'Existing application state changed'
  assert all(sha(ROOT/n)==h for n,h in native.items()),'Native source changed'
  (snapshot/'cover.sha256').write_text(sha(covers[0]));(snapshot/'after-state.json').write_text(json.dumps(new))
  with tarfile.open(snapshot/'after.tar.gz','w:gz') as tar:
   tar.add(target,arcname=NAME);tar.add(covers[0],arcname='video-19-cover.jpg');tar.add(snapshot/'after-state.json',arcname='after-state.json')
  after=backup.off_vm(snapshot/'after.tar.gz',snapshot.name)
  report.update({'result':'pass','after_backup':after,'active_plugin':NAME,'video_id':19,'cover_sha256':sha(covers[0]),'cover_bytes':covers[0].stat().st_size,'existing_media_and_artwork_files_preserved':len(before['files']),'catalog_queue_permissions_and_uptimes_unchanged':True,'native_source_files_preserved':len(native),'thumbnail_only':True,'encoder_queue_dispatched':False})
 except Exception as e:
  if registered:sql('app-database-1',"DELETE FROM plugins WHERE uuid='"+UUID+"' AND name='"+NAME+"';");invalidate()
  if installed and {f.name:sha(f) for f in target.glob('*.php')}==expected:shutil.rmtree(target)
  report.update({'result':'fail','error_type':type(e).__name__,'assertion':str(e)[:160] if isinstance(e,AssertionError) else None,'rollback':'new plugin disabled; application data and any generated cover retained'})
 (snapshot/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
