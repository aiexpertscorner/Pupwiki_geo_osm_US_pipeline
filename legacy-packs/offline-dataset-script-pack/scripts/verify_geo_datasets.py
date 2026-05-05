#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, zipfile, gzip
from pathlib import Path
def pm(p,w): return bool(set((p or '').replace('/',' ').split()) & w)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest', default='config/datasets.generated.json'); ap.add_argument('--root', default='.'); ap.add_argument('--priority', action='append', default=['P1']); ap.add_argument('--include-optional', action='store_true'); ap.add_argument('--include-large-osm', action='store_true'); args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8')); rows=[]
    for row in manifest.get('datasets',[]):
        if not pm(row.get('Priority',''), set(args.priority)): continue
        for it in row.get('download_items',[]):
            if it.get('kind')=='landing_page': continue
            if not it.get('default', True) and not args.include_optional: continue
            if it.get('large') and 'osm.pbf' in it.get('destination','') and not args.include_large_osm: continue
            p=Path(args.root)/it['destination']; status='missing'; detail=''
            if p.exists() and p.stat().st_size>0:
                status='ok'; detail=f'{p.stat().st_size} bytes'
                if p.suffix.lower()=='.zip':
                    try:
                        with zipfile.ZipFile(p) as z: bad=z.testzip()
                        status='ok_zip' if bad is None else 'bad_zip'; detail=detail if bad is None else f'bad member: {bad}'
                    except Exception as e: status='bad_zip'; detail=repr(e)
                elif p.name.endswith('.gz'):
                    try:
                        with gzip.open(p,'rb') as g: g.read(1024)
                        status='ok_gzip'
                    except Exception as e: status='bad_gzip'; detail=repr(e)
            rows.append({'status':status,'dataset':row.get('Dataset'),'path':str(p),'detail':detail})
    out=Path(args.root)/'data-work/verify-report.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
    summary={}
    for r in rows: summary[r['status']]=summary.get(r['status'],0)+1
    print('Verification summary:', summary); print(f'Wrote {out}')
if __name__=='__main__': main()
