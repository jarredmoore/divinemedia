#!/usr/bin/env python3
"""Persist verified TLS/config mounts without restarting or recreating the backend.
The native startup/Encoder sequence is never invoked. Test only the TLS synchronizer.
"""
import copy,hashlib,importlib.util,json,os,pathlib,shutil,stat,subprocess,tarfile,tempfile,uuid
import yaml
ROOT=pathlib.Path('/srv/divinemedia/app');WEB='app-avideo-1';SYNC='/usr/local/bin/apache-sync-certificates.sh';VHOST='/etc/apache2/sites-enabled/000-default.conf'
PRIORITY=r'''
  # DM_CONFIGURED_TLS_PRIORITY: keep a valid certificate for the configured vhost.
  local configured_name configured_cert configured_key
  configured_name="$(awk '$1 == "ServerName" {print $2; exit}' "${CONFIG_FILE}")"
  configured_cert="$(awk '$1 == "SSLCertificateFile" {gsub(/\"/, "", $2); print $2; exit}' "${CONFIG_FILE}")"
  configured_key="$(awk '$1 == "SSLCertificateKeyFile" {gsub(/\"/, "", $2); print $2; exit}' "${CONFIG_FILE}")"
  if [ -n "${configured_name}" ] && [ -f "${configured_cert}" ] && [ -f "${configured_key}" ] \
    && is_certificate_valid "${configured_cert}" \
    && openssl x509 -in "${configured_cert}" -checkhost "${configured_name}" -noout 2>/dev/null | grep -Fq 'does match certificate'; then
    printf '%s\n%s\n' "${configured_cert}" "${configured_key}"
    return
  fi
'''
def run(*args,check=True,**kw):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check,timeout=90,**kw)
def docker(*args,**kw):return run('docker',*args,**kw)
def sha(data):return hashlib.sha256(data).hexdigest()
def atomic(path,data):
 meta=path.stat();fd,tmp=tempfile.mkstemp(prefix='.dm-bootstrap-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(data);out.flush();os.fsync(out.fileno())
  os.chmod(tmp,stat.S_IMODE(meta.st_mode));os.chown(tmp,meta.st_uid,meta.st_gid);os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def restore_mode(member,dest):
 item=tarfile.data_filter(member,dest)
 return item.replace(uid=member.uid,gid=member.gid,mode=member.mode & 0o777 if member.isfile() or member.isdir() else None) if item else None
def put_script(data):
 docker('exec','-i',WEB,'php','-r','$p=$argv[1];$m=fileperms($p)&0777;$u=fileowner($p);$g=filegroup($p);$t=tempnam(dirname($p),".dm-bootstrap-");file_put_contents($t,stream_get_contents(STDIN));chmod($t,$m);chown($t,$u);chgrp($t,$g);if(!rename($t,$p))exit(2);',SYNC,input=data)
def model(files):return yaml.safe_load(run('docker','compose',*[x for p in files for x in ['-f',p]],'config',cwd=ROOT).stdout)
if __name__=='__main__':
 os.umask(0o077);snapshot=pathlib.Path(pathlib.Path('/srv/divinemedia/backups/.latest-domain-snapshot').read_text().strip());state=snapshot/'bootstrap-state';state.mkdir(mode=0o700,exist_ok=False)
 report={'result':'pending','state':str(state),'no_container_restart':True,'native_startup_not_executed':True};phase='read-bootstrap';changed_script=False;changed_compose=False;target=ROOT/'.compose/domain-bootstrap';created_target=False
 try:
  record=json.loads(docker('inspect',WEB).stdout)[0];service=record['Config']['Labels']['com.docker.compose.service'];files=record['Config']['Labels']['com.docker.compose.project.config_files'].split(',');compose=pathlib.Path(files[-1]);original_compose=compose.read_bytes();original_sync=docker('exec',WEB,'cat',SYNC).stdout;original_vhost=docker('exec',WEB,'cat',VHOST).stdout
  if b'DM_CONFIGURED_TLS_PRIORITY' in original_sync:raise RuntimeError('Bootstrap TLS patch already exists; inspect its prior proof')
  anchor=b'get_effective_certificates() {\n'
  if original_sync.count(anchor)!=1:raise RuntimeError('Unexpected certificate synchronizer source')
  patched=original_sync.replace(anchor,anchor+PRIORITY.encode());(state/'sync-before.sh').write_bytes(original_sync);(state/'compose-before.yml').write_bytes(original_compose);(state/'vhost-before.conf').write_bytes(original_vhost)
  env=dict(x.split('=',1) for x in record['Config']['Env'] if '=' in x)
  current_cert='/etc/letsencrypt/live/divinemedia/fullchain.pem';current_key='/etc/letsencrypt/live/divinemedia/privkey.pem'
  for key,current in [('TLS_CERTIFICATE_FILE',current_cert),('TLS_CERTIFICATE_KEY',current_key)]:
   candidate=env.get(key)
   if candidate:
    one=docker('exec',WEB,'readlink','-f',candidate,check=False).stdout.strip();two=docker('exec',WEB,'readlink','-f',current).stdout.strip()
    if one and one==two:raise RuntimeError('Native startup could overwrite the managed certificate; review its generation settings')
  before_model=model(files);doc=yaml.safe_load(original_compose);node=doc['services'].setdefault(service,{});volumes=node.setdefault('volumes',[])
  targets=['/etc/apache2/sites-enabled',SYNC]
  for mount in before_model['services'][service].get('volumes',[]):
   if mount.get('target') in targets or mount.get('target','').startswith('/etc/apache2/sites-enabled/'):raise RuntimeError('An existing Apache/bootstrap mount requires separate review')
  if target.exists():raise RuntimeError('Refusing an unowned bootstrap directory')
  target.mkdir(mode=0o700);created_target=True;(target/'apache-sync-certificates.sh').write_bytes(patched);(target/'apache-sync-certificates.sh').chmod(0o755)
  docker('cp','-a',WEB+':/etc/apache2/sites-enabled/.',str(target/'sites-enabled'))
  volumes.extend(['./.compose/domain-bootstrap/sites-enabled:/etc/apache2/sites-enabled','./.compose/domain-bootstrap/apache-sync-certificates.sh:'+SYNC+':ro'])
  desired=yaml.safe_dump(doc,sort_keys=False).encode()
  spec=importlib.util.spec_from_file_location('backup',pathlib.Path(__file__).with_name('prepare-domain-certificate.py'));backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
  with tarfile.open(state/'bootstrap-before.tar.gz','w:gz') as archive:
   for name in ['sync-before.sh','compose-before.yml','vhost-before.conf']:archive.add(state/name,arcname=name)
  report['before_backup']=backup.off_vm(state/'bootstrap-before.tar.gz',snapshot.name)
  phase='isolated-tls-sync-test';scratch=pathlib.Path(tempfile.mkdtemp(prefix='bootstrap-tls-',dir='/srv/divinemedia/backups'));name='dm-bootstrap-tls-'+uuid.uuid4().hex[:10];network=name+'-net'
  try:
   with tarfile.open(snapshot/'runtime-active.tar.gz') as archive:archive.extractall(scratch,filter=restore_mode)
   (scratch/'sync.sh').write_bytes(patched);(scratch/'sync.sh').chmod(0o755)
   config=scratch/'etc/apache2/sites-enabled/000-default.conf';before_test=config.read_bytes()
   docker('network','create','--internal',network)
   args=['run','--name',name,'--network',network,'--memory','256m','--memory-swap','256m','--cpus','0.25','--pids-limit','96','--entrypoint','/bin/bash','-e','SERVER_NAME=localhost','-e','TLS_CERTIFICATE_FILE=/tmp/unusable-default.crt','-e','TLS_CERTIFICATE_KEY=/tmp/unusable-default.key']
   for source,dest,readonly in [(scratch/'sync.sh',SYNC,True),(scratch/'etc/apache2','/etc/apache2',False),(scratch/'etc/letsencrypt','/etc/letsencrypt',False)]:args+=['--mount','type=bind,src='+str(source)+',dst='+dest+(',readonly' if readonly else '')]
   args+=[record['Image'],'-c',SYNC+' && apache2ctl -t'];docker(*args)
   if config.read_bytes()!=before_test:raise RuntimeError('TLS sync changed the verified vhost unexpectedly')
   report['isolated_test']='valid configured dual-host certificate wins over unusable localhost defaults'
  finally:
   docker('rm','-fv',name,check=False);docker('network','rm',network,check=False);shutil.rmtree(scratch)
  phase='persist-compose-and-runtime'
  if compose.read_bytes()!=original_compose or docker('exec',WEB,'cat',SYNC).stdout!=original_sync:raise RuntimeError('Deployment configuration changed during verification')
  atomic(compose,desired);changed_compose=True;after_model=model(files);filtered=copy.deepcopy(after_model)
  filtered['services'][service]['volumes']=[m for m in filtered['services'][service].get('volumes',[]) if m.get('target') not in targets]
  if filtered!=before_model:raise RuntimeError('An unrelated Compose setting changed')
  put_script(patched);changed_script=True;docker('exec',WEB,'bash','-n',SYNC);docker('exec',WEB,SYNC)
  if docker('exec',WEB,'cat',VHOST).stdout!=original_vhost:raise RuntimeError('Active vhost changed unexpectedly')
  docker('exec',WEB,'apache2ctl','-t')
  phase='off-vm-persistent-state'
  with tarfile.open(state/'bootstrap-after.tar.gz','w:gz') as archive:archive.add(compose,arcname='compose-after.yml');archive.add(target,arcname='domain-bootstrap')
  report['after_backup']=backup.off_vm(state/'bootstrap-after.tar.gz',snapshot.name)
  plan={'compose':str(compose),'compose_before':sha(original_compose),'compose_after':sha(desired),'sync_before':sha(original_sync),'sync_after':sha(patched),'managed_directory':str(target)};(state/'plan.json').write_text(json.dumps(plan,indent=2))
  report.update({'result':'pass','service':service,'compose_bind_mounts_added':2,'unrelated_compose_settings_unchanged':True,'active_vhost_unchanged':True,'native_encoder_startup_untouched':True})
 except Exception as error:
  if changed_script:put_script(original_sync)
  if changed_compose:atomic(compose,original_compose)
  if created_target:shutil.rmtree(target)
  report.update({'result':'fail','failed_phase':phase,'error_type':type(error).__name__});(state/'private-error.txt').write_text(str(error))
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 if report['result']!='pass':raise SystemExit(1)
