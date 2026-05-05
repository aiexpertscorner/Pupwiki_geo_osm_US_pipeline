#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest', default='config/datasets.generated.json'); ap.add_argument('--root', default='.'); args=ap.parse_args(); root=Path(args.root)
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8')); paths=set(['data-raw','data-work','data-build/places/v1','public/data/places/v1','docs/sources'])
    for f in manifest.get('folder_plan',[]):
        if f.get('Folder'): paths.add(f['Folder'])
    for row in manifest.get('datasets',[]):
        rec=row.get('Recommended local path') or ''
        if rec and not rec.lower().startswith(('use ','not ')):
            p=Path(rec); paths.add(str(p if rec.endswith('/') else p.parent))
        for it in row.get('download_items',[]):
            p=Path(it['destination']); paths.add(str(p if str(p).endswith('/') else p.parent))
    for p in sorted(paths): (root/p).mkdir(parents=True, exist_ok=True)
    gi=root/'.gitignore'
    if not gi.exists(): gi.write_text('# PupWiki geo raw/generated data\ndata-raw/\ndata-work/\ndata-build/\n*.osm.pbf\n*.zip.part\n*.tmp\n.env\n', encoding='utf-8')
    print(f'Created/verified {len(paths)} directories under {root.resolve()}')
if __name__=='__main__': main()
