import os,json,tarfile,hashlib,subprocess,time,tempfile,shutil,uuid,sys,urllib.parse,re
source=open('/srv/divinemedia/backups/.latest-roundtrip-backup').read().strip()
manifest=json.load(open(source+'/manifest.json'))
for row in manifest['files']:
 h=hashlib.sha256()
 with open(source+'/'+row['name'],'rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 assert h.hexdigest()==row['sha256'],'Source checksum mismatch'
prefix='dm-rehearsal-'+uuid.uuid4().hex[:10];network=prefix+'-net';containers=[]
scratch=tempfile.mkdtemp(prefix='rehearsal-',dir='/srv/divinemedia/backups');os.chmod(scratch,0o700)
def run(args,data=None,check=True):
 return subprocess.run(args,input=data,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check,timeout=240)
def docker(*args,**kwargs):return run(['docker',*args],**kwargs)
def recovery_filter(member,destination):
 item=tarfile.data_filter(member,destination)
 if item is None:return None
 return item.replace(uid=member.uid,gid=member.gid,mode=(member.mode & 0o777) if member.isfile() or member.isdir() else None)
phase='initialization'
report={'source':'off-VM downloaded copy','source_hashes_verified':True,'media_count':manifest['media_count'],'databases':[]}
try:
 phase='verify-image-recovery-source'
 image_manifest=json.load(open(source+'/images-manifest.json'))
 for row in image_manifest['files']:
  h=hashlib.sha256()
  with open(source+'/'+row['name'],'rb') as f:
   for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
  assert h.hexdigest()==row['sha256'],'Image archive checksum mismatch'
 report['recovery_images_verified']=image_manifest['image_count']
 phase='extract-application'
 runtime_manifest=json.load(open(source+'/runtime-manifest.json'))
 for row in runtime_manifest['files']:
  h=hashlib.sha256(open(source+'/'+row['name'],'rb').read()).hexdigest()
  assert h==row['sha256'],'Runtime source checksum mismatch'
 with tarfile.open(source+'/web-runtime-config.tar.gz','r:gz') as archive:archive.extractall(scratch+'/runtime',filter=recovery_filter)
 with tarfile.open(source+'/application.tar.gz','r:gz') as archive:archive.extractall(scratch,filter=recovery_filter)
 app=scratch+'/app';media=app+'/.compose/videos'
 recovered=json.load(open(source+'/media-after.json'))
 for row in recovered:
  p=os.path.join(media,row['path']);h=hashlib.sha256()
  with open(p,'rb') as f:
   for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
  assert h.hexdigest()==row['sha256'],'Restored media mismatch'
 report['restored_media_hashes_verified']=len(recovered)
 metadata=json.load(open(source+'/container-recovery-metadata.json'))
 byname={r['Name'].lstrip('/'):r for r in metadata}
 phase='create-isolated-network'
 docker('network','create','--internal',network)
 for label,old,alias in [('avideo','app-database-1','database'),('encoder','app-database_encoder-1','database_encoder')]:
  phase='start-database-'+label
  record=byname[old];name=prefix+'-'+label;env=dict(x.split('=',1) for x in record['Config']['Env'] if '=' in x)
  args=['run','-d','--name',name,'--network',network,'--network-alias',alias,'--read-only','--memory','768m','--memory-swap','768m','--cpus','0.5','--pids-limit','128','--tmpfs','/var/lib/mysql:rw,size=512m','--tmpfs','/run/mysqld:rw,size=16m','--tmpfs','/tmp:rw,size=32m','--mount','type=bind,src='+source+'/'+label+'.sql.gz,dst=/backup.sql.gz,readonly','-e','MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1','-e','MYSQL_ALLOW_EMPTY_PASSWORD=yes','-e','MYSQL_ROOT_PASSWORD=','-e','MARIADB_ROOT_PASSWORD=',record['Image'],'mariadbd','--skip-name-resolve','--local-infile=0','--innodb-buffer-pool-size=64M','--performance-schema=OFF']
  for settings in record.get('NetworkSettings',{}).get('Networks',{}).values():
   for alias_value in settings.get('Aliases',[]) or []:
    if alias_value and alias_value!=old:args[1:1]=['--network-alias',alias_value]
  containers.append(name);docker(*args)
  for attempt in range(150):
   result=docker('exec',name,'sh','-c','[ "$(cat /proc/1/comm)" = mariadbd ] && mariadb-admin --protocol=socket -uroot ping',check=False)
   if result.returncode==0:break
   time.sleep(1)
  else:raise RuntimeError('Scratch database readiness timeout')
  phase='restore-database-'+label
  docker('exec',name,'sh','-c','gzip -dc /backup.sql.gz | mariadb --protocol=socket -uroot')
  docker('exec',name,'mariadb-check','--protocol=socket','-uroot','--check','--all-databases')
  db=env['MYSQL_DATABASE'];user=env['MYSQL_USER'];password=env['MYSQL_PASSWORD']
  esc=lambda s:s.replace("'","''")
  sql="SET sql_mode='NO_BACKSLASH_ESCAPES'; CREATE USER IF NOT EXISTS '"+esc(user)+"'@'%' IDENTIFIED BY '"+esc(password)+"'; GRANT ALL ON `"+db.replace('`','``')+"`.* TO '"+esc(user)+"'@'%';"
  phase='grant-scratch-app-user-'+label
  docker('exec','-i',name,'mariadb','--protocol=socket','-uroot',data=sql)
  count=docker('exec',name,'mariadb','--protocol=socket','-uroot','-NB','-e',"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='"+esc(db)+"';").stdout.strip()
  report['databases'].append({'label':label,'restored_tables':int(count),'table_checks':'pass'})
  if label=='avideo':
   count=docker('exec',name,'mariadb','--protocol=socket','-uroot','-NB',db,'-e','SELECT COUNT(*) FROM videos;').stdout.strip();report['restored_video_rows']=int(count)
 phase='stage-player-plugins'
 sys.path.insert(0,'/srv/divinemedia/backups/native-feature-source')
 import ui_plugins
 proposals=ui_plugins.inspect_sources(app)
 main=prefix+'-avideo'
 mainenv=dict(x.split('=',1) for x in byname['app-database-1']['Config']['Env'] if '=' in x)
 for plugin_name,meta in proposals.items():
  count=docker('exec',main,'mariadb','--protocol=socket','-uroot','-NB',mainenv['MYSQL_DATABASE'],'-e',"SELECT COUNT(*) FROM plugins WHERE name="+ui_plugins.sql_literal(plugin_name)+" OR uuid="+ui_plugins.sql_literal(meta['uuid'])+';').stdout.strip()
  if count!='0':raise RuntimeError('Unexpected existing utility plugin in stage')
  docker('exec','-i',main,'mariadb','--protocol=socket','-uroot',mainenv['MYSQL_DATABASE'],data=ui_plugins.insert_statement(plugin_name,meta))
 report['ui_plugin_source_hashes']={n:m['sha256'] for n,m in proposals.items()}
 report['player_plugins_staged']=list(proposals)
 phase='start-recovered-cache' 
 cache=prefix+'-cache';containers.append(cache)
 docker('run','-d','--name',cache,'--network',network,'--network-alias','memcached','--memory','64m','--memory-swap','64m','--cpus','0.25','--pids-limit','64',byname['app-memcached-1']['Image'],'memcached','-m','16')
 phase='start-recovered-web-runtime'
 web=prefix+'-web';containers.append(web);record=byname['app-avideo-1']
 envfile=scratch+'/web.env'
 with open(envfile,'w') as f:
  for value in record['Config']['Env']:
   assert '\n' not in value,'Unsupported multiline environment value'
   f.write(value+'\n')
 os.chmod(envfile,0o600)
 args=['run','--env-file',envfile,'-d','--name',web,'--network',network,'--memory','1g','--memory-swap','1g','--cpus','0.5','--pids-limit','128','--entrypoint','/bin/sh']
 for src,dst,readonly in [(app,'/var/www/html/AVideo',False),(media,'/var/www/html/AVideo/videos',False),(app+'/.compose/encoder','/var/www/html/AVideo/Encoder',False),(app+'/.compose/letsencrypt','/etc/letsencrypt',True),(scratch+'/runtime/etc/apache2','/etc/apache2',True),(scratch+'/runtime/etc/php','/etc/php',True),(scratch+'/runtime/etc/ssl','/etc/ssl',True)]:
  assert os.path.isdir(src),'Missing restored application directory'
  args+=['--mount','type=bind,src='+src+',dst='+dst+(',readonly' if readonly else '')]
 args += [record['Image'],'-c','apache2ctl -D FOREGROUND']
 docker(*args)
 time.sleep(3)
 phase='recovered-apache-config'
 result=docker('exec',web,'apache2ctl','-t');report['apache_config']='pass'
 # Use restored credentials inside the isolated network. Never print them.
 php='''$rows=json_decode(file_get_contents("/recovery-metadata.json"),true);foreach($rows as $r){if(!in_array($r["Name"],["/app-database-1","/app-database_encoder-1"]))continue;$e=[];foreach($r["Config"]["Env"] as $v){$p=explode("=",$v,2);$e[$p[0]]=$p[1]??"";}$host=$r["Name"]==="/app-database-1"?"database":"database_encoder";$db=new mysqli($host,$e["MYSQL_USER"],$e["MYSQL_PASSWORD"],$e["MYSQL_DATABASE"]);if($db->connect_errno)exit(2);echo "PASS recovered application runtime database connection\\n";}'''
 # Metadata is copied into scratch container only, then removed with it.
 docker('cp',source+'/container-recovery-metadata.json',web+':/recovery-metadata.json')
 phase='recovered-runtime-database-connections'
 docker('exec',web,'php','-r',php);report['application_runtime_db_connections']='pass'
 phase='isolated-web-http'
 status=docker('exec',web,'curl','--max-time','30','-sS','-o','/tmp/recovery-response.html','-w','%{http_code}','-H','Host: media.divinecreativegroup.com','http://127.0.0.1/').stdout.strip()
 report['isolated_http_status']=status
 if status in ('301','302','303','307','308'):
  phase='isolated-web-https'
  status=docker('exec',web,'curl','--max-time','30','--noproxy','media.divinecreativegroup.com','--resolve','media.divinecreativegroup.com:443:127.0.0.1','-sS','-o','/tmp/recovery-response.html','-w','%{http_code}','https://media.divinecreativegroup.com/').stdout.strip()
  report['isolated_https_status']=status
 if status not in ('200','302','303'):raise RuntimeError('Isolated HTTP smoke test failed, status '+status)
 phase='rendered-response-check'
 docker('exec',web,'php','-r','$s=file_get_contents("/tmp/recovery-response.html");if(strlen($s)<100||preg_match("/Fatal error|Parse error|database connection failed/i",$s))exit(2);')
 report['rendered_response_no_fatal_error']='pass'
 phase='restored-static-media-range'
 sample=next(r for r in recovered if r['path'].lower().endswith('.mp3'))
 https='isolated_https_status' in report
 curl=['exec',web,'curl','--max-time','30','-sS','-o','/dev/null','-w','%{http_code}','-H','Range: bytes=0-1023']
 if https:curl+=['--noproxy','media.divinecreativegroup.com','--resolve','media.divinecreativegroup.com:443:127.0.0.1']
 else:curl+=['-H','Host: media.divinecreativegroup.com']
 base='https://media.divinecreativegroup.com' if https else 'http://127.0.0.1'
 code=docker(*(curl+[base+'/videos/'+urllib.parse.quote(sample['path'],safe='/')])).stdout.strip()
 report['restored_media_range_status']=code
 if code!='206':raise RuntimeError('Restored static media range failed')
 assert report['restored_video_rows']==manifest['main_video_rows'],'Restored video count differs from backup manifest'
 phase='isolated-native-player-controls'
 endpoint=base+'/videoEmbed/1?autoplay=0&controls=1'
 args=['exec',web,'curl','--max-time','30','-fsS','--noproxy','media.divinecreativegroup.com','--resolve','media.divinecreativegroup.com:443:127.0.0.1',endpoint]
 html=docker(*args).stdout
 for marker in ['plugin/Hotkeys/listener.js','playerSeekForward']:
  if marker not in html:raise RuntimeError('Missing native utility marker: '+marker)
 if re.search(r'Fatal error|Parse error',html):raise RuntimeError('Native player rendering failed')
 report['native_player_utilities_rendered']=True
 report['native_startup_not_executed']=True
 report['result']='pass' 
except Exception as exc:
 report['result']='fail';report['error_type']=type(exc).__name__;report['failed_phase']=phase
 if phase.startswith('isolated-web'):
  log=docker('logs',prefix+'-web',check=False).stderr
  report['web_error_flags']={v:v.lower() in log.lower() for v in ['AH01276','AH00035','AH01630','Permission denied','client denied','Cannot serve directory','Fatal error','Uncaught','memcached','getaddrinfo','Connection refused','Access denied','failed to open stream','Failed opening required','Call to undefined function','mysqli_sql_exception']}
  with open(source+'/restore-private-http-log.txt','w') as f:f.write(log)
  try:
   rootlog=app+'/.compose/videos/avideo.log'
   if os.path.isfile(rootlog):
    with open(rootlog,errors='replace') as f:f.seek(max(0,os.path.getsize(rootlog)-20000));tail=f.read()
    report['app_error_flags']={v:v.lower() in tail.lower() for v in ['memcached','getaddrinfo','Connection refused','Access denied','Permission denied','configuration.php','Could not connect','does not exist','mysqli','Failed opening','Fatal error','Uncaught']}
   response=docker('exec',prefix+'-web','cat','/tmp/recovery-response.html',check=False).stdout
   report['response_error_flags']={v:v.lower() in response.lower() for v in ['database','error','denied','install','unavailable']}
  except Exception:pass
 if isinstance(exc,subprocess.CalledProcessError):
  report['command_return_code']=exc.returncode
  with open(source+'/restore-private-error.txt','w') as f:f.write(exc.stderr or '')
  if phase in ('start-recovered-web-runtime','recovered-apache-config'):
   log=docker('logs',prefix+'-web',check=False).stderr
   report['web_startup_flags']={v:v.lower() in log.lower() for v in ['Syntax error','does not exist','Permission denied','SSLCertificateFile','not defined','No such file']}
   with open(source+'/restore-private-web-startup.txt','w') as f:f.write(log)
 # Exception text or command output can contain SQL/configuration details: keep private.
finally:
 for name in reversed(containers):docker('rm','-fv',name,check=False)
 docker('network','rm',network,check=False)
 shutil.rmtree(scratch)
 leftovers=docker('ps','-a','--filter','name='+prefix,'--format','{{.Names}}').stdout.strip()
 report['scratch_network_removed']=docker('network','inspect',network,check=False).returncode!=0
 report['scratch_containers_removed']=not bool(leftovers)
 report['scratch_files_removed']=not os.path.exists(scratch)
 with open(source+'/restore-verification.json','w') as f:json.dump(report,f,indent=2)
 print(json.dumps(report),flush=True)
 if report['result']!='pass' or leftovers or not report['scratch_network_removed']:sys.exit(1)

open("/srv/divinemedia/backups/native-player-stage-report.json","w").write(json.dumps(report,indent=2))
