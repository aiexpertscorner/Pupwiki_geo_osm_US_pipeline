#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
NS={'a':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
RELNS={'pr':'http://schemas.openxmlformats.org/package/2006/relationships'}
def col_index(ref):
    n=0
    for ch in re.match(r'([A-Z]+)', ref).group(1): n=n*26+ord(ch)-64
    return n-1
def read_xlsm(path):
    sheets={}
    with zipfile.ZipFile(path) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('a:si', NS):
                ss.append(''.join(t.text or '' for t in si.findall('.//a:t', NS)))
        wb=ET.fromstring(z.read('xl/workbook.xml')); rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        relmap={r.attrib['Id']:r.attrib['Target'] for r in rels.findall('pr:Relationship', RELNS)}
        for s in wb.findall('a:sheets/a:sheet', NS):
            name=s.attrib['name']; rid=s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            root=ET.fromstring(z.read('xl/'+relmap[rid])); rowmap={}
            for row in root.findall('a:sheetData/a:row', NS):
                vals={}; rn=int(row.attrib['r'])
                for c in row.findall('a:c', NS):
                    t=c.attrib.get('t'); v=c.find('a:v', NS); val=None
                    if v is not None:
                        raw=v.text or ''; val=ss[int(raw)] if t=='s' and raw.isdigit() else raw
                    elif t=='inlineStr': val=''.join(x.text or '' for x in c.findall('.//a:t', NS))
                    vals[col_index(c.attrib['r'])]=val
                rowmap[rn]=vals
            sheets[name]=rowmap
    return sheets
def slug(s): return re.sub(r'[^a-z0-9]+','-',(s or '').lower()).strip('-') or 'dataset'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--xlsm', default='geodatapupwiki.xlsm'); ap.add_argument('--out', default='config/datasets.from-xlsm.json'); ap.add_argument('--csv', default='config/datasets.from-xlsm.csv'); args=ap.parse_args()
    sheets=read_xlsm(Path(args.xlsm)); headers=[sheets['Geo Data Sources'][4].get(i) for i in range(10)]; rows=[]
    for r in range(5, 300):
        vals=[sheets['Geo Data Sources'].get(r,{}).get(i) for i in range(10)]
        if any(vals):
            item={h:(vals[i] if i < len(vals) else None) for i,h in enumerate(headers)}; item['source_row']=r; item['id']=f"xlsm-row-{r:02d}-{slug(item.get('Dataset'))}"; rows.append(item)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True); Path(args.out).write_text(json.dumps({'name':'PupWiki Geo Pipeline Dataset Manifest','created_from':str(args.xlsm),'datasets':rows}, indent=2, ensure_ascii=False), encoding='utf-8')
    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.csv).open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=headers+['source_row','id']); w.writeheader(); w.writerows(rows)
    print(f'Wrote {len(rows)} rows')
if __name__ == '__main__': main()
