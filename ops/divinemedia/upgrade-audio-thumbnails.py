#!/usr/bin/env python3
"""Lease the existing thumbnail plugin, add audio covers, and backfill only the reviewed new uploads."""
import argparse,importlib.util,json,os,pathlib,shutil,tarfile,time,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');NAME='DivineThumbnails';WEB='app-avideo-1';UUID='dbdb9ef6-71f0-48e4-b512-67cf98f50b1d'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();os.umask(0o077)
 bundle=pathlib.Path(a.bundle);base=load('deploy_base',bundle/'deploy-native-thumbnails.py');sha=base.sha;run=base.run;sql=base.sql
 stage=json.loads((bundle/'stage-report.json').read_text());assert stage['result']=='pass'
 for key in ['automatic_thumbnail_on_native_video_upload','automatic_audio_waveform_fallback','registered_album_metadata_match_and_embedded_art','batch_larger_than_eight_drains_automatically','existing_covers_and_audio_artwork_preserved']:assert stage['checks'][key]
 assets=bundle/'thumbnail-plugin';expected=stage['thumbnail_source_hashes'];assert {str(p.relative_to(assets)):sha(p) for p in assets.rglob('*') if p.is_file()}==expected
 manifest=bundle/'native-source-hashes.json';assert sha(manifest)==stage['native_source_manifest_sha256'];native=json.loads(manifest.read_text());assert all(sha(ROOT/n)==h for n,h in native.items()),'Native files changed since rehearsal'
 target=ROOT/'plugin'/NAME;before_plugin={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()};assert set(before_plugin)=={'DivineThumbnails.php','worker.php','clear-cache.php'}
 row=json.loads(sql('app-database-1',"SELECT JSON_OBJECT('id',id,'status',status,'pluginversion',pluginversion,'object_data',object_data,'modified',modified) FROM plugins WHERE uuid='"+UUID+"';"));assert row['status']=='active' and row['pluginversion']=='1.0'
 rows=[json.loads(s) for s in sql('app-database-1',"SELECT JSON_OBJECT('id',id,'filename',filename,'title',title,'type',type) FROM videos WHERE id BETWEEN 20 AND 30 ORDER BY id;").splitlines()];assert [v['id'] for v in rows]==list(range(20,31)) and all(v['type']=='audio' for v in rows)
 if not a.apply:print(json.dumps({'result':'plan','upgrade':'1.0 to 1.1','target_ids':[v['id'] for v in rows],'audio_cover_priority':['embedded','registered album','waveform'],'encoder_queue_dispatch':False}));raise SystemExit(0)
 snapshot=pathlib.Path('/srv/divinemedia/backups')/('audio-cover-upgrade-'+uuid.uuid4().hex[:12]);snapshot.mkdir(mode=0o700)
 before=base.state();(snapshot/'before-state.json').write_text(json.dumps(before));(snapshot/'plugin-row.json').write_text(json.dumps(row));shutil.copytree(target,snapshot/'plugin-before')
 with tarfile.open(snapshot/'before.tar.gz','w:gz') as tar:
  for name in ['before-state.json','plugin-row.json','plugin-before']:tar.add(snapshot/name,arcname=name)
 backup=load('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');proof=backup.off_vm(snapshot/'before.tar.gz',snapshot.name)
 report={'result':'pending','state':str(snapshot),'before_backup':proof};changed=False
 try:
  # Replace the worker first, then the hook. Existing 1.0 video-only jobs are compatible.
  changed=True
  for name in ['covers/2ndTimeAround.jpg','album-covers.json','clear-cache.php','worker.php','DivineThumbnails.php']:
   path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.parent.chmod(0o755);tmp=path.with_name('.'+path.name+'.new');tmp.write_bytes((assets/name).read_bytes());tmp.chmod(0o644);tmp.replace(path)
  changed=True
  for name in ['DivineThumbnails.php','worker.php','clear-cache.php']:run('docker','exec',WEB,'php','-l','/var/www/html/AVideo/plugin/'+NAME+'/'+name)
  sql('app-database-1',"UPDATE plugins SET pluginversion='1.1',modified=NOW() WHERE uuid='"+UUID+"' AND pluginversion='1.0';");base.invalidate()
  code="$_SERVER['HTTP_HOST']='media.divinemedia.us';$_SERVER['HTTPS']='on';$_SERVER['REQUEST_URI']='/';require '/var/www/html/AVideo/videos/configuration.php';AVideoPlugin::loadPlugin('DivineThumbnails');$out=[];foreach(json_decode(stream_get_contents(STDIN),true) as $id){$out[$id]=DivineThumbnails::enqueue($id);}echo json_encode($out);"
  raw=run('docker','exec','-i','--user','www-data',WEB,'php','-r',code,data=json.dumps([v['id'] for v in rows]).encode());queued=json.loads(raw.strip().splitlines()[-1])
  covers={}
  for attempt in range(120):
   for v in rows:
    found=list((ROOT/'.compose/videos').rglob(v['filename']+'.jpg'))
    if found and found[0].stat().st_size>100:covers[v['id']]=found[0]
   if len(covers)==len(rows):break
   time.sleep(0.5)
  assert len(covers)==11,'Not all new audio covers were produced'
  after=base.state();assert all(after['files'].get(n)==h for n,h in before['files'].items()),'An existing media or artwork file changed'
  added=set(after['files'])-set(before['files']);assert all(any(pathlib.Path(n).name.startswith(v['filename']) for v in rows) and pathlib.Path(n).suffix in ['.jpg','.png','.webp'] for n in added),'Unexpected media added'
  assert all(after[k]==before[k] for k in ['catalog','queue','permissions','uptimes']),'Catalog, queue, permissions or uptimes changed'
  assert all(sha(ROOT/n)==h for n,h in native.items() if not n.startswith('plugin/DivineThumbnails/'))
  assert {str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()}==expected
  (snapshot/'after-state.json').write_text(json.dumps(after))
  with tarfile.open(snapshot/'after.tar.gz','w:gz') as tar:
   tar.add(target,arcname='plugin-after');tar.add(snapshot/'after-state.json',arcname='after-state.json')
   for id,path in covers.items():tar.add(path,arcname='covers/'+str(id)+'.jpg')
  after_proof=backup.off_vm(snapshot/'after.tar.gz',snapshot.name)
  report.update({'result':'pass','after_backup':after_proof,'plugin_version':'1.1','generated_cover_ids':sorted(covers),'existing_media_and_artwork_preserved':len(before['files']),'catalog_queue_permissions_uptimes_unchanged':True,'native_core_sources_unchanged':True,'encoder_queue_dispatched':False,'cover_hashes':{str(id):sha(path) for id,path in covers.items()}})
 except Exception as e:
  if changed:
   current={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()}
   if all(h in {expected.get(n),before_plugin.get(n)} for n,h in current.items()) and set(before_plugin)<=set(current):
    shutil.rmtree(target);shutil.copytree(snapshot/'plugin-before',target)
    sql('app-database-1',"UPDATE plugins SET pluginversion='1.0' WHERE uuid='"+UUID+"' AND pluginversion='1.1';");base.invalidate()
  report.update({'result':'fail','error_type':type(e).__name__,'assertion':str(e)[:140] if isinstance(e,AssertionError) else None,'rollback':'Own plugin restored when its lease matches; generated covers and user media retained'})
 (snapshot/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
