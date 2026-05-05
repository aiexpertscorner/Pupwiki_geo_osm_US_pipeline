#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
LOG_PATH=Path('data-work/download-log.jsonl')
def priority_match(row_priority, wanted): return bool(set((row_priority or '').replace('/',' ').split()) & wanted)
def expand_env_url(url):
    out=url; missing=[]
    for part in url.split('${')[1:]:
        key=part.split('}',1)[0]; val=os.environ.get(key)
        if not val: missing.append(key)
        else: out=out.replace('${'+key+'}', val)
    return out, missing
def selected_items(manifest, args):
    wanted=set(args.priority or ['P1']); items=[]
    for row in manifest.get('datasets',[]):
        if not args.all and not priority_match(row.get('Priority',''), wanted): continue
        if args.dataset and args.dataset.lower() not in (row.get('Dataset') or '').lower(): continue
        if args.group and args.group.lower() not in (row.get('Group') or '').lower(): continue
        for it in row.get('download_items',[]):
            if it.get('kind')=='landing_page' and not args.include_landing_pages: continue
            if not it.get('default', True) and not args.include_optional: continue
            if it.get('large') and not args.include_large_osm and 'osm.pbf' in it.get('destination',''): continue
            if 'state-level' in (it.get('notes') or '').lower() and not args.include_state_layers: continue
            if 'all states' in (it.get('notes') or '').lower() and not args.include_all_states: continue
            url, missing=expand_env_url(it['url'])
            if missing:
                print(f"SKIP env missing {missing}: {row.get('Dataset')} -> {it['url']}"); continue
            items.append((row,it,url))
    return items
def remote_ok(url, timeout=20):
    try:
        req=urllib.request.Request(url, method='HEAD', headers={'User-Agent':'PupWikiGeoDownloader/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r: return r.status < 400
    except Exception: return None
def download_one(job):
    row,it,url,root,dry,overwrite,verify=job; dest=Path(root)/it['destination']; dest.parent.mkdir(parents=True, exist_ok=True)
    if verify and remote_ok(url) is False: return {'status':'remote_error','dataset':row.get('Dataset'),'url':url,'dest':str(dest)}
    if dry: return {'status':'dry_run','dataset':row.get('Dataset'),'url':url,'dest':str(dest)}
    if dest.exists() and dest.stat().st_size>0 and not overwrite: return {'status':'exists','dataset':row.get('Dataset'),'url':url,'dest':str(dest),'bytes':dest.stat().st_size}
    tmp=dest.with_suffix(dest.suffix+'.part'); downloaded=tmp.stat().st_size if tmp.exists() else 0; headers={'User-Agent':'PupWikiGeoDownloader/1.0'}
    if downloaded: headers['Range']=f'bytes={downloaded}-'
    try:
        req=urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as r, tmp.open('ab' if downloaded else 'wb') as f:
            while True:
                chunk=r.read(1024*1024)
                if not chunk: break
                f.write(chunk)
        tmp.replace(dest); return {'status':'downloaded','dataset':row.get('Dataset'),'url':url,'dest':str(dest),'bytes':dest.stat().st_size}
    except urllib.error.HTTPError as e: return {'status':'http_error','dataset':row.get('Dataset'),'url':url,'dest':str(dest),'http_status':e.code,'error':str(e)}
    except Exception as e: return {'status':'error','dataset':row.get('Dataset'),'url':url,'dest':str(dest),'error':repr(e)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest', default='config/datasets.generated.json'); ap.add_argument('--root', default='.'); ap.add_argument('--priority', action='append'); ap.add_argument('--all', action='store_true'); ap.add_argument('--dataset'); ap.add_argument('--group'); ap.add_argument('--include-large-osm', action='store_true'); ap.add_argument('--include-optional', action='store_true'); ap.add_argument('--include-state-layers', action='store_true'); ap.add_argument('--include-all-states', action='store_true'); ap.add_argument('--include-landing-pages', action='store_true'); ap.add_argument('--verify-remote', action='store_true'); ap.add_argument('--overwrite', action='store_true'); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--workers', type=int, default=3); args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8')); todo=selected_items(manifest,args); print(f'Selected {len(todo)} download item(s).')
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True); jobs=[(r,i,u,args.root,args.dry_run,args.overwrite,args.verify_remote) for r,i,u in todo]
    with ThreadPoolExecutor(max_workers=max(1,args.workers)) as ex, LOG_PATH.open('a',encoding='utf-8') as log:
        for fut in as_completed([ex.submit(download_one,j) for j in jobs]):
            res=fut.result(); print(f"{res['status']:>14} | {res.get('dataset','')} | {res.get('dest','')}"); log.write(json.dumps(res, ensure_ascii=False)+'\n'); log.flush()
if __name__=='__main__': main()
