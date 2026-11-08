#!/usr/bin/env python3
"""Apply a verified domain release on Azure with automatic scoped rollback.
Only application URL settings, presentation assets, and Apache hostname/TLS config
change. Never upload files, run encoding, alter videos, or restore databases.
"""
import argparse,hashlib,importlib.util,json,os,pathlib,re,subprocess,sys,time,uuid
from urllib.parse import quote
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';MAIN_DB='app-database-1';ENC_DB='app-database_encoder-1'
OLD='media.divinecreativegroup.com';NEW='media.divinemedia.us'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def get(path,host=NEW,partial=False,natural=False):
 args=['docker','exec',WEB,'curl','--max-time','40','--noproxy',host,'-sS','-D','/tmp/dm-domain-headers','-w','\n__DM_STATUS__%{http_code}']
 if not natural:args+=['--resolve',host+':443:127.0.0.1']
 if partial:args+=['-H','Range: bytes=0-127']
 result=subprocess.run(args+['https://'+host+path],capture_output=True,check=True,timeout=50)
 body,status=result.stdout.rsplit(b'\n__DM_STATUS__',1);return int(status),body
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--commit',required=True);a=p.parse_args();os.umask(0o077)
 bundle=pathlib.Path(a.bundle).resolve();sys.path.insert(0,str(bundle));import domain_settings as settings
 spec=importlib.util.spec_from_file_location('domain_config',bundle/'apply-domain-config.py');domains=importlib.util.module_from_spec(spec);spec.loader.exec_module(domains)
 expected=json.loads((bundle/'source-hashes.json').read_text())
 for name,sha in expected.items():
  if digest(bundle/name)!=sha:raise RuntimeError('Release source differs from GitHub feature source')
 stage=json.loads((bundle/'stage-report.json').read_text())
 if stage['result']!='pass' or stage['rollback_reapply']!='pass' or stage.get('legacy_post_and_api_requests')!='not redirected':raise RuntimeError('Isolated verification incomplete')
 snapshot=pathlib.Path(pathlib.Path('/srv/divinemedia/backups/.latest-domain-snapshot').read_text().strip())
 proof=json.loads((snapshot/'database-settings-backup-report.json').read_text());settings_path=snapshot/'database-url-settings-before.json'
 if not proof['roundtrip_verified'] or digest(settings_path)!=proof['sha256']:raise RuntimeError('URL backup proof mismatch')
 before_settings=json.loads(settings_path.read_text())
 if settings.read_settings(MAIN_DB,ENC_DB)!=before_settings:raise RuntimeError('URL settings changed after backup')
 queue=lambda:settings.query(ENC_DB,'SELECT status,COUNT(*) FROM encoder_queue GROUP BY status;')
 before_queue=queue();active=settings.query(ENC_DB,"SELECT COUNT(*) FROM encoder_queue WHERE status NOT IN ('done','error');")
 if active!='0':raise RuntimeError('Processing queue is active; leave existing jobs running')
 api='/plugin/API/get.json.php?APIName=video&rowCount=50&current=1&noRelated=1'
 status,body=get(api,OLD);assert status==200;before_rows=json.loads(body)['response']['rows']
 handler_names=['objects/login.json.php','view/mini-upload-form/upload.php','view/mini-upload-form/assets/js/script.js','.compose/encoder/objects/Login.php','.compose/encoder/objects/Streamer.php','.compose/encoder/objects/Encoder.php','.htaccess','view/userLogin.php','view/mini-upload-form/index.php','.compose/encoder/view/index.php']
 before_handlers={name:digest(ROOT/name) for name in handler_names}
 media_root=ROOT/'.compose/videos'
 inventory={str(path.relative_to(media_root)):digest(path) for path in media_root.rglob('*') if path.is_file() and path.suffix.lower() in ['.mp3','.mp4']}
 nonce=uuid.uuid4().hex[:8];ui_state=snapshot/('application-'+nonce);db_state=snapshot/('settings-'+nonce)
 report={'commit':a.commit,'release':bundle.name,'snapshot':str(snapshot),'result':'pending'};ui_plan=None;db_plan=None;phase='apply-domain-config'
 try:
  ui_plan=domains.install(ROOT,WEB,bundle/'assets',snapshot,ui_state,True)
  phase='apply-url-settings';db_plan=settings.apply(MAIN_DB,ENC_DB,before_settings,db_state)
  time.sleep(3)
  phase='new-host-routes'
  paths=['/','/view/','/user','/Encoder/','/?type=audio','/videoEmbed/1','/objects/login.json.php']
  for path in paths:assert get(path)[0]==200,'Canonical route failed'
  assert get('/upload')[0]==302,'Guest upload guard changed'
  phase='legacy-compatibility'
  for path in ['/','/view/','/?type=audio','/videoEmbed/1',api]:assert get(path,OLD)[0]==200,'Legacy route failed'
  for path in ['/user','/upload','/Encoder/']:
   status,_=get(path,OLD);headers=subprocess.check_output(['docker','exec',WEB,'cat','/tmp/dm-domain-headers']).decode()
   assert status==302 and 'https://'+NEW+path in headers,'Legacy auth entry did not move to canonical host'
  phase='canonical-ui'
  status,body=get('/');assert b'https://divinemedia.us/' in body and ('https://'+NEW+'/').encode() in body,'Entrance links are not canonical'
  status,body=get('/user');assert b'id="loginForm"' in body and b'/divine-entrance/login-theme.js' in body,'Native login missing'
  headers=subprocess.check_output(['docker','exec',WEB,'cat','/tmp/dm-domain-headers']).decode()
  cookie_domains=re.findall(r'^Set-Cookie:.*?;\s*domain=([^;\r\n]+)',headers,re.I|re.M)
  assert all(x.lstrip('.').lower() in [NEW,'divinemedia.us'] for x in cookie_domains),'Incompatible login cookie domain'
  status,body=get('/Encoder/');assert b'id="siteURL"' in body and ('value="https://'+NEW+'/"').encode() in body,'Encoder default site is not canonical'
  phase='backend-self-connection'
  assert get('/objects/login.json.php',natural=True)[0]==200,'Backend cannot resolve/reach its own public hostname'
  php='require "videos/configuration.php";require_once "objects/Configuration.php";require_once "objects/Streamer.php";if(!Streamer::isURLAllowed("https://media.divinemedia.us/"))exit(2);if(!getExternalHttpUrlForShell("https://media.divinemedia.us/","domain-verification"))exit(3);'
  subprocess.run(['docker','exec','-w','/var/www/html/AVideo/Encoder',WEB,'php','-r',php],capture_output=True,check=True,timeout=40)
  phase='playback-and-preservation'
  for host in [OLD,NEW]:
   for suffix in ['.mp3','.mp4']:
    path=next(name for name in inventory if name.lower().endswith(suffix));assert get('/videos/'+quote(path,safe='/'),host,partial=True)[0]==206,'Media range failed'
  status,body=get(api);after_rows=json.loads(body)['response']['rows'];assert len(after_rows)==len(before_rows),'Catalog changed'
  assert before_handlers=={name:digest(ROOT/name) for name in handler_names},'Native handlers changed'
  assert before_queue==queue(),'Encoder queue changed during migration'
  current_inventory={str(path.relative_to(media_root)):digest(path) for path in media_root.rglob('*') if path.is_file() and path.suffix.lower() in ['.mp3','.mp4']}
  assert current_inventory==inventory,'Media inventory changed during migration'
  report.update({'result':'pass','canonical_routes':'200; guest upload 302','legacy_media_api_and_embeds':'compatible','legacy_auth_entries':'302 to new host','backend_public_self_connection':'pass','encoder_site_allowed':True,'login_cookie_domains':'compatible','catalog_rows':len(after_rows),'original_media_hashes_preserved':len(inventory),'native_handler_hashes_preserved':len(handler_names),'encoder_queue_unchanged':True,'mp3_mp4_ranges':'206 on both hosts','application_rollback':str(ui_state),'settings_rollback':str(db_state)})
 except Exception as error:
  if db_plan:settings.rollback(MAIN_DB,ENC_DB,db_state)
  if ui_plan:domains.rollback(ROOT,WEB,ui_state)
  report.update({'result':'rolled_back','failed_phase':phase,'error_type':type(error).__name__})
  if isinstance(error,AssertionError):report['assertion']=str(error)
  (bundle/'live-private-error.txt').write_text(str(error))
 report['containers']=subprocess.check_output(['docker','ps','--format','{{.Names}} {{.Status}}'],text=True).splitlines()
 (bundle/'live-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 if report['result']!='pass':raise SystemExit(1)
