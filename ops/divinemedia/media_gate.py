"""Small reversible Apache routing change for the single origin delivery boundary."""
import re
MARKER = '# DM_MEDIA_GATE_V1'
RULES = '''# DM_MEDIA_GATE_V1
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/[.]well-known/acme-challenge/[A-Za-z0-9_-]+$
RewriteRule (^|/)[.] - [F,END]
RewriteRule ^Encoder/videos(?:/|$) - [F,END,NC]
RewriteRule ^(?:videos/.*|divine-media/(?:assets/.*|session|logout)|view/(?:xsendfile|hls)[.]php|plugin/VideoHLS/downloadProtection[.]php)$ divine-delivery/media.php [END]
</IfModule>
'''
HEADERS = '''
# DM_MEDIA_GATE_V1
<LocationMatch "^/(?:divine-delivery/media[.]php|videos/|divine-media/|hls/live/|view/(?:xsendfile|hls)[.]php|plugin/VideoHLS/downloadProtection[.]php)">
    Header onsuccess unset Cache-Control
    Header onsuccess unset Expires
    Header always set Expires "0"
    Header always set Cache-Control "private, no-store, max-age=0"
    Header always set X-Content-Type-Options "nosniff"
    Header always unset Access-Control-Allow-Origin
    Header always unset Access-Control-Allow-Credentials
</LocationMatch>
'''
# Do not unset PHP's CORS headers on authorized responses. Root legacy rules may set '*'
# only on media extensions; the guard's rewritten script is PHP. Verify headers in rehearsal.
HEADERS = HEADERS.replace('    Header always unset Access-Control-Allow-Origin\n','').replace('    Header always unset Access-Control-Allow-Credentials\n','')
def root_rules(original: bytes) -> bytes:
    if MARKER.encode() in original: raise RuntimeError('Gate already installed; inspect before changing')
    return RULES.encode()+original

def vhost(original: bytes) -> bytes:
    text=original.decode()
    if MARKER in text: raise RuntimeError('Gate already installed; inspect before changing')
    # Native live proxy can occur in HTTP vhost while HTTPS inherits rewrite. Remove both.
    forward=r'^\s*ProxyPass(?:Reverse)?\s+"/hls/live/"[^\n]*\n'
    text,count=re.subn(forward,'\n',text,flags=re.M)
    if count not in (2,4): raise RuntimeError('Unexpected live proxy topology')
    # All public live requests must pass the same PHP guard; no direct live proxy survives.
    insertion='''
    # DM_MEDIA_GATE_V1
    RewriteEngine On
    RewriteRule ^/hls/live/.*$ /divine-delivery/media.php [END]
    XSendFilePath /HLS/live/
'''
    text,n=re.subn(r'</VirtualHost>',lambda m:insertion+HEADERS+'\n'+m[0],text,flags=re.I)
    if n!=2: raise RuntimeError('Expected HTTP and HTTPS vhosts')
    return text.encode()

def nginx_origin(original: bytes) -> bytes:
    """Close raw HLS HTTP delivery; Apache reads the shared HLS files after authorization."""
    text=original.decode()
    if MARKER in text:raise RuntimeError('Live guard already installed')
    for scope in ('live','audio'):
        pattern=re.compile(r'(?m)^\s*location\s+/'+scope+r'\s*\{')
        found=list(pattern.finditer(text))
        if len(found)!=1:raise RuntimeError('Unexpected live location topology')
        match=found[0];start=text.index('{',match.start());depth=1;i=start+1;quote=None;comment=False;escaped=False
        while i<len(text) and depth:
            char=text[i]
            if comment:
                if char=='\n':comment=False
            elif escaped:escaped=False
            elif char=='\\':escaped=True
            elif quote:
                if char==quote:quote=None
            elif char in ['"',"'"]:quote=char
            elif char=='#':comment=True
            elif char=='{':depth+=1
            elif char=='}':depth-=1
            i+=1
        if depth:raise RuntimeError('Unbalanced live location')
        replacement='\n                # DM_MEDIA_GATE_V1: delivery is served by the authorized Apache boundary.\n                location ^~ /'+scope+' { return 403; }'
        text=text[:match.start()]+replacement+text[i:]
    # RTMP remains an ingest protocol. External playback must not bypass HTTPS authorization.
    # Local native FFmpeg thumbnail/recording hooks retain their existing read access.
    play=re.findall(r'^\s*(?:allow|deny)\s+play\s+[^;]+;',text,re.M)
    if play:
        if any(not re.match(r'^\s*allow\s+play\s+all;',p)for p in play):raise RuntimeError('Unexpected RTMP play policy')
        text,n=re.subn(r'(^[ \t]*)allow\s+play\s+all;',lambda m:m[1]+'allow play 127.0.0.1;\n'+m[1]+'deny play all;',text,flags=re.M)
        if n!=3:raise RuntimeError('Expected server/live/audio playback scopes')
    else:
        text,n=re.subn(r'(^\s*listen\s+1935\s*;)',lambda m:m[0]+'\n                allow play 127.0.0.1;\n                deny play all;',text,flags=re.M)
        if n!=1:raise RuntimeError('Expected one RTMP ingest listener')
    return text.encode()
