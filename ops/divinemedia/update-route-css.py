#!/usr/bin/env python3
"""Publish a validated CSS-only refinement with a cache-version bump and combined rollback."""
import argparse,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,tarfile,uuid
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def archive(path,items):
 with tarfile.open(path,'w:gz') as out:
  for src,name in items:out.add(src,arcname=name)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--initial-snapshot',required=True);p.add_argument('--assets',required=True);p.add_argument('--installer',required=True);a=p.parse_args();os.umask(0o077)
 root=pathlib.Path(a.root);initial=pathlib.Path(a.initial_snapshot);assets=pathlib.Path(a.assets);target=root/'divine-shell';installer=module('routes',a.installer);backup=module('backup','/srv/divinemedia/backups/domain-bootstrap-source/prepare-domain-certificate.py');old=json.loads((initial/'plan.json').read_text())
 assert {n:digest(root/n) for n in old['after']}==old['after'];assert {n:digest(target/n) for n in old['assets']}==old['assets'];assert {p.name for p in assets.iterdir()}==set(old['assets'])
 for n in set(old['assets'])-{'head.php','shell.css'}:assert digest(assets/n)==old['assets'][n]
 previous={n:(target/n).read_bytes() for n in ['head.php','shell.css']};desired={n:(assets/n).read_bytes() for n in previous};assert desired['head.php'].replace(b'33-routes-2',b'33-routes-1')==previous['head.php'],'Only the cache version may change in the head'
 subprocess.run(['docker','exec','-i','app-avideo-1','php','-l'],input=desired['head.php'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30)
 state=pathlib.Path('/srv/divinemedia/backups')/('route-css-'+uuid.uuid4().hex[:10]);state.mkdir(mode=0o700);archive(state/'before.tar.gz',[(target/n,n) for n in previous]+[(initial/'plan.json','initial-plan.json')]);before=backup.off_vm(state/'before.tar.gz',state.name)
 report={'result':'pending','state':str(state),'before_backup':before,'native_templates_unchanged':True,'no_restart_or_jobs':True}
 try:
  for n,data in desired.items():installer.atomic(target/n,data,(target/n).stat())
  recovery=state/'recovery';recovery.mkdir(mode=0o700)
  for n,h in old['before'].items():
   assert digest(initial/n)==h;dest=recovery/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(initial/n,dest)
  effective={**old,'assets':{n:digest(target/n) for n in old['assets']}};(recovery/'plan.json').write_text(json.dumps(effective,indent=2));assert {n:digest(root/n) for n in old['after']}==old['after']
  archive(state/'after.tar.gz',[(target,'divine-shell'),(recovery,'recovery')]);after=backup.off_vm(state/'after.tar.gz',state.name)
  report.update({'result':'pass','after_backup':after,'combined_rollback_snapshot':str(recovery),'changed_assets':['head.php cache version only','shell.css'],'final_assets':effective['assets']})
 except Exception as error:
  for n,data in previous.items():installer.atomic(target/n,data,(target/n).stat())
  report.update({'result':'fail','rolled_back':True,'error_type':type(error).__name__})
 (state/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));raise SystemExit(0 if report['result']=='pass' else 1)
