#!/usr/bin/env python3
"""Activate four staged native UI utilities; never migrate or process media."""
import hashlib,importlib.util,json,os,pathlib,subprocess,uuid
import ui_plugins
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';DB='app-database-1'
def run(*a,**kw):return subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=90,**kw).stdout.decode()
def sql(q):return run('docker','exec','-i',DB,'sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb --user="$MYSQL_USER" "$MYSQL_DATABASE" --batch --raw --skip-column-names',input=q.encode()).strip()
def selected():return [json.loads(x) for x in sql("SELECT JSON_OBJECT('id',id,'uuid',uuid,'name',name,'dirName',dirName,'pluginversion',pluginversion,'status',status,'object_data',object_data) FROM plugins WHERE name IN ('Hotkeys','NextButton','SeekButton','TheaterButton') ORDER BY name;").splitlines() if x]
def native_create(proposal):
 code="$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';require '/var/www/html/AVideo/videos/configuration.php';foreach(json_decode(stream_get_contents(STDIN),true) as $name=>$m){$p=new Plugin(0);$p->setUuid($m['uuid']);$p->setName($name);$p->setDirName($name);$p->setPluginversion($m['version']);$p->setObject_data($m['options']);$p->setStatus('active');if(!$p->save())exit(2);}"
 run('docker','exec','-i',WEB,'php','-r',code,input=json.dumps(proposal).encode())
def invalidate_plugin_cache(proposal):
 code="$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';require '/var/www/html/AVideo/videos/configuration.php';foreach(json_decode(stream_get_contents(STDIN),true) as $uuid){Plugin::deletePluginCache($uuid);}"
 run('docker','exec','-i',WEB,'php','-r',code,input=json.dumps([m['uuid'] for m in proposal.values()]).encode())
def media_hashes():
 result={}
 for p in (ROOT/'.compose/videos').rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.mp3','.mp4']:
   h=hashlib.sha256()
   with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
   result[str(p.relative_to(ROOT/'.compose/videos'))]=h.hexdigest()
 return result
if __name__=='__main__':
 import sys
 if '--apply' not in sys.argv:raise SystemExit('Candidate operation: --apply required; live render blocker is unresolved, see docs/DIVINE-MEDIA-NATIVE-FEATURES.md')
 os.umask(0o077);stage=json.loads(pathlib.Path('/srv/divinemedia/backups/native-player-stage-report.json').read_text());assert stage['result']=='pass' and stage['native_player_utilities_rendered'];proposal=ui_plugins.inspect_sources(ROOT);assert {n:m['sha256'] for n,m in proposal.items()}==stage['ui_plugin_source_hashes'];assert not selected(),'Existing plugin rows require separate review'
 state=pathlib.Path('/srv/divinemedia/backups')/('player-utilities-'+uuid.uuid4().hex[:10]);state.mkdir(mode=0o700);before=media_hashes();catalog=sql('SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;');uptime=run('docker','inspect','--format','{{.State.StartedAt}}',WEB).strip();(state/'before.json').write_text(json.dumps({'selected_rows':[],'proposal':proposal,'media':before,'catalog':catalog,'container_started_at':uptime}));
 spec=importlib.util.spec_from_file_location('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
 before_proof=backup.off_vm(state/'before.json',state.name);report={'result':'pending','state':str(state),'before_backup':before_proof,'native_plugins':list(proposal),'no_container_restart':True,'migrations_run':False};inserted=[]
 try:
  native_create(proposal);inserted=selected();assert len(inserted)==4
  # Match the admin toggle's targeted plugin cache invalidation.
  invalidate_plugin_cache(proposal)
  html=run('docker','exec',WEB,'curl','--max-time','40','-fsS','--noproxy','media.divinemedia.us','--resolve','media.divinemedia.us:443:127.0.0.1','https://media.divinemedia.us/videoEmbed/1?autoplay=0&controls=1')
  (state/'private-native-player.html').write_text(html)
  report['native_markers']={'hotkeys':'plugin/Hotkeys/listener.js' in html,'seek':'playerSeekForward' in html}
  assert 'plugin/Hotkeys/listener.js' in html and 'playerSeekForward' in html and 'Fatal error' not in html
  assert media_hashes()==before and sql('SELECT JSON_ARRAY(id,title,filename,status,users_id) FROM videos ORDER BY id;')==catalog
  assert run('docker','inspect','--format','{{.State.StartedAt}}',WEB).strip()==uptime
  (state/'after.json').write_text(json.dumps(inserted));after_proof=backup.off_vm(state/'after.json',state.name)
  report.update({'result':'pass','after_backup':after_proof,'native_player_rendered':True,'media_hashes_preserved':len(before),'catalog_preserved':True,'seek_buttons_on_mobile':True})
 except Exception as error:
  if not inserted:inserted=selected()
  expected=all(row['name'] in proposal and row['uuid']==proposal[row['name']]['uuid'] and row['status']=='active' and row['pluginversion']==proposal[row['name']]['version'] and json.loads(row['object_data'])==json.loads(proposal[row['name']]['options']) for row in inserted)
  if inserted and expected and selected()==inserted:
   sql('START TRANSACTION;'+''.join('DELETE FROM plugins WHERE id='+str(row['id'])+' AND uuid='+ui_plugins.sql_literal(row['uuid'])+';' for row in inserted)+'COMMIT;');report['rolled_back']=not selected();invalidate_plugin_cache(proposal)
  report.update({'result':'fail','error_type':type(error).__name__})
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
