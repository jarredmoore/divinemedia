#!/usr/bin/env python3
"""Brand the standalone authenticated Local Encoder launcher head, without invoking it."""
import hashlib,importlib.util,json,os,pathlib,shutil,subprocess,tarfile,uuid
ROOT=pathlib.Path('/srv/divinemedia/app');NAME='.compose/encoder/view/localEncoder.php'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def archive(path,items):
 with tarfile.open(path,'w:gz') as out:
  for p,n in items:out.add(p,arcname=n)
if __name__=='__main__':
 os.umask(0o077);previous=pathlib.Path('/srv/divinemedia/backups/route-css-93998cd0c0/recovery');plan=json.loads((previous/'plan.json').read_text());p=ROOT/NAME;original=p.read_bytes();marker=b'DM_ROUTE_SHELL_V1';assert marker not in original and original.lower().count(b'</head>')==1
 installer=module('routes','/srv/divinemedia/backups/routes-release-ac0a8476b73a/apply-route-shell.py');backup=module('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py')
 assert {n:sha(ROOT/n) for n in plan['after']}==plan['after'] and {n:sha(ROOT/'divine-shell'/n) for n in plan['assets']}==plan['assets']
 at=original.lower().index(b'</head>');addition=installer.hook(2);desired=original[:at]+addition+original[at:];assert desired.replace(addition,b'',1)==original
 subprocess.run(['docker','exec','-i','app-avideo-1','php','-l'],input=desired,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30)
 state=pathlib.Path('/srv/divinemedia/backups')/('encoder-shell-'+uuid.uuid4().hex[:10]);state.mkdir(mode=0o700);archive(state/'before.tar.gz',[(p,NAME),(previous,'previous-recovery')]);before=backup.off_vm(state/'before.tar.gz',state.name);report={'result':'pending','state':str(state),'before_backup':before,'native_launcher_not_executed':True,'no_restart_or_jobs':True}
 try:
  installer.atomic(p,desired,p.stat());recovery=state/'recovery';shutil.copytree(previous,recovery)
  dest=recovery/NAME;dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True);dest.write_bytes(original);plan['before'][NAME]=hashlib.sha256(original).hexdigest();plan['after'][NAME]=sha(p);(recovery/'plan.json').write_text(json.dumps(plan,indent=2))
  archive(state/'after.tar.gz',[(p,NAME),(recovery,'recovery')]);after=backup.off_vm(state/'after.tar.gz',state.name);report.update({'result':'pass','after_backup':after,'combined_rollback_snapshot':str(recovery),'changed_template':NAME,'head_insertion_only':True,'original_sha256':hashlib.sha256(original).hexdigest(),'final_sha256':sha(p)})
 except Exception as error:
  installer.atomic(p,original,p.stat());report.update({'result':'fail','rolled_back':True,'error_type':type(error).__name__})
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
