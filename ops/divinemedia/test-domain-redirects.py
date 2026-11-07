#!/usr/bin/env python3
"""Verify the vhost redirect delta in an internal-only Apache/PHP stub.
No production app/database mounts, published ports, credentials or upload jobs.
"""
import argparse,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,tarfile,tempfile,time,uuid

def run(*args,check=True):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check,timeout=60)
def docker(*args,**kw):return run('docker',*args,**kw)
def recovery_filter(member,destination):
 item=tarfile.data_filter(member,destination)
 return item.replace(uid=member.uid,gid=member.gid,mode=member.mode & 0o777 if member.isfile() or member.isdir() else None) if item else None
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--base-bundle',required=True);a=p.parse_args();os.umask(0o077)
 bundle=pathlib.Path(a.bundle);base=pathlib.Path(a.base_bundle);snapshot=pathlib.Path(pathlib.Path('/srv/divinemedia/backups/.latest-domain-snapshot').read_text().strip())
 report={'result':'pending','verification_basis':{'full_restore_release':base.name,'redirect_delta':'internal Apache/PHP stub'}}
 baseline=json.loads((base/'stage-report.json').read_text());assert baseline['result']=='pass' and baseline['rollback_reapply']=='pass'
 # The full restore proof remains applicable to all unchanged assets/settings code.
 unchanged=['domain_settings.py','apply-entrance.py','apply-creator.py','assets/divine-entrance/landing.php','assets/divine-entrance/login-theme.js','assets/divine-entrance/login-theme.php','assets/divine-creator/creator.js','assets/divine-creator/theme.php']
 for name in unchanged:assert (bundle/name).read_bytes()==(base/name).read_bytes(),'Unexpected source delta'
 spec=importlib.util.spec_from_file_location('domain_config',bundle/'apply-domain-config.py');domains=importlib.util.module_from_spec(spec);spec.loader.exec_module(domains)
 scratch=pathlib.Path(tempfile.mkdtemp(prefix='domain-http-test-',dir='/srv/divinemedia/backups'));scratch.chmod(0o700)
 prefix='dm-domain-http-'+uuid.uuid4().hex[:10];network=prefix+'-net';web=prefix+'-web';phase='extract-runtime'
 try:
  with tarfile.open(snapshot/'runtime-with-new-certificate.tar.gz') as archive:archive.extractall(scratch/'runtime',filter=recovery_filter)
  vhost=scratch/'runtime/etc/apache2/sites-enabled/000-default.conf';patched=domains.rewrite_vhost(vhost.read_bytes())
  # Replace every non-redirected request with a stub to prove method/body retention.
  needle=b'[R=302,L,NE,QSD]\n';fixture=b'    RewriteCond %{DOCUMENT_ROOT}%{REQUEST_URI} !-f\n    RewriteRule ^ /stub.php [END]\n'
  assert patched.count(needle)==2;vhost.write_bytes(patched.replace(needle,needle+fixture))
  app=scratch/'app';app.mkdir(mode=0o755);app.chmod(0o755)
  php=b'<?php header("Content-Type: application/json");echo json_encode(["method"=>$_SERVER["REQUEST_METHOD"],"uri"=>$_SERVER["REQUEST_URI"],"body"=>file_get_contents("php://input")]);'
  (app/'stub.php').write_bytes(php);(app/'stub.php').chmod(0o644)
  (app/'videos').mkdir(mode=0o755);(app/'videos').chmod(0o755);(app/'videos/sample.mp4').write_bytes(b'x'*2048);(app/'videos/sample.mp4').chmod(0o644)
  phase='start-internal-stub';docker('network','create','--internal',network)
  image=docker('inspect','--format','{{.Image}}','app-avideo-1').stdout.decode().strip()
  args=['run','-d','--name',web,'--network',network,'--memory','384m','--memory-swap','384m','--cpus','0.25','--pids-limit','128','--entrypoint','/bin/sh']
  for source,target in [(app,'/var/www/html/AVideo'),(scratch/'runtime/etc/apache2','/etc/apache2'),(scratch/'runtime/etc/letsencrypt','/etc/letsencrypt')]:args+=['--mount','type=bind,src='+str(source)+',dst='+target+',readonly']
  docker(*(args+[image,'-c','apache2ctl -D FOREGROUND']));time.sleep(3)
  def request(path,host='media.divinecreativegroup.com',post=False,partial=False):
   args=['exec',web,'curl','--max-time','20','--noproxy',host,'--resolve',host+':443:127.0.0.1','-sS','-D','/tmp/dm-headers','-o','/tmp/dm-body','-w','%{http_code}']
   if post:args+=['--data','example=fixture']
   if partial:args+=['-H','Range: bytes=0-127']
   status=docker(*(args+['https://'+host+path])).stdout.decode().strip();body=docker('exec',web,'cat','/tmp/dm-body').stdout;headers=docker('exec',web,'cat','/tmp/dm-headers').stdout.decode()
   return status,body,headers
  phase='canonical-entry-redirects'
  for path in ['/user','/upload','/Encoder/','/Encoder/view/index.php','/view/mini-upload-form/index.php']:
   status,_,headers=request(path);assert status=='302' and 'https://media.divinemedia.us'+path in headers,'Legacy entry redirect failed'
   assert request(path,'media.divinemedia.us')[0]=='200','Canonical host redirects unexpectedly'
  phase='credential-query-discard'
  status,_,headers=request('/Encoder/?user=fixture&pass=fixture');assert status=='302' and 'Location: https://media.divinemedia.us/Encoder/\r\n' in headers and 'fixture' not in headers,'Credential query forwarded'
  status,_,headers=request('/Encoder/?noNavbar=1');assert status=='302' and '?noNavbar=1' in headers,'Compact mode query lost'
  phase='post-and-callback-retention'
  for path in ['/user','/Encoder/','/view/mini-upload-form/upload.php','/Encoder/view/index_signin.json.php']:
   status,body,_=request(path,post=True);data=json.loads(body);assert status=='200' and data['method']=='POST' and data['body']=='example=fixture','POST was redirected or changed'
  status,body,_=request('/plugin/API/get.json.php?APIName=video');assert status=='200' and json.loads(body)['method']=='GET','Legacy API redirected'
  assert request('/videos/sample.mp4',partial=True)[0]=='206','Legacy static range changed'
  report.update(baseline);report.update({'result':'pass','legacy_auth_redirects':'302 to canonical host','credential_queries_forwarded':False,'compact_mode_preserved':True,'legacy_post_and_api_requests':'not redirected','legacy_static_range':'206','unchanged_source_files':len(unchanged),'verification_basis':{'full_restore_release':base.name,'redirect_delta':'internal Apache/PHP stub'}})
 except Exception as exc:
  report.update({'result':'fail','phase':phase,'error_type':type(exc).__name__})
  if isinstance(exc,AssertionError):report['assertion']=str(exc)
  (bundle/'redirect-private-error.txt').write_text(str(exc))
 finally:
  docker('rm','-fv',web,check=False);docker('network','rm',network,check=False);shutil.rmtree(scratch)
  report['redirect_scratch_removed']=not bool(docker('ps','-a','--filter','name='+prefix,'--format','{{.Names}}').stdout.strip())
 (bundle/'stage-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 if report['result']!='pass':raise SystemExit(1)
