#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, zipfile
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest', default='config/datasets.generated.json'); ap.add_argument('--root', default='.'); args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8')); count=0
    for row in manifest.get('datasets',[]):
        for it in row.get('download_items',[]):
            src=Path(args.root)/it.get('destination','')
            if src.suffix.lower()!='.zip' or not src.exists(): continue
            dest=Path(args.root)/(it.get('extract_to') or str(src.parent/src.stem)); dest.mkdir(parents=True, exist_ok=True)
            print(f'Unpacking {src} -> {dest}')
            with zipfile.ZipFile(src) as z: z.extractall(dest)
            count+=1
    print(f'Unpacked {count} ZIP archive(s).')
if __name__=='__main__': main()
