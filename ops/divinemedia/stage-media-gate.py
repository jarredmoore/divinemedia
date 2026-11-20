#!/usr/bin/env python3
"""Run only on the Azure VM. All writable app/data/session state is disposable."""
import base64,hashlib,importlib.util,json,os,pathlib,re,secrets,shutil,subprocess,tempfile,time,uuid
os.umask(0o077)
BUNDLE=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('d','/srv/divinemedia/backups/native-glass-source-2c76a8467059/deploy-native-glass.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
sp=importlib.util.spec_from_file_location('gate',BUNDLE/'media_gate.py');gate=importlib.util.module_from_spec(sp);sp.loader.exec_module(gate)
ROOT=d.ROOT;prefix='dm-gate-'+uuid.uuid4().hex[:10];scratch=pathlib.Path(tempfile.mkdtemp(prefix=prefix+'-',dir='/srv/divinemedia/backups'));network=prefix+'-net';containers=[];phase='init';report={'result':'pending','isolated':True};app=scratch/'app'
def run(*args,data=None,check=True):
 try:return subprocess.run(args,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check,timeout=240).stdout
 except subprocess.CalledProcessError as e:
  (BUNDLE/'failed-command.private.txt').write_bytes(e.stderr or b'');raise
def docker(*args,**kwargs):return run('docker',*args,**kwargs)
try:
 lease={n:d.sha(ROOT/n)for n in ['.htaccess','divine-api/index.php','divine-api/native.php','divine-api/creator.php','divine-api/encoder-worker.php']}
 lease['@vhost']=hashlib.sha256(docker('exec','app-avideo-1','cat','/etc/apache2/sites-enabled/000-default.conf')).hexdigest()
 lease['@nginx']=hashlib.sha256(docker('exec','app-live-1','cat','/usr/local/nginx/conf/nginx.conf')).hexdigest()
 (BUNDLE/'lease.json').write_text(json.dumps(lease))
 phase='copy-native-source'
 shutil.copytree(ROOT,app,symlinks=True,ignore=shutil.ignore_patterns('.compose','.git','node_modules'))
 (app/'.compose/videos').mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/'.compose/videos/configuration.php',app/'.compose/videos/configuration.php')
 for n in ['divine-api','divine-delivery']:
  dest=app/n
  if dest.exists():shutil.rmtree(dest)
  shutil.copytree(BUNDLE/n,dest);dest.chmod(0o755)
  for p in dest.glob('*.php'):p.chmod(0o644)
 # Native Encoder runtime uses the same local files; its database/session state is isolated too.
 encroot=app/'.compose/encoder';shutil.copytree(ROOT/'.compose/encoder',encroot,symlinks=True,ignore=shutil.ignore_patterns('videos','.git'))
 (encroot/'videos').mkdir(mode=0o777);(encroot/'videos').chmod(0o777)
 shutil.copy2(ROOT/'.compose/encoder/videos/configuration.php',encroot/'videos/configuration.php')
 (app/'.htaccess').write_bytes(gate.root_rules((ROOT/'.htaccess').read_bytes()))
 # No production mounts are writable from the rehearsal container.
 webmeta=json.loads(docker('inspect','app-avideo-1'))[0];dbmeta=json.loads(docker('inspect','app-database-1'))[0]
 dbvars=dict(v.split('=',1) for v in dbmeta['Config']['Env']if '='in v);dbname=dbvars['MYSQL_DATABASE']
 apache=scratch/'apache2';docker('cp','app-avideo-1:/etc/apache2',str(apache))
 vhost=apache/'sites-enabled/000-default.conf';vhost.write_bytes(gate.vhost(docker('exec','app-avideo-1','cat','/etc/apache2/sites-enabled/000-default.conf')))
 hls=scratch/'HLS';hls.mkdir(mode=0o755);hls.chmod(0o755)
 # Native-generated fixtures and grant files need access by Apache's www-data in this copy only.
 scratch.chmod(0o755);app.chmod(0o755);(app/'.compose').chmod(0o755);(app/'.compose/videos').chmod(0o777)
 phase='isolated-db-start'
 docker('network','create','--internal',network)
 database=prefix+'-db';containers.append(database)
 docker('run','-d','--name',database,'--network',network,'--network-alias','database','--memory','768m','--cpus','0.75','--tmpfs','/var/lib/mysql:rw,size=512m','--tmpfs','/run/mysqld:rw,size=16m','-e','MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1',dbmeta['Image'],'mariadbd','--skip-name-resolve','--innodb-buffer-pool-size=64M','--performance-schema=OFF')
 for _ in range(90):
  try:docker('exec',database,'mariadb-admin','--protocol=socket','-uroot','ping');break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Disposable DB did not start')
 phase='clone-db-readonly'
 dump=docker('exec','app-database-1','sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb-dump --user="$MYSQL_USER" --single-transaction --skip-lock-tables --databases "$MYSQL_DATABASE"')
 docker('exec','-i',database,'mariadb','--protocol=socket','-uroot',data=dump);del dump
 esc=lambda x:x.replace("'","''")
 grant="SET sql_mode='NO_BACKSLASH_ESCAPES'; CREATE USER '"+esc(dbvars['MYSQL_USER'])+"'@'%' IDENTIFIED BY '"+esc(dbvars['MYSQL_PASSWORD'])+"'; GRANT ALL ON `"+dbname.replace('`','``')+"`.* TO '"+esc(dbvars['MYSQL_USER'])+"'@'%';"
 docker('exec','-i',database,'mariadb','--protocol=socket','-uroot',data=grant.encode())
 def sql(q):return docker('exec','-i',database,'mariadb','--protocol=socket','-uroot','-NB',dbname,data=q.encode()).decode().strip()
 phase='isolated-encoder-db'
 encmeta=json.loads(docker('inspect','app-database_encoder-1'))[0];encvars=dict(v.split('=',1)for v in encmeta['Config']['Env']if '='in v)
 encdb=prefix+'-encoder-db';containers.append(encdb)
 docker('run','-d','--name',encdb,'--network',network,'--network-alias','database_encoder','--memory','512m','--cpus','0.5','--tmpfs','/var/lib/mysql:rw,size=256m','--tmpfs','/run/mysqld:rw,size=16m','-e','MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1',encmeta['Image'],'mariadbd','--skip-name-resolve','--innodb-buffer-pool-size=32M','--performance-schema=OFF')
 for _ in range(90):
  try:docker('exec',encdb,'mariadb-admin','--protocol=socket','-uroot','ping');break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Disposable Encoder DB did not start')
 encdump=docker('exec','app-database_encoder-1','sh','-c','export MYSQL_PWD="$MYSQL_PASSWORD"; exec mariadb-dump --user="$MYSQL_USER" --single-transaction --skip-lock-tables --databases "$MYSQL_DATABASE"')
 docker('exec','-i',encdb,'mariadb','--protocol=socket','-uroot',data=encdump);del encdump
 encgrant="SET sql_mode='NO_BACKSLASH_ESCAPES'; CREATE USER '"+esc(encvars['MYSQL_USER'])+"'@'%' IDENTIFIED BY '"+esc(encvars['MYSQL_PASSWORD'])+"'; GRANT ALL ON `"+encvars['MYSQL_DATABASE'].replace('`','``')+"`.* TO '"+esc(encvars['MYSQL_USER'])+"'@'%';"
 docker('exec','-i',encdb,'mariadb','--protocol=socket','-uroot',data=encgrant.encode())
 # Fixture permissions use native models; plugin settings stay identical to the current installation.
 cache=prefix+'-cache';containers.append(cache);cachemeta=json.loads(docker('inspect','app-memcached-1'))[0]
 docker('run','-d','--name',cache,'--network',network,'--network-alias','memcached','--memory','64m','--cpus','0.25',cachemeta['Image'],'memcached','-m','16')
 phase='isolated-apache-start'
 envfile=scratch/'web.env';envfile.write_text('\n'.join(webmeta['Config']['Env'])+'\n')
 web=prefix+'-web';containers.append(web)
 args=['run','-d','--name',web,'--network',network,'--network-alias','avideo','--add-host','media.divinemedia.us:127.0.0.1','--add-host','media.divinecreativegroup.com:127.0.0.1','--env-file',str(envfile),'--memory','1g','--cpus','1','--entrypoint','/bin/sh']
 mounts=[(app,'/var/www/html/AVideo',False),(app/'.compose/videos','/var/www/html/AVideo/videos',False),(apache,'/etc/apache2',False),(encroot,'/var/www/html/AVideo/Encoder',False),(hls,'/HLS',False)]
 for m in webmeta['Mounts']:
  target=m['Destination']
  if target.startswith(('/etc/letsencrypt','/etc/ssl','/etc/php')):mounts.append((pathlib.Path(m['Source']),target,True))
 for src,dst,ro in mounts:args+=['--mount','type=bind,src='+str(src)+',dst='+dst+(',readonly'if ro else'')]
 args += [webmeta['Image'],'-c','apache2ctl -D FOREGROUND'];docker(*args);time.sleep(3)
 docker('exec',web,'apache2ctl','-t')
 # Required XSendFile configuration is part of the actual Apache test, not a mocked transport.
 phase='isolated-live-origin'
 livemeta=json.loads(docker('inspect','app-live-1'))[0]
 nginx_bin=docker('exec','app-live-1','sh','-c',"for p in /proc/[0-9]*/comm; do if [ \"$(cat $p)\" = nginx ]; then readlink \"${p%/comm}/exe\"; break; fi; done").decode().strip()
 assert nginx_bin.startswith('/'),'No native nginx executable'
 raw_nginx=docker('exec','app-live-1','cat','/usr/local/nginx/conf/nginx.conf')
 assert not re.search(rb'^\s*exec_static\s',raw_nginx,re.M),'Unexpected nginx exec hook'
 guarded=gate.nginx_origin(raw_nginx);nginx_conf=scratch/'nginx.conf';nginx_conf.write_bytes(guarded)
 ssl=scratch/'live-ssl';docker('cp','app-live-1:/etc/apache2/ssl',str(ssl))
 live=prefix+'-live';containers.append(live)
 docker('run','-d','--name',live,'--network',network,'--network-alias','live','--memory','256m','--cpus','0.5','--entrypoint',nginx_bin,'--mount','type=bind,src='+str(nginx_conf)+',dst=/usr/local/nginx/conf/nginx.conf,readonly','--mount','type=bind,src='+str(ssl)+',dst=/etc/apache2/ssl,readonly','--mount','type=bind,src='+str(hls)+',dst=/HLS',livemeta['Image'],'-c','/usr/local/nginx/conf/nginx.conf','-g','daemon off;')
 docker('exec',live,nginx_bin,'-t','-c','/usr/local/nginx/conf/nginx.conf')
 phase='native-fixtures-and-access-tests'
 exec((BUNDLE/'tests.py.txt').read_text(),globals())
 report.update(result='pass',checks=checks,native_startup_invoked=False,production_records_modified=False)
except Exception as e:
 report['completed_checks']=globals().get('checks',{});report.update(result='fail',phase=phase,error_type=type(e).__name__,assertion=str(e)[:180]if isinstance(e,(AssertionError,RuntimeError))else None)
 if (app/'.compose/encoder/videos/avideo.log').exists():shutil.copyfile(app/'.compose/encoder/videos/avideo.log',BUNDLE/'encoder.private.log')
 if (app/'.compose/videos/avideo.log').exists():shutil.copyfile(app/'.compose/videos/avideo.log',BUNDLE/'native.private.log')
 if 'live'in globals():
  try:(BUNDLE/'nginx.private.log').write_bytes(subprocess.run(['docker','logs',live],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20).stdout)
  except Exception:pass
 # Diagnostics remain private in the bundle; never print cookies or native SQL/errors.
 if 'web'in globals():
  try:(BUNDLE/'apache-private.log').write_bytes(subprocess.run(['docker','logs',web],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20).stdout)
  except Exception:pass
finally:
 for c in reversed(containers):docker('rm','-f',c,check=False)
 docker('network','rm',network,check=False)
 shutil.rmtree(scratch)
 (BUNDLE/'stage-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
