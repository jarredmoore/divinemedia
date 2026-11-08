#!/usr/bin/env python3
"""Snapshot the backend off-VM, then issue an additive dual-host certificate.
Run on the Azure host. Never print runtime configuration, tokens or private keys.
Does not change active vhosts, application base URLs, databases or media.
"""
import datetime,hashlib,http.client,json,os,pathlib,re,shutil,subprocess,tarfile,urllib.parse,urllib.request,uuid
ROOT=pathlib.Path('/srv/divinemedia/app')
BACKUPS=pathlib.Path('/srv/divinemedia/backups')
WEB='app-avideo-1'
OLD='media.divinecreativegroup.com'
NEW='media.divinemedia.us'
CERT='divinemedia'

def run(*args,**kw):
 return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=240,**kw)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def off_vm(path,prefix):
 # VM managed identity, in-memory access token, private existing backup container.
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 url='http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource='+urllib.parse.quote('https://storage.azure.com/',safe='')
 token=json.load(opener.open(urllib.request.Request(url,headers={'Metadata':'true'}),timeout=20))['access_token']
 blob='/verified-backups/'+urllib.parse.quote(prefix+'/'+path.name,safe='/')
 headers={'Authorization':'Bearer '+token,'x-ms-version':'2023-11-03'}
 conn=http.client.HTTPSConnection('stdmbackup983066.blob.core.windows.net',timeout=120)
 data=path.read_bytes();conn.request('PUT',blob,body=data,headers={**headers,'x-ms-blob-type':'BlockBlob','If-None-Match':'*','Content-Length':str(len(data)),'x-ms-meta-sha256':sha(path)})
 res=conn.getresponse();status=res.status;res.read();conn.close()
 if status!=201:raise RuntimeError('Private backup upload failed')
 conn=http.client.HTTPSConnection('stdmbackup983066.blob.core.windows.net',timeout=120);conn.request('GET',blob,headers=headers);res=conn.getresponse();digest=hashlib.sha256(res.read()).hexdigest();status=res.status;conn.close()
 if status!=200 or digest!=sha(path):raise RuntimeError('Private backup roundtrip hash mismatch')
 return {'name':path.name,'sha256':digest,'bytes':len(data),'roundtrip_verified':True}
def runtime_archive(path):
 with path.open('wb') as out:
  subprocess.run(['docker','exec',WEB,'tar','-czf','-','/etc/apache2','/etc/letsencrypt'],stdout=out,stderr=subprocess.PIPE,check=True,timeout=90)
 path.chmod(0o600)

if __name__=='__main__':
 os.umask(0o077)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
 snapshot=BACKUPS/('domains-'+stamp);snapshot.mkdir(mode=0o700)
 report={'snapshot':str(snapshot),'phase':'snapshot','result':'pending','off_vm':[]}
 try:
  names=['.compose/videos/configuration.php','.compose/encoder/videos/configuration.php']
  for module in ['divine-entrance','divine-creator']:
   names.extend(str(p.relative_to(ROOT)) for p in (ROOT/module).iterdir() if p.is_file())
  before={}
  for name in names:
   source=ROOT/name;dest=snapshot/'files'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);before[name]=sha(source)
  (snapshot/'before.json').write_text(json.dumps(before,indent=2))
  runtime_archive(snapshot/'runtime-before.tar.gz')
  with tarfile.open(snapshot/'host-files-before.tar.gz','w:gz') as archive:archive.add(snapshot/'files',arcname='files');archive.add(snapshot/'before.json',arcname='before.json')
  report['phase']='off-vm-snapshot'
  for name in ['runtime-before.tar.gz','host-files-before.tar.gz']:report['off_vm'].append(off_vm(snapshot/name,snapshot.name))
  report['phase']='certificate-issuance'
  renewal=run('docker','exec',WEB,'cat','/etc/letsencrypt/renewal/'+OLD+'.conf').stdout.decode()
  account=re.search(r'^account\s*=\s*([a-zA-Z0-9]+)',renewal,re.M).group(1)
  args=['docker','exec',WEB,'certbot','certonly','--webroot','-w','/var/www/html/AVideo','--cert-name',CERT,'-d',OLD,'-d',NEW,'--non-interactive','--agree-tos','--account',account]
  result=subprocess.run(args,capture_output=True,timeout=180)
  (snapshot/'certbot-private.log').write_bytes(result.stdout+result.stderr)
  if result.returncode:raise RuntimeError('Certificate issuer did not complete; private log retained')
  cert_path='/etc/letsencrypt/live/'+CERT+'/fullchain.pem'
  info=run('docker','exec',WEB,'openssl','x509','-in',cert_path,'-noout','-dates','-ext','subjectAltName').stdout.decode()
  assert 'DNS:'+NEW in info and 'DNS:'+OLD in info,'Certificate missing required names'
  report['certificate']={'name':CERT,'domains':[OLD,NEW],'expires':re.search(r'notAfter=(.*)',info).group(1)}
  report['phase']='off-vm-certificate'
  runtime_archive(snapshot/'runtime-with-new-certificate.tar.gz');report['off_vm'].append(off_vm(snapshot/'runtime-with-new-certificate.tar.gz',snapshot.name))
  (BACKUPS/'.latest-domain-snapshot').write_text(str(snapshot)+'\n')
  report.update({'result':'pass','phase':'complete','active_configuration_unchanged':True})
 except Exception as exc:
  report.update({'result':'fail','error_type':type(exc).__name__})
  (snapshot/'private-error.txt').write_text(str(exc))
 (snapshot/'certificate-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 if report['result']!='pass':raise SystemExit(1)
