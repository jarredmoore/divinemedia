#!/usr/bin/env python3
"""Lease-checked hostname/presentation changes; no database or media writes.
Use after prepare-domain-certificate.py has verified the private off-VM snapshot.
"""
import argparse,hashlib,json,os,pathlib,re,stat,subprocess,tarfile,tempfile,uuid
OLD='media.divinecreativegroup.com';NEW='media.divinemedia.us'
VHOST='/etc/apache2/sites-enabled/000-default.conf'
ASSETS=['divine-entrance/landing.php','divine-entrance/login-theme.js','divine-entrance/login-theme.php','divine-creator/creator.js','divine-creator/theme.php']
CONFIGS=['.compose/videos/configuration.php','.compose/encoder/videos/configuration.php']
def digest(data):return hashlib.sha256(data).hexdigest()
def docker(web,*args,data=None):return subprocess.run(['docker','exec',*(['-i'] if data is not None else []),web,*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=60)
def atomic(path,data):
 metadata=path.stat();fd,tmp=tempfile.mkstemp(prefix='.dm-domains-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(data);out.flush();os.fsync(out.fileno())
  os.chmod(tmp,stat.S_IMODE(metadata.st_mode))
  if os.geteuid()==0:os.chown(tmp,metadata.st_uid,metadata.st_gid)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def write_vhost(web,data):
 php='$p=$argv[1];$m=fileperms($p)&0777;$u=fileowner($p);$g=filegroup($p);$t=tempnam(dirname($p),".dm-domains-");file_put_contents($t,stream_get_contents(STDIN));chmod($t,$m);chown($t,$u);chgrp($t,$g);if(!rename($t,$p))exit(2);'
 docker(web,'php','-r',php,VHOST,data=data)
def apache_reload(web):
 docker(web,'apache2ctl','-t');docker(web,'apache2ctl','-k','graceful')
def rollback(root,web,state):
 root=pathlib.Path(root);state=pathlib.Path(state);plan=json.loads((state/'plan.json').read_text())
 for name,sha in plan['after'].items():
  if digest((root/name).read_bytes())!=sha:raise RuntimeError('Later source change prevents rollback')
 if digest(docker(web,'cat',VHOST).stdout)!=plan['vhost_after']:raise RuntimeError('Later vhost change prevents rollback')
 for name,sha in plan['before'].items():
  if digest((state/'files'/name).read_bytes())!=sha:raise RuntimeError('Rollback snapshot checksum mismatch')
 original=(state/'vhost-before.conf').read_bytes()
 if digest(original)!=plan['vhost_before']:raise RuntimeError('Vhost snapshot checksum mismatch')
 for name in plan['before']:atomic(root/name,(state/'files'/name).read_bytes())
 write_vhost(web,original);apache_reload(web)
 return {'rolled_back':True}
def install(root,web,assets,snapshot,state,apply=False):
 root=pathlib.Path(root);assets=pathlib.Path(assets);snapshot=pathlib.Path(snapshot);state=pathlib.Path(state)
 cert=json.loads((snapshot/'certificate-report.json').read_text())
 if cert['result']!='pass' or not all(x['roundtrip_verified'] for x in cert['off_vm']):raise RuntimeError('Verified off-VM snapshot is required')
 expected=json.loads((snapshot/'before.json').read_text());originals={};changes={}
 for name in CONFIGS+ASSETS:
  path=root/name
  if path.is_symlink():raise RuntimeError('Unexpected source symlink')
  originals[name]=path.read_bytes()
  if digest(originals[name])!=expected[name]:raise RuntimeError('Source changed since domain snapshot')
 for name in CONFIGS:
  data=originals[name];pattern=rb"(\$global\[['\"]webSiteRootURL['\"]\]\s*=\s*['\"])https://media[.]divinecreativegroup[.]com(/(?:Encoder/)?)"
  changes[name],count=re.subn(pattern,lambda m:m.group(1)+b'https://'+NEW.encode()+m.group(2),data)
  if count!=1:raise RuntimeError('Unexpected public URL configuration shape')
 for name in ASSETS:changes[name]=(assets/name).read_bytes()
 original_vhost=docker(web,'cat',VHOST).stdout
 with tarfile.open(snapshot/'runtime-before.tar.gz') as archive:
  member=archive.getmember(VHOST.lstrip('/'))
  if not member.isfile():raise RuntimeError('Unexpected archived vhost shape')
  expected_vhost=archive.extractfile(member).read()
 if original_vhost!=expected_vhost:raise RuntimeError('Vhost changed since domain snapshot')
 vhost,count=re.subn(rb'(ServerName\s+)'+re.escape(OLD.encode()),lambda m:m.group(1)+NEW.encode(),original_vhost)
 if count!=2:raise RuntimeError('Unexpected vhost names')
 vhost,count=re.subn(rb'(ServerAlias\s+)localhost',lambda m:m.group(1)+OLD.encode()+b' localhost',vhost)
 if count!=2:raise RuntimeError('Unexpected vhost aliases')
 old_cert=b'/etc/letsencrypt/live/'+OLD.encode()+b'/'
 if vhost.count(old_cert)!=2:raise RuntimeError('Unexpected certificate paths')
 vhost=vhost.replace(old_cert,b'/etc/letsencrypt/live/divinemedia/')
 info=docker(web,'openssl','x509','-in','/etc/letsencrypt/live/divinemedia/fullchain.pem','-noout','-ext','subjectAltName').stdout
 if b'DNS:'+NEW.encode() not in info or b'DNS:'+OLD.encode() not in info:raise RuntimeError('Dual-host certificate missing')
 plan={'before':{n:digest(d) for n,d in originals.items()},'after':{n:digest(d) for n,d in changes.items()},'vhost_before':digest(original_vhost),'vhost_after':digest(vhost),'domains':[OLD,NEW]}
 if not apply:return plan
 state.mkdir(mode=0o700,parents=True,exist_ok=False)
 for name,data in originals.items():
  dest=state/'files'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 (state/'vhost-before.conf').write_bytes(original_vhost);(state/'plan.json').write_text(json.dumps(plan,indent=2))
 written=[];vhost_written=False
 try:
  write_vhost(web,vhost);vhost_written=True;apache_reload(web)
  for name,data in changes.items():atomic(root/name,data);written.append(name)
  for name in [*CONFIGS,'divine-entrance/landing.php','divine-entrance/login-theme.php','divine-creator/theme.php']:
   runtime=name.replace('.compose/videos/','videos/').replace('.compose/encoder/','Encoder/')
   docker(web,'php','-l','/var/www/html/AVideo/'+runtime)
 except Exception:
  for name in written:
   if digest((root/name).read_bytes())!=plan['after'][name]:raise RuntimeError('Concurrent edit prevents automatic restoration')
   atomic(root/name,originals[name])
  if vhost_written:
   if digest(docker(web,'cat',VHOST).stdout)!=plan['vhost_after']:raise RuntimeError('Concurrent vhost edit prevents automatic restoration')
   write_vhost(web,original_vhost);apache_reload(web)
  raise
 plan['rollback_state']=str(state);return plan
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='/srv/divinemedia/app');p.add_argument('--web',default='app-avideo-1');p.add_argument('--assets');p.add_argument('--snapshot');p.add_argument('--state');p.add_argument('--apply',action='store_true');p.add_argument('--rollback');a=p.parse_args();os.umask(0o077)
 if a.rollback:result=rollback(a.root,a.web,a.rollback)
 else:
  if not all([a.assets,a.snapshot,a.state]):p.error('--assets, --snapshot and --state required')
  result=install(a.root,a.web,a.assets,a.snapshot,a.state,a.apply)
 print(json.dumps(result,indent=2))
