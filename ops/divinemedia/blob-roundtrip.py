import os,json,urllib.request,urllib.parse,http.client,hashlib,time,email.utils,sys
account='stdmbackup983066';container='verified-backups';host=account+'.blob.core.windows.net'
root=open('/srv/divinemedia/backups/.latest-verification-backup').read().strip()
supplement=any(flag in sys.argv for flag in ['--runtime','--images','--verification'])
manifest_name='verification-manifest.json' if '--verification' in sys.argv else ('images-manifest.json' if '--images' in sys.argv else ('runtime-manifest.json' if supplement else 'manifest.json'))
manifest=json.load(open(root+'/'+manifest_name));prefix=os.path.basename(root)
if not supplement:assert manifest['media_stable_during_backup'] and manifest['archived_media_hashes_verified']==manifest['media_count']
# Tokens stay in memory; use the VM identity, never keys or SAS URLs.
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def token():
 url='http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource='+urllib.parse.quote('https://storage.azure.com/',safe='')
 req=urllib.request.Request(url,headers={'Metadata':'true'})
 return json.load(opener.open(req,timeout=15))['access_token']
auth=token()
def request(method,name,source=None,dest=None,sha=None):
 path='/'+container+'/'+urllib.parse.quote(prefix+'/'+name,safe='/')
 for attempt in range(8):
  connection=http.client.HTTPSConnection(host,timeout=180)
  headers={'Authorization':'Bearer '+auth,'x-ms-version':'2023-11-03','x-ms-date':email.utils.formatdate(usegmt=True)}
  if source:
   headers.update({'Content-Length':str(os.path.getsize(source)),'x-ms-blob-type':'BlockBlob','Content-Type':'application/octet-stream','If-None-Match':'*'})
   if sha:headers['x-ms-meta-sha256']=sha
  if source and os.path.getsize(source)>4*1024**3:raise RuntimeError('Backup object exceeds this helper single-upload limit; use staged block upload')
  with open(source,'rb') if source else open(os.devnull,'rb') as body:
   connection.request(method,path,body=body if source else None,headers=headers)
   response=connection.getresponse()
   if response.status in (401,403,429,500,503):
    response.read();connection.close()
    if attempt<7:time.sleep(min(5*(attempt+1),30));continue
   if response.status not in ((201,) if method=='PUT' else (200,)):
    status=response.status;response.read();connection.close();raise RuntimeError('Blob '+method+' status '+str(status))
   if dest:
    h=hashlib.sha256()
    with open(dest,'wb') as f:
     while True:
      chunk=response.read(1048576)
      if not chunk:break
      f.write(chunk);h.update(chunk)
    connection.close();return h.hexdigest()
   response.read();connection.close();return
 raise RuntimeError('Blob request retry limit')
entries=manifest['files']+[{'name':manifest_name,'sha256':hashlib.sha256(open(root+'/'+manifest_name,'rb').read()).hexdigest(),'bytes':os.path.getsize(root+'/'+manifest_name)}]
for item in entries:
 request('PUT',item['name'],source=root+'/'+item['name'],sha=item['sha256'])
print('PASS off-VM upload:',len(entries),'objects',sum(x['bytes'] for x in entries),'bytes',flush=True)
dest='/srv/divinemedia/backups/roundtrip-'+prefix
os.makedirs(dest,mode=0o700,exist_ok=True)
for item in entries:
 digest=request('GET',item['name'],dest=dest+'/'+item['name'])
 if digest!=item['sha256']:raise RuntimeError('Downloaded object hash mismatch: '+item['name'])
print('PASS downloaded object SHA-256 checks:',len(entries),flush=True)
with open('/srv/divinemedia/backups/.latest-roundtrip-backup','w') as f:f.write(dest+'\n')
with open(root+('/off-vm-report-verification.json' if '--verification' in sys.argv else ('/off-vm-images-verification.json' if '--images' in sys.argv else ('/off-vm-runtime-verification.json' if supplement else '/off-vm-verification.json'))),'w') as f:json.dump({'account':account,'container':container,'prefix':prefix,'objects':len(entries),'bytes':sum(x['bytes'] for x in entries),'all_download_hashes_match':True,'roundtrip_path':dest},f,indent=2)
print('RESTORE_SOURCE',dest,flush=True)
