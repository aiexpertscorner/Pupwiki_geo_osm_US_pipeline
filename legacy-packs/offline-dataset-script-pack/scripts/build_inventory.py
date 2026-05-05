#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
def sha256(path, limit_mb=64):
    h=hashlib.sha256(); remaining=limit_mb*1024*1024
    with path.open('rb') as f:
        while remaining>0:
            chunk=f.read(min(1024*1024, remaining))
            if not chunk: break
            h.update(chunk); remaining-=len(chunk)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--full-hash', action='store_true'); args=ap.parse_args(); root=Path(args.root); items=[]
    for base in ['data-raw','data-work','data-build','public/data/places/v1']:
        b=root/base
        if not b.exists(): continue
        for p in b.rglob('*'):
            if p.is_file(): items.append({'path':str(p.relative_to(root)),'size_bytes':p.stat().st_size,'sha256_prefix':sha256(p, 1000000 if args.full_hash else 64)})
    out=root/'data-work/file-inventory.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding='utf-8'); print(f'Wrote {len(items)} files to {out}')
if __name__=='__main__': main()
