#!/usr/bin/env python3
"""Persist/test a scoped Apache certificate reload hook and back up active TLS."""
import hashlib,importlib.util,json,os,pathlib,subprocess
if __name__=='__main__':
 os.umask(0o077);source=pathlib.Path(__file__).parent/'hooks/divinemedia-apache-renew';data=source.read_bytes()
 target=pathlib.Path('/srv/divinemedia/app/.compose/letsencrypt/renewal-hooks/deploy/divinemedia-apache-renew')
 if target.exists() and target.read_bytes()!=data:raise RuntimeError('Refusing to overwrite an unowned renewal hook')
 target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o750)
 hook='/etc/letsencrypt/renewal-hooks/deploy/divinemedia-apache-renew'
 subprocess.run(['docker','exec','app-avideo-1','sh','-n',hook],capture_output=True,check=True)
 subprocess.run(['docker','exec','-e','RENEWED_LINEAGE=/etc/letsencrypt/live/divinemedia','app-avideo-1',hook],capture_output=True,check=True)
 snapshot=pathlib.Path(pathlib.Path('/srv/divinemedia/backups/.latest-domain-snapshot').read_text().strip())
 spec=importlib.util.spec_from_file_location('domain_backup',pathlib.Path(__file__).with_name('prepare-domain-certificate.py'));backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
 archive=snapshot/'runtime-active.tar.gz';backup.runtime_archive(archive);proof=backup.off_vm(archive,snapshot.name)
 report={'result':'pass','hook':str(target),'hook_sha256':hashlib.sha256(data).hexdigest(),'hook_test':'Apache config valid and graceful reload succeeds','active_tls_backup':proof}
 (snapshot/'renewal-hook-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
