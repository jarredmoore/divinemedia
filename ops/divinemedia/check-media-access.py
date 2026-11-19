#!/usr/bin/env python3
"""Read-only release gate. Private plans/cookies never appear in arguments or output."""
import argparse,json,pathlib,re,stat,subprocess,urllib.parse
REQUIRED={
 'public-video-guest','public-audio-guest','public-image-guest','public-document-guest','public-live-guest',
 'private-video-owner','private-video-owner-range','private-video-guest','private-video-other-user',
 'private-audio-owner','private-audio-guest','private-image-owner','private-image-guest',
 'private-document-owner','private-document-guest','private-hls-manifest-guest','private-hls-segment-guest',
 'private-live-owner','private-live-guest','private-after-logout','private-expired-token',
}
def private_file(name):
 p=pathlib.Path(name)
 if not p.is_file() or stat.S_IMODE(p.stat().st_mode)&0o077:raise ValueError('Plan and cookie files must be private (0600)')
 return p

def check(case):
 label=case['id']
 if not re.fullmatch(r'[a-z0-9-]{1,80}',label):raise ValueError('Invalid case label')
 u=urllib.parse.urlsplit(case['url'])
 if u.scheme!='https' or u.hostname not in ['divinemedia.us','media.divinemedia.us'] or u.username or u.password or u.port not in [None,443]:raise ValueError('Unsupported test origin')
 expected=case['expected'];denied=label.startswith('private-')and not label.endswith(('owner','owner-range'))
 if not isinstance(expected,list)or not expected or any(not isinstance(s,int)for s in expected):raise ValueError('Invalid expected statuses')
 if denied and not set(expected)<=set([401,403,404]):raise ValueError('Private denial cases must require 401, 403 or 404')
 if not denied and not set(expected)<=set([200,206]):raise ValueError('Authorized cases must require successful media access')
 if label=='private-video-owner-range' and expected!=[206]:raise ValueError('The range check must require HTTP 206')
 config=['url = '+json.dumps(case['url']),'silent','show-error','max-time = 15','output = "/dev/null"','write-out = "%{http_code}"']
 # A bounded byte request tests GET/range behavior without downloading complete media.
 config+=['range = "0-0"','max-filesize = 1048576']
 if case.get('cookieFile'):config+=['cookie = '+json.dumps(str(private_file(case['cookieFile']).resolve()))]
 if case.get('referer'):config+=['referer = '+json.dumps(case['referer'])]
 result=subprocess.run(['curl','--config','-'],input='\n'.join(config)+'\n',capture_output=True,text=True,timeout=20)
 try:status=int(result.stdout)
 except ValueError:status=0
 # Curl may refuse an oversized 200 response before reading it; status still proves access.
 return {'id':label,'status':status,'expected':expected,'pass':status in expected}

def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--report',required=True);args=p.parse_args()
 try:
  plan=json.loads(private_file(args.plan).read_text());cases=plan['cases'];ids=[x['id']for x in cases]
  if len(ids)!=len(set(ids)):raise ValueError('Duplicate case labels')
  missing=sorted(REQUIRED-set(ids));results=[check(c)for c in cases]
  report={'result':'pass'if not missing and all(r['pass']for r in results)else'blocked','missing_required_cases':missing,'checks':results,'read_only':True,'redirects_followed':False,'tls_verification':True,'urls_and_credentials_logged':False}
 except Exception as e:report={'result':'blocked','error_type':type(e).__name__,'message':'Check private plan permissions, test-case schema, and connectivity. No URL or credential details are logged.'}
 path=pathlib.Path(args.report);path.write_text(json.dumps(report,indent=2)+'\n');path.chmod(0o600);print(json.dumps(report));return 0 if report['result']=='pass'else 1
if __name__=='__main__':raise SystemExit(main())
