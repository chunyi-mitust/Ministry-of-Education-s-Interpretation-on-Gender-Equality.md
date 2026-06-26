# -*- coding: utf-8 -*-
"""Crawl gender.edu.tw 函釋目錄, diff against the Obsidian DB, write a JSON map."""
import sys, io, os, re, ssl, json, time, urllib.request
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_obsidian_vault import normalize_reference_key, parse_frontmatter, read_text

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
BASE = 'https://www.gender.edu.tw/web/index.php/m3/m3_03_index'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=40, context=ctx).read().decode('utf-8','replace')

entries = {}  # norm_doc_no -> dict
for page in range(1, 25):
    url = BASE if page == 1 else f"{BASE}/{page}?k=&y=&m=&d=&w=&n="
    try:
        html = fetch(url)
    except Exception as e:
        print(f"PAGE {page} ERROR {e}"); continue
    rows = re.findall(r'<tr>(.*?)</tr>', html, re.S)
    cnt = 0
    for r in rows:
        if 'catalog' not in r: continue
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        if len(cells) < 4: continue
        def txt(c): return re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ', c)).strip()
        date = txt(cells[0]); zi = txt(cells[1]); hao = txt(cells[2]); subject = txt(cells[3])
        href = re.search(r'href="([^"]+\.pdf)"', cells[1])
        pdf = href.group(1) if href else ''
        if not (zi and hao): continue
        doc_no = f"{zi}字第{hao}號"
        key = normalize_reference_key(doc_no)
        entries[key] = {"doc_no":doc_no, "zi":zi, "hao":hao, "date":date, "subject":subject, "pdf":pdf, "page":page}
        cnt += 1
    print(f"page {page}: {cnt} entries (total {len(entries)})")
    time.sleep(0.3)

# DB doc_no set
DB = Path(__file__).resolve().parent.parent / "10_函釋"
db_keys = {}
for md in DB.glob("*.md"):
    fm, _ = parse_frontmatter(read_text(md))
    dn = fm.get("doc_no")
    if dn:
        db_keys[normalize_reference_key(str(dn))] = md.name

catalog_not_db = {k:v for k,v in entries.items() if k not in db_keys}
db_not_catalog = {k:v for k,v in db_keys.items() if k not in entries}

print("\n=== SUMMARY ===")
print("catalog entries:", len(entries))
print("db doc_no:", len(db_keys))
print("catalog NOT in db:", len(catalog_not_db))
print("db NOT in catalog:", len(db_not_catalog))

out = {"entries":entries, "catalog_not_db":catalog_not_db, "db_not_catalog":db_not_catalog}
with open("catalog_map.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n--- catalog NOT in db (collectible gaps) ---")
for k,v in sorted(catalog_not_db.items(), key=lambda x:x[1]['page']):
    print(f"  {v['doc_no']}  | {v['date']} | {v['subject'][:30]}")
