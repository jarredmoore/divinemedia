#!/usr/bin/env python3
"""Lease and upgrade only the two JSON adapter files that project public player preferences."""
import argparse,importlib.util,json,os,pathlib,subprocess,tarfile,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';NAMES=['native.php','read.php']
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();os.umask(0o077)
 bundle=pathlib.Path(a.bundle);base=load('base',bundle/'deploy-native-thumbnails.py');sha=base.sha;run=base.run
 stage=json.loads((bundle/'stage-report.json').read_text());assert stage['result']=='pass' and stage['checks']['native_player_configuration_and_disable_switch']
 expected=stage['api_source_hashes'];before_hashes=json.loads((bundle/'player-before-hashes.json').read_text())
 assert set(before_hashes)==set(NAMES)
 for name in expected:
  assert sha(bundle/'api'/name)==expected[name]
  assert sha(ROOT/'divine-api'/name)==(before_hashes[name] if name in NAMES else expected[name]),'Adapter source changed after audit'
 manifest=bundle/'native-source-hashes.json';assert sha(manifest)==stage['native_source_manifest_sha256'];native=json.loads(manifest.read_text());assert all(sha(ROOT/n)==h for n,h in native.items())
 if not a.apply:print(json.dumps({'result':'plan','api_files':NAMES,'native_settings_written':False,'new_public_fields':['seek','hotkeys','theater','miniPlayer']}));raise SystemExit(0)
 snapshot=pathlib.Path('/srv/divinemedia/backups')/('player-preferences-'+uuid.uuid4().hex[:12]);snapshot.mkdir(mode=0o700)
 before=base.state();(snapshot/'before-state.json').write_text(json.dumps(before))
 for name in NAMES:(snapshot/name).write_bytes((ROOT/'divine-api'/name).read_bytes())
 with tarfile.open(snapshot/'before.tar.gz','w:gz') as tar:
  for name in ['before-state.json',*NAMES]:tar.add(snapshot/name,arcname=name)
 backup=load('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');proof=backup.off_vm(snapshot/'before.tar.gz',snapshot.name)
 report={'result':'pending','state':str(snapshot),'before_backup':proof};written=[]
 def put(path,data):
  mode=path.stat().st_mode&0o777;tmp=path.with_name('.'+path.name+'.player-update');tmp.write_bytes(data);tmp.chmod(mode);tmp.replace(path)
 try:
  for name in NAMES:
   put(ROOT/'divine-api'/name,(bundle/'api'/name).read_bytes());written.append(name)
   run('docker','exec',WEB,'php','-l','/var/www/html/AVideo/divine-api/'+name)
  # Use the existing private gateway key inside the container; never put it in argv/output.
  code="""$key=trim(file_get_contents('/var/www/tmp/divine-frontend-gateway.key'));$c=curl_init('https://media.divinemedia.us/divine-api/index.php?action=video&id=19');curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_RESOLVE=>['media.divinemedia.us:443:127.0.0.1'],CURLOPT_HTTPHEADER=>['X-Divine-Gateway-Key: '.$key,'X-Divine-Frontend-Origin: https://divinemedia.us'],CURLOPT_TIMEOUT=>25]);$raw=curl_exec($c);$status=curl_getinfo($c,CURLINFO_RESPONSE_CODE);$d=json_decode($raw,true);if($status!==200||!isset($d['player']['seek']))exit(4);echo json_encode(['status'=>$status,'player'=>$d['player']]);"""
  smoke=json.loads(run('docker','exec',WEB,'php','-r',code));after=base.state()
  assert after['files']==before['files'],'Media or artwork changed'
  core=lambda s:[json.loads(line)[:-1] for line in s.splitlines() if line]
  assert core(after['catalog'])==core(before['catalog']) and all(after[k]==before[k] for k in ['queue','permissions','uptimes'])
  assert all(sha(ROOT/n)==h for n,h in native.items())
  (snapshot/'after-state.json').write_text(json.dumps(after))
  with tarfile.open(snapshot/'after.tar.gz','w:gz') as tar:
   for name in NAMES:tar.add(ROOT/'divine-api'/name,arcname=name)
   tar.add(snapshot/'after-state.json',arcname='after-state.json')
  after_proof=backup.off_vm(snapshot/'after.tar.gz',snapshot.name)
  report.update({'result':'pass','after_backup':after_proof,'api_files':NAMES,'public_projection':smoke,'existing_media_artwork_preserved':len(before['files']),'catalog_content_queue_permissions_uptimes_unchanged':True,'native_sources_unchanged':True,'plugin_settings_written':False,'encoder_jobs_started':False})
 except Exception as e:
  for name in written:
   path=ROOT/'divine-api'/name
   if sha(path)==expected[name]:put(path,(snapshot/name).read_bytes())
  report.update({'result':'fail','error_type':type(e).__name__,'assertion':str(e)[:140] if isinstance(e,AssertionError) else None,'rollback':'only matching adapter files restored'})
 (snapshot/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
