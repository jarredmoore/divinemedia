#!/usr/bin/env python3
"""Backed-up, lease-checked origin rollout. Never restart containers or dispatch jobs."""
import argparse,copy,hashlib,importlib.util,json,os,pathlib,shutil,uuid,yaml
os.umask(0o077)
s=importlib.util.spec_from_file_location('d','/srv/divinemedia/backups/native-glass-source-2c76a8467059/deploy-native-glass.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
ROOT=d.ROOT;WEB=d.WEB;LIVE='app-live-1';VHOST='/etc/apache2/sites-enabled/000-default.conf';NGINX='/usr/local/nginx/conf/nginx.conf';API=['index.php','native.php','creator.php','encoder-worker.php']
def sha(data):return hashlib.sha256(data).hexdigest()
def docker(*args,data=None):return d.run('docker',*args,data=data)
def put(path,raw):docker('exec','-i',LIVE,'sh','-c','cat > "$1"','sh',path,data=raw)
def put_vhost(raw):
 docker('exec','-i',WEB,'php','-r','$p=$argv[1];$m=fileperms($p)&0777;$t=tempnam(dirname($p),".dm-gate-");file_put_contents($t,stream_get_contents(STDIN));chmod($t,$m);if(!rename($t,$p))exit(2);',VHOST,data=raw)
def status(path):return int(docker('exec',WEB,'curl','--noproxy','media.divinemedia.us','--resolve','media.divinemedia.us:443:127.0.0.1','-sS','--max-time','20','-o','/dev/null','-w','%{http_code}','https://media.divinemedia.us'+path))
def save(state,plan):(state/'plan.json').write_text(json.dumps(plan))
def model(files):return yaml.safe_load(d.run('docker','compose',*[x for f in files for x in ['-f',f]],'config'))
def restore(state):
 plan=json.loads((state/'plan.json').read_text())
 for n,h in plan.get('written',{}).items():assert d.sha(ROOT/n)==h,'Source rollback lease changed'
 for n in ['.htaccess',*['divine-api/'+n for n in API]]:d.atomic(ROOT/n,(state/'files'/n).read_bytes())
 d.atomic(pathlib.Path(plan['host_vhost']),(state/'host-vhost-before.conf').read_bytes());put_vhost((state/'vhost-before.conf').read_bytes());put(NGINX,(state/'nginx-before.conf').read_bytes())
 if plan.get('compose_changed'):
  compose=pathlib.Path(plan['compose']);assert sha(compose.read_bytes())==plan['compose_after'],'Compose rollback lease changed';d.atomic(compose,(state/'compose-before.yml').read_bytes())
 docker('exec',WEB,'apache2ctl','-t');docker('exec',WEB,'apache2ctl','graceful')
 if plan.get('nginx_binary'):docker('exec',LIVE,plan['nginx_binary'],'-t','-c',NGINX);docker('exec',LIVE,plan['nginx_binary'],'-s','reload','-c',NGINX)
 for n in list(plan.get('written',{})):
  if n.startswith('divine-delivery/'):(ROOT/n).unlink()
 folder=ROOT/'divine-delivery'
 if folder.exists()and not any(folder.iterdir()):folder.rmdir()
 return {'result':'rolled_back','containers_restarted':False}
p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--phase',choices=['bridge','activate','rollback'],required=True);p.add_argument('--state');a=p.parse_args();bundle=pathlib.Path(a.bundle)
s=importlib.util.spec_from_file_location('gate',bundle/'media_gate.py');gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate)
if a.phase=='rollback':print(json.dumps(restore(pathlib.Path(a.state))));raise SystemExit()
assert json.loads((bundle/'stage-report.json').read_text())['result']=='pass','Exact native rehearsal required'
lease=json.loads((bundle/'lease.json').read_text())
if a.phase=='bridge':
 assert all(d.sha(ROOT/n)==h for n,h in lease.items()if not n.startswith('@')),'Native source lease changed'
 vh=docker('exec',WEB,'cat',VHOST);ng=docker('exec',LIVE,'cat',NGINX)
 assert sha(vh)==lease['@vhost']and sha(ng)==lease['@nginx'],'Origin config lease changed'
 host=ROOT/'.compose/domain-bootstrap/sites-enabled/000-default.conf';assert host.is_file(),'Persistent vhost missing'
 assert not(ROOT/'divine-delivery').exists(),'Existing gate needs upgrade review'
 state=pathlib.Path('/srv/divinemedia/backups')/('media-gate-deploy-'+uuid.uuid4().hex[:12]);state.mkdir(mode=0o700)
 before=d.snapshot();(state/'before-state.json').write_text(json.dumps(before))
 for n in ['.htaccess',*['divine-api/'+n for n in API]]:
  dest=state/'files'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
 (state/'host-vhost-before.conf').write_bytes(host.read_bytes());(state/'vhost-before.conf').write_bytes(vh);(state/'nginx-before.conf').write_bytes(ng)
 meta=json.loads(docker('inspect',LIVE))[0];files=meta['Config']['Labels']['com.docker.compose.project.config_files'].split(',');compose=pathlib.Path(files[-1]);service=meta['Config']['Labels']['com.docker.compose.service'];(state/'compose-before.yml').write_bytes(compose.read_bytes())
 d.archive(state/'before.tar.gz',[(state/'files','files'),(state/'vhost-before.conf','vhost.conf'),(state/'host-vhost-before.conf','host-vhost.conf'),(state/'nginx-before.conf','nginx.conf'),(state/'compose-before.yml','compose.yml'),(state/'before-state.json','before-state.json')]);proof=d.backup_module().off_vm(state/'before.tar.gz',state.name)
 plan={'bundle':str(bundle),'host_vhost':str(host),'compose':str(compose),'compose_files':files,'service':service,'written':{},'before_backup':proof};save(state,plan)
 try:
  folder=ROOT/'divine-delivery';folder.mkdir(mode=0o755);folder.chmod(0o755)
  for source in (bundle/'divine-delivery').glob('*.php'):
   dest=folder/source.name;dest.write_bytes(source.read_bytes());dest.chmod(0o644);plan['written'][str(dest.relative_to(ROOT))]=d.sha(dest)
  for n in API:
   dest=ROOT/'divine-api'/n;d.atomic(dest,(bundle/'divine-api'/n).read_bytes());plan['written'][str(dest.relative_to(ROOT))]=d.sha(dest)
  bridge=b'# DM_MEDIA_BRIDGE_V1\n<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteRule ^divine-media/(?:session|logout|assets/.*)$ divine-delivery/media.php [END]\n</IfModule>\n'
  d.atomic(ROOT/'.htaccess',bridge+(state/'files/.htaccess').read_bytes());plan['written']['.htaccess']=d.sha(ROOT/'.htaccess');save(state,plan)
  assert status('/divine-media/session')==401 and status('/divine-delivery/core.php')==404,'Bridge smoke failed'
  plan['phase']='bridge';save(state,plan);print(json.dumps({'result':'pass','phase':'bridge','state':str(state),'gate_active':False,'before_backup_verified':True}))
 except Exception:save(state,plan);restore(state);raise
else:
 state=pathlib.Path(a.state);plan=json.loads((state/'plan.json').read_text());assert plan['bundle']==str(bundle)and plan['phase']=='bridge'
 assert all(d.sha(ROOT/n)==h for n,h in plan['written'].items()),'Bridge lease changed'
 vh=(state/'vhost-before.conf').read_bytes();ng=(state/'nginx-before.conf').read_bytes();assert docker('exec',WEB,'cat',VHOST)==vh and docker('exec',LIVE,'cat',NGINX)==ng,'Origin config changed'
 desired_vh=gate.vhost(vh);desired_ng=gate.nginx_origin(ng)
 binary=docker('exec',LIVE,'sh','-c','for p in /proc/[0-9]*/comm; do if [ "$(cat "$p")" = nginx ]; then readlink "${p%/comm}/exe"; break; fi; done').decode().strip();assert binary.startswith('/');plan['nginx_binary']=binary
 managed=pathlib.Path('/srv/divinemedia/runtime/media-gate/live-conf');assert not managed.exists()or (managed/'nginx.conf').read_bytes()==desired_ng,'Managed config differs'
 managed.parent.mkdir(parents=True,exist_ok=True)
 if not managed.exists():docker('cp',LIVE+':/usr/local/nginx/conf',str(managed))
 (managed/'nginx.conf').write_bytes(desired_ng)
 compose=pathlib.Path(plan['compose']);original=(state/'compose-before.yml').read_bytes();assert compose.read_bytes()==original
 before_model=model(plan['compose_files']);doc=yaml.safe_load(original);doc['services']=doc.get('services')or {};doc['services'][plan['service']]=doc['services'].get(plan['service'])or {};node=doc['services'][plan['service']];node['volumes']=node.get('volumes')or [];node['volumes'].append(str(managed)+':/usr/local/nginx/conf')
 try:
  d.atomic(compose,yaml.safe_dump(doc,sort_keys=False).encode());plan.update(compose_changed=True,compose_after=sha(compose.read_bytes()));save(state,plan)
  filtered=copy.deepcopy(model(plan['compose_files']));filtered['services'][plan['service']]['volumes']=[m for m in filtered['services'][plan['service']].get('volumes',[])if m.get('target')!='/usr/local/nginx/conf'];assert filtered==before_model,'Unrelated Compose change'
  put('/usr/local/nginx/conf/.divine-media-gate.conf',desired_ng);docker('exec',LIVE,binary,'-t','-c','/usr/local/nginx/conf/.divine-media-gate.conf')
  d.atomic(pathlib.Path(plan['host_vhost']),desired_vh);put_vhost(desired_vh);docker('exec',WEB,'apache2ctl','-t')
  d.atomic(ROOT/'.htaccess',gate.root_rules((state/'files/.htaccess').read_bytes()));plan['written']['.htaccess']=d.sha(ROOT/'.htaccess');save(state,plan)
  put(NGINX,desired_ng);docker('exec',LIVE,binary,'-t','-c',NGINX);docker('exec',WEB,'apache2ctl','graceful');docker('exec',LIVE,binary,'-s','reload','-c',NGINX)
  assert status('/videos/.divine-private/frontend-gateway.php')in [403,404]and status('/.compose/videos/configuration.php')in [403,404]
  assert status('/Encoder/videos/fixture.mp4')in [403,404]
  after=d.snapshot();before=json.loads((state/'before-state.json').read_text());assert before['uptimes']==after['uptimes'],'Container restarted'
  plan['phase']='active';save(state,plan);(state/'after-state.json').write_text(json.dumps(after))
  d.archive(state/'after.tar.gz',[(ROOT/'divine-delivery','divine-delivery'),(ROOT/'.htaccess','root.htaccess'),(state/'plan.json','plan.json'),(managed,'live-conf'),(pathlib.Path(plan['host_vhost']),'vhost.conf')]);d.backup_module().off_vm(state/'after.tar.gz',state.name)
  print(json.dumps({'result':'pass','phase':'active','state':str(state),'existing_media_preserved':all(after['media'].get(n)==h for n,h in before['media'].items()),'catalog_unchanged':before['catalog']==after['catalog'],'queue_unchanged':before['queue']==after['queue'],'containers_restarted':False,'native_startup_invoked':False,'persistent_live_config':True}))
 except Exception:save(state,plan);restore(state);raise
