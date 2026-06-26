# -*- coding: utf-8 -*-
"""Strip 公文 boilerplate (受文者/地址/聯絡/正本…) from 10_函釋 notes, keeping 主旨+說明.
Run with --apply to write; default is dry-run."""
import sys, io, re, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_obsidian_vault import read_text, parse_frontmatter

DIR = Path(__file__).resolve().parent.parent / "10_函釋"

HEADER_LINE = re.compile(
    r'^\s*(檔\s*號|保存期限|係存年限|地\s*址|傳\s*真|聯\s*絡\s*人|聯絡電話|電\s*話|'
    r'電子(信箱|郵件|郵遞)|[Ee][-\s]?mail|承\s*辦\s*人|受\s*文\s*者|速\s*別|密\s*等|附\s*件|'
    r'發文日期|發文字號|裝\s*訂\s*線|抄\s*件|分\s*類)[^\n]*?[:：;][^\n]*$',
    re.M)
MINISTRY_FUNC = re.compile(r'^\s*#*\s*[一-鿿]{2,12}\s*(?:書\s*函|開會通知單|函|公告)\s*$', re.M)

def clean(text: str) -> str:
    m = re.search(r'^##\s*Page\b', text, re.M)
    if not m:
        return text  # no OCR page region (hand-authored / catalog) -> untouched
    head = text[:m.start()].rstrip()
    pages = text[m.start():]

    # 1) drop page markers
    pages = re.sub(r'^##\s*Page\s+\d+\s*$', '', pages, flags=re.M)
    # 2) strip everything before the formal 主旨 (handles glued OCR; normalises 主告→主旨)
    stripped = re.sub(r'(?s)^.*?主\s*[旨告曰㫖]\s*[：:；;]\s*', '主旨：', pages, count=1)
    had_subject = stripped != pages
    pages = stripped
    # 3) remove ONLY the 正本/副本/署名 distribution block, KEEPING any 附件 content
    #    that follows it (一覽表/流程說明/設置要點 etc. are substantive, not boilerplate).
    #    Anchor on a sentence/line-boundary 正本 to avoid a stray 正本 inside 說明.
    positions = [m.start() for m in re.finditer(r'正\s*本', pages)]
    cut = None
    for pos in positions:
        prev = pages[:pos].rstrip(' 　\t')
        if not (prev == '' or prev[-1] in '。」）)\n'):
            continue
        # treat as distribution only if 正本 has a colon, or a 副本: follows shortly
        if re.match(r'正\s*本\s*[：:]', pages[pos:pos+8]) or re.search(r'副\s*本\s*[：:]', pages[pos:pos+200]):
            cut = pos
    if cut is not None:
        after = pages[cut:]
        mb = re.search(r'副\s*本\s*[：:][^\n]*', after)          # block ends at 副本 line
        if mb:
            block_end = cut + mb.end()
            # absorb a trailing single 署名 / page-footer line right after 副本
            mtail = re.match(r'\n[^\n]{0,30}(?:部長|次長|署長|局長|第[一二三四五六七八九十百\d]+頁)[^\n]*',
                             pages[block_end:])
            if mtail:
                block_end += mtail.end()
        else:
            nl = pages.find('\n', cut)
            block_end = nl if nl != -1 else len(pages)
        pages = (pages[:cut].rstrip(' 　\t') + '\n' + pages[block_end:].lstrip('\n')).rstrip() + '\n'
    # 3b) remove each electronic-exchange recipient dump (公文電子交換 / 受文單位 列表).
    #     Bound it to the next 主旨 so bundled 含前函 letters that follow are kept.
    pages = re.sub(
        r'(?s)(電子交換受文單位|公文電子交換|電子交換文件|電子認證加值服務)\s*[：:].*?(?=主\s*旨\s*[：:]|\Z)',
        '', pages)
    # 3c) drop standalone meta markers / attachment legends
    pages = re.sub(r'^\s*[（(]?\s*抄本暨發文清單\s*[)）]?\s*$', '', pages, flags=re.M)
    pages = re.sub(r'^\s*[（(]?\s*[＊*]\s*代表有附件[^\n]*$', '', pages, flags=re.M)
    # 4) belt-and-suspenders: drop any surviving standalone header lines
    pages = HEADER_LINE.sub('', pages)
    # 4b) drop glued header lines (no 主旨 anchor): a line carrying >=2 "欄位：值" header
    #     fields is a run-together 公文 header; content lines never have that form.
    field = re.compile(r'(地\s*址|傳\s*真|聯\s*絡\s*人|聯絡電話|電\s*話|受\s*文\s*者|'
                       r'發文字號|發文日期|速\s*別|密\s*等|檔\s*號|保存年限|係存年限)\s*[：:]')
    pages = '\n'.join('' if len(field.findall(ln)) >= 2 else ln for ln in pages.split('\n'))
    # 5) drop ministry-函 header fragments ("教育部 書函" / "內政部兒童局 函" …)
    pages = MINISTRY_FUNC.sub('', pages)
    # 5b) lone 正本/副本 lines (e.g. block had no 副本, or 副本 without 正本) and page footers
    pages = re.sub(r'^\s*(?:正|副)\s*本\s*[：:][^\n]*$', '', pages, flags=re.M)
    pages = re.sub(r'^\s*第[一二三四五六七八九十百\d]+\s*頁[，、\s]*共[一二三四五六七八九十百\d]+\s*頁\s*$', '', pages, flags=re.M)
    # 6) noise: stray markdown '#', long dotted runs, punctuation-only / 裝訂線 lines
    pages = re.sub(r'^\s*#+\s*$', '', pages, flags=re.M)
    pages = re.sub(r'[.．・·]{3,}', '', pages)
    pages = re.sub(r'^[\s.．・·,，、:：;；─—_\-]{0,6}$', '', pages, flags=re.M)
    pages = re.sub(r'^\s*[裝訂線]\s*$', '', pages, flags=re.M)
    # 7) collapse blank lines / trailing spaces
    pages = re.sub(r'[ \t]+$', '', pages, flags=re.M)
    pages = re.sub(r'\n{3,}', '\n\n', pages).strip()

    return head + "\n\n" + pages + "\n"

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    ap.add_argument('--show', nargs='*', default=[]); args = ap.parse_args()
    changed = 0; skipped = 0; total_before = 0; total_after = 0; nosubj = []
    for md in sorted(DIR.glob('*.md')):
        raw = read_text(md)
        fm, _ = parse_frontmatter(raw)
        if str(fm.get('type')) == '函釋目錄':
            skipped += 1; continue
        new = clean(raw)
        if '## Page' not in raw:
            skipped += 1; continue
        if '主旨：' not in new and '主旨:' not in new:
            nosubj.append(md.name)
        total_before += len(raw); total_after += len(new)
        if new != raw:
            changed += 1
            if args.apply:
                md.write_text(new, encoding='utf-8', newline='\n')
        if md.name.replace('.md','') in args.show or md.name in args.show:
            print("="*30, md.name, "="*30)
            print("----- AFTER -----")
            print(new[new.find('OBSIDIAN:END'):][:1500] if 'OBSIDIAN:END' in new else new[:1500])
    print(f"\nchanged={changed} skipped={skipped} "
          f"chars {total_before}->{total_after} (-{total_before-total_after}, "
          f"{100*(total_before-total_after)/max(total_before,1):.1f}%)")
    print("files still without 主旨 after clean:", len(nosubj))
    for n in nosubj[:20]: print("   ", n)

if __name__ == '__main__':
    main()
