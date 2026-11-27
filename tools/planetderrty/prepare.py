#!/usr/bin/env python3
"""Build a private, local review library. Never uploads or changes source MP3s."""
import argparse, hashlib, json, pathlib, re, subprocess, xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('songs');p.add_argument('output');args=p.parse_args()
root=pathlib.Path(args.songs);out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
xml=(root/'flashmo_songs.xml').read_text(encoding='utf-8-sig');fixed=re.sub(r'&(?!#\d+;|#x[0-9a-fA-F]+;|amp;|lt;|gt;|quot;|apos;)','&amp;',xml)
rows=[dict(n.attrib) for n in ET.fromstring(fixed).findall('song')];byname={r['filename']:r for r in rows};ordered=[r['filename'] for r in rows];ordered.extend(p.name for p in sorted(root.glob('*.mp3')) if p.name not in ordered)
tracks=[]
for name in ordered:
 file=root/name
 if not file.is_file():continue
 probe=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(file)],capture_output=True,text=True)
 data=json.loads(probe.stdout or '{}');fmt=data.get('format',{});tags=fmt.get('tags',{});duration=float(fmt.get('duration') or 0);legacy=byname.get(name)
 warnings=[]
 if duration<30:warnings.append('Short source: check for incomplete audio before publishing.')
 if legacy and tags.get('title','').strip().casefold()!=legacy.get('track','').strip().casefold():warnings.append('Legacy XML title differs from embedded title; review legacy credits.')
 tracks.append(dict(id=hashlib.sha256(file.read_bytes()).hexdigest(),filename=name,src='original/songs/'+name,title=tags.get('title',file.stem).strip(),artist=tags.get('artist','Unknown artist').strip(),album=tags.get('album','').strip(),duration=duration,tags=tags,legacy=legacy,warnings=warnings,bytes=file.stat().st_size,streams=data.get('streams',[]),probeWarnings=probe.stderr.strip(),visibility='private',metadataSource='embedded-tags' if tags.get('title') else 'filename'))
result=dict(title='Planet Derrty',visibility='private',originalPlaylistCount=len(rows),trackCount=len(tracks),tracks=tracks)
(out/'tracks.json').write_text(json.dumps(result,indent=2));print(json.dumps({'tracks':len(tracks),'legacyOrder':len(rows),'shortSources':[t['filename'] for t in tracks if t['duration']<30],'bytes':sum(t['bytes'] for t in tracks)}))
