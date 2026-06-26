from __future__ import annotations

import re
import shutil
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
DIR_OVERVIEW = ROOT / "00_總覽"
DIR_INTERPRETATIONS = ROOT / "10_函釋"
DIR_LAWS = ROOT / "20_法規"
DIR_LOCAL_RULES = ROOT / "30_校內規定"
DIR_CONCEPTS = ROOT / "40_概念"
DIR_ATTACHMENTS = ROOT / "90_附件"
DIR_PDFS = DIR_ATTACHMENTS / "PDF"
DIR_TEXT_SOURCES = DIR_ATTACHMENTS / "文字來源"
DIR_MAINTENANCE = ROOT / "99_維護"

TODAY = datetime.now().strftime("%Y-%m-%d")
OBSIDIAN_BEGIN = "<!-- OBSIDIAN:BEGIN -->"
OBSIDIAN_END = "<!-- OBSIDIAN:END -->"
RELATED_BEGIN = "<!-- RELATED:BEGIN -->"
RELATED_END = "<!-- RELATED:END -->"
INTERPRETATION_REFS_BEGIN = "<!-- INTERPRETATION-REFERENCES:BEGIN -->"
INTERPRETATION_REFS_END = "<!-- INTERPRETATION-REFERENCES:END -->"


@dataclass(frozen=True)
class Concept:
    name: str
    aliases: tuple[str, ...] = ()
    kind: str = "concept"
    summary: str = ""
    related: tuple[str, ...] = ()

    @property
    def terms(self) -> tuple[str, ...]:
        seen = []
        for term in (self.name, *self.aliases):
            if term and term not in seen:
                seen.append(term)
        return tuple(seen)


CONCEPTS: tuple[Concept, ...] = (
    Concept("性別平等教育法", ("性平法", "性平教育法"), "law", "校園性平體系的母法，規範性別平等教育與校園性別事件處理。"),
    Concept("性別平等教育法施行細則", ("性平法施行細則",), "law", "性別平等教育法的施行細部規範。"),
    Concept(
        "校園性別事件防治準則",
        (
            "防治準則",
            "校園性侵害性騷擾或性霸凌防治準則",
            "校園性侵害性騷擾及性霸凌防治準則",
            "校園性侵害、性騷擾或性霸凌防治準則",
        ),
        "law",
        "校園性別事件受理、調查、通知、移送與防治教育的核心準則。",
    ),
    Concept("性別平等工作法", ("性別工作平等法", "性工法"), "law", "職場性別平等與性騷擾防治的法律。"),
    Concept("性騷擾防治法", ("性騷法",), "law", "非屬性平法或工作法適用範圍時常見的性騷擾防治法律。"),
    Concept("性騷擾防治法施行細則", (), "law", "性騷擾防治法的施行細部規範。"),
    Concept("性騷擾防治準則", (), "law", "性騷擾防治相關作業準則。"),
    Concept("性侵害犯罪防治法", ("性侵法",), "law", "性侵害犯罪防治、通報與被害人保護相關法律。"),
    Concept("性侵害犯罪防治法施行細則", (), "law", "性侵害犯罪防治法的施行細部規範。"),
    Concept("跟蹤騷擾防制法", ("跟騷法",), "law", "跟蹤騷擾行為防制與保護命令相關法律。"),
    Concept("跟蹤騷擾防制法施行細則", (), "law", "跟蹤騷擾防制法的施行細部規範。"),
    Concept("兒童及少年福利與權益保障法", ("兒少法",), "law", "兒少保護、福利與權益保障法律。"),
    Concept("兒童及少年福利與權益保障法施行細則", (), "law", "兒少福利與權益保障法的施行細部規範。"),
    Concept("兒童及少年性剝削防制條例", ("兒少性剝削條例",), "law", "兒童及少年性剝削防制法律。"),
    Concept("教師法", (), "law", "教師聘任、解聘、不續聘、停聘與申訴救濟等事項的法律。"),
    Concept("教師法施行細則", (), "law", "教師法的施行細部規範。"),
    Concept("教育人員任用條例", (), "law", "教育人員任用資格與消極資格相關法律。"),
    Concept("行政程序法", (), "law", "行政程序、陳述意見、迴避、送達與行政處分等共通程序法。"),
    Concept("刑法", ("刑法第10條", "妨礙性自主罪章"), "law", "性侵害犯罪與性影像等刑事法概念的來源之一。"),
    Concept("專科以上學校兼任教師聘任辦法", ("兼任教師聘任辦法",), "law", "專科以上學校兼任教師聘任與資格管理規範。"),
    Concept(
        "學校校長及教職員工違反與性或性別有關之專業倫理防治指引",
        ("專業倫理防治指引",),
        "law",
        "校長與教職員工專業倫理防治規範。",
    ),
    Concept("校園性別事件", ("校園性侵害性騷擾或性霸凌事件", "校園性侵害、性騷擾或性霸凌事件", "校園相關性別事件"), summary="性平法下的校園性侵害、性騷擾、性霸凌及專業倫理事件總稱。"),
    Concept("性侵害", ("性侵害事件", "性侵害犯罪"), summary="校園性別事件類型之一，連結性侵害犯罪防治法與刑法概念。"),
    Concept("性騷擾", ("性騷擾事件",), summary="校園性別事件及其他性騷擾防治體系的核心類型。"),
    Concept("性霸凌", ("性霸凌事件",), summary="針對性別特徵、性別特質、性傾向或性別認同的貶抑、攻擊或威脅。"),
    Concept("數位網路性別暴力", ("數位性別暴力", "網路性別暴力"), summary="以數位或網路方式發生的性別暴力態樣。"),
    Concept("性影像", ("私密影像", "性私密影像"), summary="刑法與數位性別暴力中常見的影像或電磁紀錄概念。"),
    Concept("跟蹤騷擾", ("跟騷",), summary="反覆或持續違反意願之騷擾行為。"),
    Concept("專業倫理行為", ("與性或性別有關之專業倫理行為", "違反專業倫理", "專業倫理事件"), summary="校長或教職員工利用不對等權勢關係發展有違專業倫理的人際互動。"),
    Concept("親密關係", ("發展親密關係",), summary="專業倫理判斷中常見的關係型態。"),
    Concept("情節重大", ("情節重大判斷", "情節輕重判斷"), summary="懲處、解聘或不得聘任等結果的重要判斷門檻。"),
    Concept("併案調查", ("併案審議", "併案審議議處", "併案議處"), summary="同一行為人或多事件間合併調查、審議或議處的程序。"),
    Concept("事件管轄學校", ("管轄學校",), summary="依事件發生與身分關係負責受理調查的學校。"),
    Concept("議處權責學校", ("權責學校", "議處學校"), summary="負責終局議處或移送議處的學校或機關。"),
    Concept("主管機關", ("教育主管機關", "主管教育行政機關"), summary="性平法與相關教育法規中的中央、地方或所屬主管機關。"),
    Concept("管轄權", ("案件管轄", "管轄疑義"), summary="決定受理、調查、申復或救濟權責歸屬的概念。"),
    Concept("跨校事件", ("跨校案件", "跨校人員"), summary="涉及不同學校或跨校身分的校園性別事件。"),
    Concept("校長案件", ("校長案",), summary="行為人或當事人為校長時的調查、停職、申復與議處問題。"),
    Concept("調查程序", ("調查處理程序", "調查處理"), summary="校園性別事件受理後的調查與處理程序。"),
    Concept("調查小組", ("調查小組組成",), summary="性平會組成或委託的調查組織。"),
    Concept("調查報告", ("調查結果",), summary="調查事實、理由、建議及後續議處的主要書面文件。"),
    Concept("初審小組", ("初審",), summary="受理或程序初步審查相關小組。"),
    Concept("調查專業人員", ("調查專業人才庫", "專業調查人員"), summary="參與校園性別事件調查的專業人員。"),
    Concept("申請調查", ("申請人申請調查", "申請案"), summary="被害人、法定代理人或實際照顧者提出調查申請。"),
    Concept("檢舉", ("檢舉案", "檢舉人檢舉"), summary="非申請人向學校或主管機關提出校園性別事件線索。"),
    Concept("撤回申請", ("撤銷申請", "放棄申請調查", "切結"), summary="申請人欲撤回、放棄或以切結取代程序的問題。"),
    Concept("申復", ("申覆", "申復程序", "申復時點"), summary="性平法體系中特定處理結果的內部救濟程序。"),
    Concept("申訴", ("申訴程序", "教師申訴", "學生申訴"), summary="教師、學生或相關人員依法提出的申訴救濟。"),
    Concept("救濟程序", ("後續救濟", "行政救濟"), summary="申復、申訴、訴願或行政訴訟等救濟路徑。"),
    Concept("重為決定", ("重啟調查", "重新踐行程序"), summary="原處理結果被撤銷或需重新作成決定時的程序。"),
    Concept("閱卷", ("調閱資料", "資料調閱"), summary="當事人或相關機關請求閱覽卷證資料的問題。"),
    Concept("錄音錄影", ("錄音", "錄影"), summary="調查、訪談或會議中錄音錄影的程序與保密問題。"),
    Concept("保密義務", ("保密", "簽保密同意書", "保密同意書"), summary="校園性別事件處理過程中的資訊保密與法律責任。"),
    Concept("個資保護", ("個人資料", "個資", "身分資訊"), summary="當事人身分、卷證與資料提供時的個資保護問題。"),
    Concept("通報義務", ("通報", "通報處理"), summary="校園性別事件、兒少、性侵害或不適任人員等通報義務。"),
    Concept("校安通報", ("校安",), summary="教育體系校安事件通報。"),
    Concept("社政通報", ("社會局通報", "社政主管機關"), summary="涉及兒少、社福或社政主管機關的通報與函報。"),
    Concept("不適任教育人員通報", ("不適任教育人員", "不適任者"), summary="不適任教育人員通報、資訊蒐集與查詢。"),
    Concept("行為人", ("加害人",), summary="被指涉或經認定作成校園性別事件行為的人。"),
    Concept("被害人", ("受害人",), summary="受校園性別事件侵害或影響的人。"),
    Concept("申請人", (), summary="依法提出調查申請的人。"),
    Concept("檢舉人", (), summary="提出檢舉的人。"),
    Concept("法定代理人", (), summary="未成年人或受監護宣告者依法定代理之人。"),
    Concept("實際照顧者", (), summary="實際照顧學生或被害人的人。"),
    Concept("教職員工", ("校長或教職員工", "校長、教師、職員、工友"), summary="性平法中校長、教師、職員、工友及相關人員的統稱。"),
    Concept("軍訓教官", ("軍訓人員", "教官"), summary="軍訓教官涉及校園性別事件時的議處與救濟。"),
    Concept("教育實習", ("教育實習生", "師資生", "實習教師"), summary="教育實習者或師資生涉及事件時的身分與處理。"),
    Concept("校外實習", ("實習場域", "校外實習性騷擾"), summary="校外實習場域中的性騷擾或性別事件處理。"),
    Concept("推廣教育", ("進修推廣教育", "推廣教育學員"), summary="接受進修推廣教育者是否屬學生的問題。"),
    Concept("交換學生", (), summary="交換學生於性平法學生定義下的身分問題。"),
    Concept("學制轉銜", ("學制轉銜期間",), summary="學制轉銜期間未具學籍者的身分與管轄問題。"),
    Concept("學生定義", ("學生之定義", "學生身分"), summary="性平法或防治準則中學生身分範圍的認定。"),
    Concept("未成年人", ("未成年學生", "未滿14歲", "十八歲以下", "18歲以下"), summary="未成年人在申請、通報、行政罰與保護程序中的特殊問題。"),
    Concept("兒童及少年", ("兒少",), summary="兒少保護、通報及福利權益相關概念。"),
    Concept("懲處", ("議處", "懲戒", "獎懲", "處置"), summary="調查結果後依身分法規進行的處理。"),
    Concept("解聘", ("解聘處分",), summary="教師或教育人員聘任關係終止。"),
    Concept("不續聘", ("不續聘處分",), summary="教師或教育人員聘期屆滿後不再續聘。"),
    Concept("停聘", ("停止聘任",), summary="調查或議處期間暫停聘任相關措施。"),
    Concept("不得聘任", ("不得聘任、任用、進用或運用", "終身不得聘任", "不得任用", "不得進用", "不得運用"), summary="性平事件後續的人員任用限制。"),
    Concept("教師評審委員會", ("教評會",), summary="教師聘任、解聘、不續聘、停聘與部分懲處審議機制。"),
    Concept("教師申訴評議委員會", ("教申會",), summary="教師申訴救濟審議機制。"),
    Concept("學生申訴評議委員會", ("學生申評會",), summary="學生申訴救濟審議機制。"),
    Concept("性別平等教育委員會", ("性平會", "學校性平會"), summary="性平法下負責推動、調查與審議的重要委員會。"),
    Concept("性別平等教育", ("性平教育",), summary="促進性別地位實質平等、消除性別歧視的教育。"),
    Concept("性別認同", (), summary="個人對自我歸屬性別的認知及接受。"),
    Concept("性傾向", (), summary="性平法下多元性別差異的重要面向。"),
    Concept("性別特質", (), summary="性霸凌與性別歧視判斷中常見的概念。"),
    Concept("性別特徵", (), summary="性霸凌與性別歧視判斷中常見的概念。"),
    Concept("出席費", ("支領出席費",), summary="調查小組、跨校案件或委員出席費支給問題。"),
    Concept("公益判斷", ("涉及公益",), summary="事件是否涉及公益及資訊揭露、續行處理之判斷。"),
    Concept("合意案件", ("合意事件",), summary="當事人合意或未成年合意案件的處理問題。"),
    Concept("家內案件", ("家庭內事件",), summary="家庭內或非校園關係案件與性平法適用的界線。"),
    Concept("保護令", (), summary="保護令與校園事件通報、處理之關聯。"),
    Concept("法院判決", ("司法判決", "刑事判決"), summary="法院判決對校園性別事件調查、重啟或懲處的影響。"),
    Concept("行政罰", ("裁罰",), summary="行政處罰及處罰權時效問題。"),
    Concept("正當法律程序", ("法定程序", "程序保障"), summary="受理、調查、陳述意見與決定程序的基本要求。"),
    Concept("陳述意見", (), summary="行政程序與懲處程序中當事人陳述意見的權利。"),
    Concept("迴避", ("利益衝突",), summary="調查、審議或決定程序中的迴避問題。"),
    Concept("懷孕學生輔導", ("學生懷孕事件", "懷孕事件"), summary="學生懷孕事件之輔導與處理。"),
    Concept("服儀規定", ("服儀", "服裝儀容"), summary="服裝儀容規定與性別平等。"),
)

CONCEPT_BY_NAME = {concept.name: concept for concept in CONCEPTS}
LAW_NAMES = {concept.name for concept in CONCEPTS if concept.kind == "law"}


@dataclass
class Record:
    title: str
    path: Path
    kind: str
    number: int | None = None
    issued_date: str = ""
    roc_date: str = ""
    doc_no: str = ""
    subject: str = ""
    concepts: list[str] = field(default_factory=list)


def ensure_dirs() -> None:
    for path in (
        DIR_OVERVIEW,
        DIR_INTERPRETATIONS,
        DIR_LAWS,
        DIR_LOCAL_RULES,
        DIR_CONCEPTS,
        DIR_PDFS,
        DIR_TEXT_SOURCES,
        DIR_MAINTENANCE,
    ):
        path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Big5 is a common legacy encoding for Traditional Chinese files.
        return data.decode("cp950")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalize_cjk_compat(text: str) -> tuple[str, int]:
    changed = 0
    out: list[str] = []
    for ch in text:
        if "\uf900" <= ch <= "\ufaff":
            normalized = unicodedata.normalize("NFKC", ch)
            if normalized != ch:
                changed += 1
            out.append(normalized)
        else:
            out.append(ch)
    result = "".join(out)
    result = result.replace("\r\n", "\n").replace("\r", "\n").replace("\ufeff", "")
    result = result.replace("\x0c", "\n")
    result = re.sub(r"\.{20,}", "", result)
    return result, changed


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return {}, normalized
    marker = "\n---\n"
    end = normalized.find(marker, 4)
    if end == -1:
        return {}, normalized
    raw = normalized[4:end]
    body = normalized[end + len(marker) :]
    fm: dict[str, object] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            fm.setdefault(current_key, [])
            if isinstance(fm[current_key], list):
                fm[current_key].append(parse_scalar(line[4:].strip()))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            fm[key] = []
        else:
            fm[key] = parse_scalar(value)
    return fm, body


def parse_scalar(value: str) -> object:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def yaml_quote(value: object) -> str:
    if isinstance(value, int):
        return str(value)
    text = str(value)
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def dump_frontmatter(fm: dict[str, object]) -> str:
    preferred = [
        "title",
        "type",
        "doc_no",
        "issued_date",
        "roc_date",
        "subject",
        "source_pdf",
        "source_attachment",
        "source_text",
        "source_text_attachment",
        "source_url",
        "listing_page",
        "listing_text",
        "page_count",
        "text_chars",
        "image_count",
        "aliases",
        "concepts",
        "related_interpretations",
        "tags",
        "obsidian_processed_at",
        "extracted_at",
    ]
    keys = [key for key in preferred if key in fm]
    keys.extend(sorted(key for key in fm.keys() if key not in keys and fm[key] not in (None, "", [], {})))
    lines = ["---"]
    for key in keys:
        value = fm.get(key)
        if value in (None, "", [], {}):
            continue
        if isinstance(value, (list, tuple)):
            lines.append(f"{key}:")
            for item in unique_list([str(x) for x in value if str(x).strip()]):
                lines.append(f"  - {yaml_quote(item)}")
        else:
            lines.append(f"{key}: {yaml_quote(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def unique_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        clean = item.strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def clean_title_from_name(stem: str) -> str:
    title = re.sub(r"^\d{3}_", "", stem)
    title = title.removeprefix("法規-").removeprefix("校內規定-")
    return title.strip()


def clean_interpretation_title(value: str) -> str:
    return re.sub(r"^\d{3}_", "", value).strip()


def extract_sequence_number(*values: str) -> int | None:
    for value in values:
        match = re.match(r"^(\d{3})_", value or "")
        if match:
            return int(match.group(1))
    return None


def normalize_doc_no_value(doc_no: str) -> str:
    doc_no = clean_inline(doc_no, 160)
    doc_no = re.sub(r"\s+", "", doc_no)
    replacements = {
        "憂教學": "臺教學",
        "臺教學三字": "臺教學(三)字",
        "臺教學（三）字": "臺教學(三)字",
        "臺教人三字": "臺教人(三)字",
        "臺訓三字": "臺訓(三)字",
        "台訓三字": "台訓(三)字",
        "台人二字": "台人(二)字",
        "臺人二字": "臺人(二)字",
    }
    for old, new in replacements.items():
        doc_no = doc_no.replace(old, new)
    return doc_no


def is_probable_doc_no(doc_no: str) -> bool:
    return bool(doc_no and "字第" in doc_no and "號" in doc_no and "月" not in doc_no and len(doc_no) <= 80)


def sanitize_filename_stem(stem: str) -> str:
    stem = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", stem)
    stem = re.sub(r"\s+", "", stem)
    stem = stem.strip(" ._")
    return stem[:120] if len(stem) > 120 else stem


def duplicate_suffix(title: str) -> str:
    suffix = clean_interpretation_title(title)
    suffix = re.sub(r"^\d{6,8}[-_]*", "", suffix)
    suffix = suffix.strip(" -_")
    return sanitize_filename_stem(suffix)[:45] or "同號函釋"


def collision_descriptor(fm: dict[str, object], doc_no: str) -> str:
    """Derive a human-readable suffix for same-doc_no collisions, avoiding doc_no-doc_no names."""
    candidates: list[str] = []
    aliases = fm.get("aliases")
    if isinstance(aliases, list):
        for alias in aliases:
            alias = str(alias)
            if "號-" in alias:
                candidates.append(alias.split("號-", 1)[1])
    source = str(fm.get("source_pdf") or fm.get("source_text") or "")
    if source:
        stem = re.sub(r"\.(pdf|txt)$", "", source, flags=re.I)
        stem = re.sub(r"^\d{3}_", "", stem)
        stem = re.sub(r"^\d{6,8}", "", stem)
        candidates.append(stem)
    for candidate in candidates:
        cleaned = sanitize_filename_stem(candidate.strip(" -_"))[:45]
        # Reject a descriptor that is just the doc_no itself.
        if cleaned and cleaned != sanitize_filename_stem(doc_no):
            return cleaned
    return ""


def read_interpretation_metadata(path: Path) -> tuple[str, str, str, str]:
    text = read_text(path)
    text, _ = normalize_cjk_compat(text)
    fm, body = parse_frontmatter(text)
    title = clean_interpretation_title(str(fm.get("title") or extract_h1(body, path.stem)))
    note_type = str(fm.get("type") or ("函釋目錄" if "目錄" in title else "函釋"))
    doc_no = normalize_doc_no_value(str(fm.get("doc_no") or extract_doc_no(body)))
    descriptor = collision_descriptor(fm, doc_no)
    return title, note_type, doc_no, descriptor


def safe_move(src: Path, dst: Path) -> Path:
    if src.resolve() == dst.resolve():
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if src.stat().st_size == dst.stat().st_size:
            src.unlink()
            return dst
        base = dst.with_suffix("")
        suffix = dst.suffix
        index = 2
        while True:
            candidate = base.parent / f"{base.name}_{index}{suffix}"
            if not candidate.exists():
                dst = candidate
                break
            index += 1
    shutil.move(str(src), str(dst))
    return dst


def organize_files() -> dict[str, int]:
    moved = defaultdict(int)
    for md in sorted(ROOT.glob("*.md")):
        if re.match(r"^\d{3}_", md.name):
            safe_move(md, DIR_INTERPRETATIONS / md.name)
            moved["interpretation_md"] += 1
    for md in sorted(DIR_INTERPRETATIONS.glob("*.md")):
        if re.match(r"^\d{3}_", md.name):
            clean_name = re.sub(r"^\d{3}_", "", md.name)
            safe_move(md, DIR_INTERPRETATIONS / clean_name)
            moved["renamed_interpretation_md"] += 1
            continue
        if "[" in md.name or "]" in md.name:
            sanitized_name = md.name.replace("[", "(").replace("]", ")")
            safe_move(md, DIR_INTERPRETATIONS / sanitized_name)
            moved["sanitized_md_names"] += 1

    interpretation_paths = sorted(DIR_INTERPRETATIONS.glob("*.md"))
    metadata = {path: read_interpretation_metadata(path) for path in interpretation_paths}
    doc_counts: dict[str, int] = defaultdict(int)
    for title, note_type, doc_no, _descriptor in metadata.values():
        if note_type != "函釋目錄" and is_probable_doc_no(doc_no):
            doc_counts[doc_no] += 1
    collision_seen: dict[str, int] = defaultdict(int)
    for path in interpretation_paths:
        title, note_type, doc_no, descriptor = metadata[path]
        if note_type == "函釋目錄" or not is_probable_doc_no(doc_no):
            target_stem = title
        elif doc_counts[doc_no] > 1:
            collision_seen[doc_no] += 1
            suffix = descriptor or duplicate_suffix(title)
            if not suffix or sanitize_filename_stem(suffix) == sanitize_filename_stem(doc_no):
                suffix = f"同號{collision_seen[doc_no]}"
            target_stem = f"{doc_no}-{suffix}"
        else:
            target_stem = doc_no
        target_name = sanitize_filename_stem(target_stem) + path.suffix
        if target_name and target_name != path.name:
            safe_move(path, DIR_INTERPRETATIONS / target_name)
            moved["formalized_interpretation_names"] += 1

    for pdf in sorted(ROOT.glob("*.pdf")):
        safe_move(pdf, DIR_PDFS / pdf.name)
        moved["pdf"] += 1
    for txt in sorted(ROOT.glob("*.txt")):
        safe_move(txt, DIR_TEXT_SOURCES / txt.name)
        moved["txt"] += 1
    return dict(moved)


def wikilink(name: str, display: str | None = None) -> str:
    target = name.replace("|", "-")
    if display and display != name:
        return f"[[{target}|{display}]]"
    return f"[[{target}]]"


def concept_links(concepts: list[str]) -> str:
    return "、".join(wikilink(name) for name in concepts) if concepts else "（未自動標記）"


def find_concepts(text: str, title: str = "") -> list[str]:
    haystack = f"{title}\n{text}"
    found: list[str] = []
    for concept in CONCEPTS:
        for term in sorted(concept.terms, key=len, reverse=True):
            if term and term in haystack:
                found.append(concept.name)
                break
    return unique_list(found)


def extract_h1(body: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", body, flags=re.MULTILINE)
    return match.group(1).strip() if match else fallback


def clean_inline(value: str, max_len: int = 220) -> str:
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" 　:-：")
    if len(value) > max_len:
        value = value[: max_len - 1].rstrip() + "…"
    return value


def extract_doc_no(text: str) -> str:
    patterns = [
        r"發文字號[：:\s]*([^\n]+)",
        r"([臺台]教[^\n]{0,20}?字第\s*[0-9A-Za-z\-]+號)",
        r"([臺台]訓[^\n]{0,20}?字第\s*[0-9A-Za-z\-]+號)",
        r"([臺台]人[^\n]{0,20}?字第\s*[0-9A-Za-z\-]+號)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            doc_no = normalize_doc_no_value(match.group(1))
            if doc_no and doc_no not in {"無附件", "普通件", "最速件"}:
                return doc_no
    return ""


def extract_subject(text: str) -> str:
    match = re.search(r"主旨[：:\s]*(.+?)(?:\n\s*說明[：:]|\n\s*一、|\n\s*正本[：:]|\Z)", text, flags=re.S)
    if not match:
        return ""
    subject = match.group(1)
    subject = re.sub(r"\b[裝訂線]\b", "", subject)
    return clean_inline(subject, 260)


CJK_DIGITS = {
    "零": 0, "〇": 0, "○": 0, "Ｏ": 0,
    "一": 1, "壹": 1, "二": 2, "貳": 2, "兩": 2,
    "三": 3, "參": 3, "叁": 3, "四": 4, "肆": 4,
    "五": 5, "伍": 5, "六": 6, "陸": 6, "七": 7, "柒": 7,
    "八": 8, "捌": 8, "九": 9, "玖": 9,
}
CJK_UNITS = {"十": 10, "拾": 10, "百": 100, "佰": 100, "千": 1000, "仟": 1000}
CJK_NUM_CLASS = "0-9" + "".join(CJK_DIGITS) + "".join(CJK_UNITS)


def parse_cjk_number(value: str) -> int | None:
    """Parse Arabic or Traditional-Chinese (incl. 大寫) numerals, e.g. 九十三→93, 玖拾陸→96, 一一三→113."""
    value = value.strip()
    if not value:
        return None
    if re.fullmatch(r"\d+", value):
        return int(value)
    # Pure digit-by-digit Chinese form, e.g. 一一三 → 113
    if all(ch in CJK_DIGITS for ch in value):
        return int("".join(str(CJK_DIGITS[ch]) for ch in value))
    # Positional form with 十/百/千 units, e.g. 九十三 → 93
    section = 0
    current = 0
    for ch in value:
        if ch in CJK_DIGITS:
            current = CJK_DIGITS[ch]
        elif ch in CJK_UNITS:
            section += (current or 1) * CJK_UNITS[ch]
            current = 0
        else:
            return None
    return section + current


def extract_roc_date(text: str, filename: str) -> tuple[str, str]:
    match = re.search(r"發文日期[：:\s]*(?:中華民國)?\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
    if match:
        roc_y, month, day = map(int, match.groups())
        return f"{roc_y}年{month}月{day}日", iso_from_roc(roc_y, month, day)
    match = re.search(
        rf"發文日期[：:\s]*(?:中華民國)?\s*([{CJK_NUM_CLASS}]+)\s*年\s*([{CJK_NUM_CLASS}]+)\s*月\s*([{CJK_NUM_CLASS}]+)\s*日",
        text,
    )
    if match:
        roc_y = parse_cjk_number(match.group(1))
        month = parse_cjk_number(match.group(2))
        day = parse_cjk_number(match.group(3))
        if roc_y and month and day and 1 <= month <= 12 and 1 <= day <= 31:
            return f"{roc_y}年{month}月{day}日", iso_from_roc(roc_y, month, day)
    match = re.search(r"(?:^|_)(\d{6,7})(?:\D|$)", filename)
    if match:
        digits = match.group(1)
        if len(digits) == 7:
            roc_y, month, day = int(digits[:3]), int(digits[3:5]), int(digits[5:7])
        else:
            roc_y, month, day = int(digits[:2]), int(digits[2:4]), int(digits[4:6])
        if 1 <= month <= 12 and 1 <= day <= 31:
            return f"{roc_y}年{month}月{day}日", iso_from_roc(roc_y, month, day)
    return "", ""


def iso_from_roc(roc_y: int, month: int, day: int) -> str:
    year = roc_y + 1911 if roc_y < 1911 else roc_y
    return f"{year:04d}-{month:02d}-{day:02d}"


def remove_generated_block(text: str, begin: str, end: str) -> str:
    pattern = re.compile(rf"\n?{re.escape(begin)}.*?{re.escape(end)}\n?", re.S)
    return pattern.sub("\n", text).strip() + "\n"


def insert_after_h1(body: str, block: str, fallback_title: str) -> str:
    match = re.search(r"^#\s+.+?\s*$", body, flags=re.MULTILINE)
    if match:
        return body[: match.end()] + "\n\n" + block.rstrip() + "\n\n" + body[match.end() :].lstrip("\n")
    return f"# {fallback_title}\n\n{block.rstrip()}\n\n{body.lstrip()}"


def normalize_h1(body: str, title: str) -> str:
    if re.search(r"^#\s+.+?\s*$", body, flags=re.MULTILINE):
        return re.sub(r"^#\s+.+?\s*$", f"# {title}", body, count=1, flags=re.MULTILINE)
    return f"# {title}\n\n{body.lstrip()}"


def process_interpretation(path: Path) -> tuple[Record, int]:
    raw = read_text(path)
    normalized, changed = normalize_cjk_compat(raw)
    fm, body = parse_frontmatter(normalized)
    body = remove_generated_block(body, OBSIDIAN_BEGIN, OBSIDIAN_END)
    body = remove_generated_block(body, INTERPRETATION_REFS_BEGIN, INTERPRETATION_REFS_END)

    fallback_title = path.stem
    raw_title = str(fm.get("title") or extract_h1(body, fallback_title))
    title = clean_interpretation_title(raw_title)
    title = clean_inline(title, 180)
    old_aliases = fm.get("aliases")
    alias_values = [str(x) for x in old_aliases] if isinstance(old_aliases, list) else []
    number = extract_sequence_number(path.name, raw_title, str(fm.get("source_pdf") or ""), *alias_values)
    note_type = "函釋目錄" if "目錄" in title else "函釋"
    doc_no = normalize_doc_no_value(str(fm.get("doc_no") or extract_doc_no(body)))
    if note_type == "函釋目錄":
        # Catalog notes list many letters; a single extracted doc_no is meaningless
        # (and frequently garbled), so drop it to keep downstream displays clean.
        doc_no = ""
        new_fm_pop_doc_no = True
    else:
        new_fm_pop_doc_no = False
        if is_probable_doc_no(doc_no):
            title = doc_no
    body = normalize_h1(body, title)
    roc_date, issued_date = extract_roc_date(body, path.name)
    if not roc_date:
        roc_date = str(fm.get("roc_date") or "")
    if not issued_date:
        issued_date = str(fm.get("issued_date") or "")
    subject = str(fm.get("subject") or extract_subject(body))
    concepts = find_concepts(body, title)

    aliases = []
    aliases.extend(alias_values)
    aliases.extend([clean_interpretation_title(raw_title), path.stem, clean_title_from_name(path.stem), doc_no])
    aliases = unique_list(
        [
            alias
            for alias in aliases
            if alias
            and alias != title
            and not re.match(r"^\d{3}_", alias)
            # Drop the legacy self-referential "<doc_no>-<doc_no>" alias artifact.
            and not (doc_no and alias.startswith(f"{doc_no}-{doc_no}"))
        ]
    )

    tags = ["校園性平/函釋目錄" if note_type == "函釋目錄" else "校園性平/函釋"]
    new_fm = dict(fm)
    new_fm.update(
        {
            "title": title,
            "type": note_type,
            "aliases": aliases,
            "concepts": concepts,
            "tags": tags,
            "obsidian_processed_at": TODAY,
        }
    )
    if new_fm_pop_doc_no:
        new_fm.pop("doc_no", None)
    if doc_no:
        new_fm["doc_no"] = doc_no
    if issued_date:
        new_fm["issued_date"] = issued_date
    if roc_date:
        new_fm["roc_date"] = roc_date
    if subject:
        new_fm["subject"] = subject

    details = [
        f"- 類型：{note_type}",
        f"- 發文日期：{issued_date or roc_date or '未擷取'}",
        f"- 發文字號：{doc_no or '未擷取'}",
        f"- 主題概念：{concept_links(concepts)}",
    ]
    laws = [name for name in concepts if name in LAW_NAMES]
    if laws:
        details.append(f"- 相關法規：{concept_links(laws)}")
    block = f"{OBSIDIAN_BEGIN}\n## Obsidian 索引\n\n" + "\n".join(details) + f"\n{OBSIDIAN_END}\n\n"
    new_body = insert_after_h1(body.lstrip(), block, title)
    write_text(path, dump_frontmatter(new_fm) + new_body)

    return (
        Record(
            title=title,
            path=path,
            kind=note_type,
            number=number,
            issued_date=issued_date,
            roc_date=roc_date,
            doc_no=doc_no,
            subject=subject,
            concepts=concepts,
        ),
        changed,
    )


def title_for_source(path: Path) -> str:
    return clean_title_from_name(path.stem)


def extract_pdf_text(path: Path) -> tuple[str, int, str]:
    try:
        import pdfplumber
    except Exception as exc:  # pragma: no cover - depends on runtime
        return "", 0, f"pdfplumber unavailable: {exc}"
    chunks: list[str] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            page_count = len(pdf.pages)
            for index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text, _ = normalize_cjk_compat(text)
                if text.strip():
                    chunks.append(f"## Page {index}\n\n{text.strip()}")
        return "\n\n".join(chunks).strip(), page_count, ""
    except Exception as exc:
        return "", 0, str(exc)


def build_text_sources() -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for txt in sorted(DIR_TEXT_SOURCES.glob("*.txt")):
        sources[title_for_source(txt)] = txt
    return sources


def source_attachment_link(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def recover_existing_source_text(title: str, kind: str) -> str:
    """Return the previously-extracted '條文或來源文字' body of a law/local-rule note, if any."""
    target_dir = DIR_LAWS if kind == "法規" else DIR_LOCAL_RULES
    note_path = target_dir / f"{title}.md"
    if not note_path.exists():
        return ""
    body = read_text(note_path)
    body, _ = normalize_cjk_compat(body)
    marker = "## 條文或來源文字"
    index = body.find(marker)
    if index == -1:
        return ""
    content = body[index + len(marker) :].strip()
    if not content or content.startswith("（此 PDF 未能自動抽出"):
        return ""
    return content


def make_source_note(title: str, kind: str, source_pdf: Path | None, source_text: Path | None) -> tuple[Record, str]:
    text = ""
    page_count = 0
    extraction_issue = ""
    source_text_content = ""
    if source_text and source_text.exists():
        source_text_content = read_text(source_text)
        source_text_content, _ = normalize_cjk_compat(source_text_content)
        text = source_text_content.strip()
    elif source_pdf and source_pdf.exists():
        text, page_count, extraction_issue = extract_pdf_text(source_pdf)
        # Guard: if PDF extraction yields nothing (e.g. pdfplumber unavailable) but a
        # previously-generated note already holds real text, keep it rather than
        # overwriting good content with the "未能自動抽出" placeholder.
        if not text:
            existing = recover_existing_source_text(title, kind)
            if existing:
                text = existing
                if not extraction_issue:
                    extraction_issue = "沿用既有抽取文字（本次未重新抽出 PDF）"

    aliases: list[str] = []
    concept = CONCEPT_BY_NAME.get(title)
    if concept:
        aliases.extend(concept.aliases)
    if source_pdf:
        aliases.append(source_pdf.stem)
    if source_text:
        aliases.append(source_text.stem)
    aliases = unique_list([alias for alias in aliases if alias and alias != title])

    concepts = [name for name in find_concepts(text, title) if name != title]
    if concept and concept.kind != "law" and title not in concepts:
        concepts.insert(0, title)
    tags = ["校園性平/法規" if kind == "法規" else "校園性平/校內規定"]
    fm: dict[str, object] = {
        "title": title,
        "type": kind,
        "aliases": aliases,
        "concepts": concepts,
        "tags": tags,
        "obsidian_processed_at": TODAY,
    }
    if source_pdf:
        fm["source_pdf"] = source_pdf.name
        fm["source_attachment"] = source_attachment_link(source_pdf)
    if source_text:
        fm["source_text"] = source_text.name
        fm["source_text_attachment"] = source_attachment_link(source_text)
    if page_count:
        fm["page_count"] = page_count
    if text:
        fm["text_chars"] = len(text)

    source_lines = []
    if source_pdf:
        source_lines.append(f"- PDF：[[{source_attachment_link(source_pdf)}]]")
    if source_text:
        source_lines.append(f"- 文字來源：[[{source_attachment_link(source_text)}]]")
    if extraction_issue:
        source_lines.append(f"- PDF 文字抽取狀態：{extraction_issue}")
    if not source_lines:
        source_lines.append("- 來源：未標記")

    body = [
        f"# {title}",
        "",
        f"{OBSIDIAN_BEGIN}",
        "## Obsidian 索引",
        "",
        f"- 類型：{kind}",
        f"- 主題概念：{concept_links(concepts)}",
        f"{OBSIDIAN_END}",
        "",
        "## 來源",
        "",
        *source_lines,
        "",
        "## 條文或來源文字",
        "",
        text if text else "（此 PDF 未能自動抽出可用文字，請開啟來源附件閱讀。）",
        "",
    ]
    target_dir = DIR_LAWS if kind == "法規" else DIR_LOCAL_RULES
    note_path = target_dir / f"{title}.md"
    write_text(note_path, dump_frontmatter(fm) + "\n".join(body).rstrip() + "\n")
    return Record(title=title, path=note_path, kind=kind, concepts=concepts), extraction_issue


def generate_source_notes() -> tuple[list[Record], list[str]]:
    records: list[Record] = []
    issues: list[str] = []
    text_sources = build_text_sources()
    used_text_sources: set[Path] = set()

    for pdf in sorted(DIR_PDFS.glob("*.pdf")):
        title = title_for_source(pdf)
        kind = "校內規定" if pdf.stem.startswith("校內規定-") else "法規"
        source_text = text_sources.get(title)
        if source_text:
            used_text_sources.add(source_text)
        record, issue = make_source_note(title, kind, pdf, source_text)
        records.append(record)
        if issue:
            issues.append(f"{pdf.name}: {issue}")

    for title, txt in sorted(text_sources.items()):
        if txt in used_text_sources:
            continue
        record, issue = make_source_note(title, "法規", None, txt)
        records.append(record)
        if issue:
            issues.append(f"{txt.name}: {issue}")
    records.append(make_criminal_code_index())
    return records, issues


def make_criminal_code_index() -> Record:
    concept = CONCEPT_BY_NAME["刑法"]
    related_sources = [
        DIR_LAWS / "刑法第10條.md",
        DIR_LAWS / "刑法第16章妨礙性自主罪章.md",
    ]
    fm: dict[str, object] = {
        "title": "刑法",
        "type": "法規",
        "aliases": list(concept.aliases),
        "concepts": ["性侵害", "性影像", "性騷擾"],
        "tags": ["校園性平/法規"],
        "obsidian_processed_at": TODAY,
    }
    body = [
        "# 刑法",
        "",
        f"{OBSIDIAN_BEGIN}",
        "## Obsidian 索引",
        "",
        "- 類型：法規",
        "- 主題概念：[[性侵害]]、[[性影像]]、[[性騷擾]]",
        f"{OBSIDIAN_END}",
        "",
        "## 本庫收錄範圍",
        "",
        "本頁作為刑法相關資料的統一入口，避免另建 `刑法第10條`、`妨礙性自主罪章` 以外的重複概念頁。",
        "",
        "## 來源筆記",
        "",
    ]
    for source in related_sources:
        if source.exists():
            body.append(f"- [[{source.stem}]]")
    write_text(DIR_LAWS / "刑法.md", dump_frontmatter(fm) + "\n".join(body).rstrip() + "\n")
    return Record(title="刑法", path=DIR_LAWS / "刑法.md", kind="法規", concepts=["性侵害", "性影像", "性騷擾"])


def note_ref(record: Record) -> str:
    return wikilink(record.path.stem, record.title if record.path.stem != record.title else None)


def interpretation_ref(record: Record) -> str:
    display = record.doc_no or record.title
    return wikilink(record.path.stem, display if display != record.path.stem else None)


def sort_records(records: list[Record]) -> list[Record]:
    return sorted(records, key=lambda r: (r.issued_date or "0000-00-00", r.number or 9999, r.title), reverse=True)


def normalize_reference_key(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text, _ = normalize_cjk_compat(text)
    text = text.replace("臺", "台")
    text = re.sub(r"\s+", "", text)
    text = text.replace("(", "").replace(")", "").replace("（", "").replace("）", "")
    return text


def doc_no_reference_keys(doc_no: str) -> list[str]:
    compact = normalize_reference_key(doc_no)
    if not compact:
        return []
    keys = [compact]
    match = re.search(r"第([0-9A-Z]+(?:[-、][0-9A-Z]+)*)號", compact)
    if match:
        number = match.group(1)
        if re.search(r"\d{7,}", number):
            keys.append(f"第{number}號")
            keys.append(number)
    return unique_list([key for key in keys if len(key) >= 7])


def compact_roc_date(roc_date: str) -> str:
    match = re.search(r"(\d{2,3})年(\d{1,2})月(\d{1,2})日", roc_date)
    if not match:
        return ""
    year, month, day = map(int, match.groups())
    return f"{year}年{month}月{day}日"


def source_text_for_reference_scan(path: Path) -> str:
    text = read_text(path)
    text, _ = normalize_cjk_compat(text)
    _fm, body = parse_frontmatter(text)
    body = remove_generated_block(body, OBSIDIAN_BEGIN, OBSIDIAN_END)
    body = remove_generated_block(body, INTERPRETATION_REFS_BEGIN, INTERPRETATION_REFS_END)
    return body


def body_mentions_roc_date_as_reference(compact_body: str, roc_date: str) -> bool:
    date = compact_roc_date(roc_date)
    if not date:
        return False
    start = 0
    while True:
        index = compact_body.find(date, start)
        if index == -1:
            return False
        window = compact_body[max(0, index - 8) : index + len(date) + 18]
        if "函" in window and ("本部" in window or "前" in window or "諒達" in window):
            return True
        start = index + len(date)


def find_interpretation_references(interpretation_records: list[Record]) -> dict[str, list[Record]]:
    targets = [record for record in interpretation_records if record.kind == "函釋"]
    doc_keys: dict[str, list[tuple[str, Record]]] = {}
    date_targets: dict[str, list[Record]] = defaultdict(list)
    for record in targets:
        keys = doc_no_reference_keys(record.doc_no)
        if keys:
            doc_keys[record.path.stem] = [(key, record) for key in keys]
        date = compact_roc_date(record.roc_date)
        if date:
            date_targets[date].append(record)

    unique_date_targets = {date: records[0] for date, records in date_targets.items() if len(records) == 1}
    reference_map: dict[str, list[Record]] = {}
    for source in targets:
        body = source_text_for_reference_scan(source.path)
        compact_body = normalize_reference_key(body)
        source_doc_keys = set(doc_no_reference_keys(source.doc_no))
        referenced: dict[str, Record] = {}
        for target_key, key_records in doc_keys.items():
            if target_key == source.path.stem:
                continue
            for key, target in key_records:
                if source_doc_keys.intersection(doc_no_reference_keys(target.doc_no)):
                    continue
                if key and key in compact_body:
                    referenced[target.path.stem] = target
                    break
        for date, target in unique_date_targets.items():
            if target.path == source.path:
                continue
            if target.path.stem in referenced:
                continue
            if body_mentions_roc_date_as_reference(compact_body, target.roc_date):
                referenced[target.path.stem] = target
        if referenced:
            reference_map[source.path.stem] = sort_records(list(referenced.values()))
    return reference_map


def insert_after_generated_index(body: str, block: str, fallback_title: str) -> str:
    if OBSIDIAN_END in body:
        index = body.find(OBSIDIAN_END) + len(OBSIDIAN_END)
        return body[:index].rstrip() + "\n\n" + block.rstrip() + "\n\n" + body[index:].lstrip("\n")
    return insert_after_h1(body, block, fallback_title)


def update_interpretation_reference_blocks(interpretation_records: list[Record], reference_map: dict[str, list[Record]]) -> None:
    for source in interpretation_records:
        if source.kind != "函釋":
            continue
        text = read_text(source.path)
        text, _ = normalize_cjk_compat(text)
        fm, body = parse_frontmatter(text)
        body = remove_generated_block(body, INTERPRETATION_REFS_BEGIN, INTERPRETATION_REFS_END)
        references = reference_map.get(source.path.stem, [])
        if references:
            fm["related_interpretations"] = [target.path.stem for target in references]
            lines = [f"{INTERPRETATION_REFS_BEGIN}", "## 提及其他函釋", ""]
            for target in references:
                meta = target.issued_date or target.roc_date
                subject = f" - {target.subject}" if target.subject else ""
                lines.append(f"- {interpretation_ref(target)}" + (f"（{meta}）" if meta else "") + subject)
            lines.append(INTERPRETATION_REFS_END)
            body = insert_after_generated_index(body.lstrip(), "\n".join(lines), source.title)
        else:
            fm.pop("related_interpretations", None)
        write_text(source.path, dump_frontmatter(fm) + body)


def generate_interpretation_reference_index(reference_map: dict[str, list[Record]], interpretation_records: list[Record]) -> None:
    by_stem = {record.path.stem: record for record in interpretation_records}
    incoming: dict[str, list[Record]] = defaultdict(list)
    for source_stem, targets in reference_map.items():
        source = by_stem.get(source_stem)
        if not source:
            continue
        for target in targets:
            incoming[target.path.stem].append(source)

    lines = [
        "# 函釋關聯總表",
        "",
        "本表由正文中明確出現的發文字號或可唯一辨識的函示日期自動產生。",
        "",
        "## 提及其他函釋",
        "",
    ]
    if reference_map:
        for source in sort_records([by_stem[stem] for stem in reference_map if stem in by_stem]):
            lines.append(f"- {interpretation_ref(source)}")
            for target in reference_map[source.path.stem]:
                meta = target.issued_date or target.roc_date
                lines.append(f"  - 提及 {interpretation_ref(target)}" + (f"（{meta}）" if meta else ""))
    else:
        lines.append("- 未自動偵測到函釋間引用。")

    lines.extend(["", "## 被其他函釋提及", ""])
    if incoming:
        for target in sort_records([by_stem[stem] for stem in incoming if stem in by_stem]):
            sources = sort_records(incoming[target.path.stem])
            lines.append(f"- {interpretation_ref(target)}：被 {len(sources)} 份提及")
            for source in sources[:30]:
                lines.append(f"  - {interpretation_ref(source)}")
            if len(sources) > 30:
                lines.append(f"  - 另有 {len(sources) - 30} 份")
    else:
        lines.append("- 未自動偵測到被引用關係。")
    write_text(DIR_OVERVIEW / "函釋關聯總表.md", "\n".join(lines) + "\n")


def related_lines(concept_name: str, records: list[Record], limit: int | None = None) -> list[str]:
    related = [record for record in records if concept_name in record.concepts and record.title != concept_name]
    related = sort_records(related)
    if limit:
        shown = related[:limit]
    else:
        shown = related
    lines: list[str] = []
    for record in shown:
        meta = record.issued_date or record.roc_date or record.doc_no or record.kind
        subject = f" - {record.subject}" if record.subject else ""
        lines.append(f"- {meta} {note_ref(record)}{subject}")
    if limit and len(related) > limit:
        lines.append(f"- 另有 {len(related) - limit} 筆，請用反向連結或搜尋 `concepts: {concept_name}` 查看。")
    if not lines:
        lines.append("- 尚未由批次規則標記到相關資料。")
    return lines


def generate_concept_notes(records: list[Record]) -> None:
    for concept in CONCEPTS:
        if concept.kind == "law":
            continue
        fm = {
            "title": concept.name,
            "type": "概念",
            "aliases": [alias for alias in concept.aliases if alias != concept.name],
            "tags": ["校園性平/概念"],
            "obsidian_processed_at": TODAY,
        }
        body = [
            f"# {concept.name}",
            "",
            "## 定義與使用",
            "",
            concept.summary or "此概念由受控詞表統一管理，避免同義詞重複建置。",
            "",
            "## 同義詞與歸併",
            "",
        ]
        if concept.aliases:
            body.extend(f"- {alias}" for alias in concept.aliases)
        else:
            body.append("- 無")
        if concept.related:
            body.extend(["", "## 關聯概念", ""])
            body.append(concept_links(list(concept.related)))
        body.extend(["", "## 相關資料", ""])
        body.extend(related_lines(concept.name, records, limit=160))
        write_text(DIR_CONCEPTS / f"{concept.name}.md", dump_frontmatter(fm) + "\n".join(body).rstrip() + "\n")


def update_law_related_sections(records: list[Record]) -> None:
    for concept in CONCEPTS:
        if concept.kind != "law":
            continue
        candidates = list(DIR_LAWS.glob(f"{concept.name}.md"))
        if not candidates:
            continue
        path = candidates[0]
        text = read_text(path)
        text, _ = normalize_cjk_compat(text)
        text = remove_generated_block(text, RELATED_BEGIN, RELATED_END)
        related = "\n".join(related_lines(concept.name, records, limit=220))
        block = f"\n{RELATED_BEGIN}\n## 相關函釋與資料\n\n{related}\n{RELATED_END}\n"
        write_text(path, text.rstrip() + "\n" + block)


def generate_overviews(
    records: list[Record],
    moved: dict[str, int],
    changed_chars: int,
    extraction_issues: list[str],
    reference_map: dict[str, list[Record]] | None = None,
) -> None:
    reference_map = reference_map or {}
    interpretations = [r for r in records if r.kind in {"函釋", "函釋目錄"}]
    laws = [r for r in records if r.kind == "法規"]
    local_rules = [r for r in records if r.kind == "校內規定"]
    concept_counts = {concept.name: sum(1 for r in records if concept.name in r.concepts) for concept in CONCEPTS}
    reference_edges = sum(len(targets) for targets in reference_map.values())

    overview = [
        "# 性平知識庫總覽",
        "",
        "## 入口",
        "",
        "- [[函釋時間軸]]",
        "- [[函釋清單]]",
        "- [[函釋關聯總表]]",
        "- [[法規索引]]",
        "- [[概念索引]]",
        "- [[處理規範]]",
        "- [[待人工複核]]",
        "",
        "## 統計",
        "",
        f"- 函釋/目錄筆記：{len(interpretations)}",
        f"- 法規筆記：{len(laws)}",
        f"- 校內規定筆記：{len(local_rules)}",
        f"- 受控概念：{len(CONCEPTS)}",
        f"- 函釋間關聯：{reference_edges}",
        f"- 本次移入函釋 Markdown：{moved.get('interpretation_md', 0)}",
        f"- 本次移入 PDF 附件：{moved.get('pdf', 0)}",
        f"- 本次移入文字來源：{moved.get('txt', 0)}",
        f"- OCR 相容漢字正規化：{changed_chars} 字",
        "",
        "## 使用方式",
        "",
        "從概念頁進入主題，或從函釋時間軸依日期追蹤函示脈絡。每份函釋筆記的 `Obsidian 索引` 區塊會連到統一概念頁，避免同義詞各自成頁。",
        "",
    ]
    write_text(DIR_OVERVIEW / "性平知識庫總覽.md", "\n".join(overview))

    timeline = ["# 函釋時間軸", ""]
    for record in sort_records(interpretations):
        date = record.issued_date or record.roc_date or "未擷取日期"
        doc_no = f"（{record.doc_no}）" if record.doc_no else ""
        subject = f" - {record.subject}" if record.subject else ""
        timeline.append(f"- {date} {note_ref(record)}{doc_no}{subject}")
    write_text(DIR_OVERVIEW / "函釋時間軸.md", "\n".join(timeline) + "\n")

    listing = ["# 函釋清單", ""]
    for record in sorted(interpretations, key=lambda r: (r.number or 9999, r.title)):
        prefix = f"{record.number:03d}" if record.number else "未編號"
        meta = record.issued_date or record.roc_date or record.doc_no
        listing.append(f"- {prefix} {note_ref(record)}" + (f" - {meta}" if meta else ""))
    write_text(DIR_OVERVIEW / "函釋清單.md", "\n".join(listing) + "\n")

    law_index = ["# 法規索引", "", "## 法規", ""]
    for record in sorted(laws, key=lambda r: r.title):
        law_index.append(f"- {note_ref(record)}")
    law_index.extend(["", "## 校內規定", ""])
    for record in sorted(local_rules, key=lambda r: r.title):
        law_index.append(f"- {note_ref(record)}")
    write_text(DIR_OVERVIEW / "法規索引.md", "\n".join(law_index) + "\n")

    concept_index = [
        "# 概念索引",
        "",
        "同義詞已歸併到下列唯一概念頁；建立新筆記前，先查這張表。",
        "",
    ]
    for concept in CONCEPTS:
        aliases = f"（別名：{'、'.join(concept.aliases)}）" if concept.aliases else ""
        count = concept_counts.get(concept.name, 0)
        concept_index.append(f"- {wikilink(concept.name)} {aliases} - {count} 筆資料")
    write_text(DIR_OVERVIEW / "概念索引.md", "\n".join(concept_index) + "\n")

    rules = [
        "# 處理規範",
        "",
        "## 命名與歸檔",
        "",
        "- 函釋統一放在 `10_函釋`，一般函釋以正式發文字號作檔名；目錄保留目錄名稱。",
        "- 若不同資料擷取到同一發文字號，檔名會在發文字號後加短描述以避免覆蓋。",
        "- 法規與校內規定各自生成 Markdown 筆記，PDF 保留於 `90_附件/PDF`。",
        "- 原始 `.txt` 來源保留於 `90_附件/文字來源`，並由法規筆記連回。",
        "",
        "## Obsidian 欄位",
        "",
        "- 每份函釋補上 `title`、`type`、`aliases`、`concepts`、`tags` 與 `obsidian_processed_at`。",
        "- 可擷取時，補上 `發文日期`、`發文字號`、`主旨`。",
        "- 每份筆記都有 `Obsidian 索引` 區塊，集中放概念連結。",
        "- 函釋正文若明確提到其他函釋，會補上 `related_interpretations` 與 `提及其他函釋` 區塊。",
        "",
        "## 同義詞原則",
        "",
        "- 以 `00_總覽/概念索引` 為唯一受控詞表。",
        "- 例如 `性平法` 歸到 [[性別平等教育法]]，`防治準則` 歸到 [[校園性別事件防治準則]]，`性平會` 歸到 [[性別平等教育委員會]]。",
        "- 不為同一涵義另開新概念頁；只在 canonical note 的 `aliases` 增補別名。",
        "",
        "## 文字品質",
        "",
        "- 讀取時使用 UTF-8；遇到疑似亂碼先檢查是否為編碼問題。",
        "- 本次確認舊函釋中的 U+F967、U+F9CE、U+F970 等屬 PDF/OCR 相容漢字，已正規化為標準字。",
        "",
        "## 公文 boilerplate 精簡",
        "",
        "- 函釋正文只保留主旨、說明與實質附件（一覽表、流程說明、設置要點等）。",
        "- 已移除：檔號、保存期限、地址、傳真、聯絡人、電話、受文者、速別、密等、發文日期/字號等抬頭欄位；正本／副本／署名分送名單；`## Page` 分頁標記；公文電子交換受文單位清單。",
        "- 此步驟由 `99_維護/strip_boilerplate.py` 執行（在本主腳本之後跑），具冪等性；新匯入函釋可於主腳本後再跑一次。",
        "- 精簡只動 `Obsidian 索引` 之後的正文，frontmatter 與索引區塊不受影響。",
        "",
    ]
    write_text(DIR_OVERVIEW / "處理規範.md", "\n".join(rules))

    review = ["# 待人工複核", ""]
    duplicate_numbers = defaultdict(list)
    for record in interpretations:
        if record.number is not None:
            duplicate_numbers[record.number].append(record)
    dupes = {k: v for k, v in duplicate_numbers.items() if len(v) > 1}
    review.extend(["## 重複編號", ""])
    if dupes:
        for number, items in sorted(dupes.items()):
            review.append(f"- {number:03d}：" + "、".join(note_ref(item) for item in items))
    else:
        review.append("- 未發現重複編號。")
    missing_date = [r for r in interpretations if not r.issued_date and not r.roc_date]
    missing_doc_no = [r for r in interpretations if not r.doc_no]
    review.extend(["", "## 未自動擷取", ""])
    review.append(f"- 未擷取日期：{len(missing_date)} 筆")
    for record in missing_date[:40]:
        review.append(f"  - {note_ref(record)}")
    review.append(f"- 未擷取發文字號：{len(missing_doc_no)} 筆")
    for record in missing_doc_no[:40]:
        review.append(f"  - {note_ref(record)}")
    review.extend(["", "## PDF 文字抽取問題", ""])
    if extraction_issues:
        review.extend(f"- {issue}" for issue in extraction_issues)
    else:
        review.append("- 未發現 PDF 文字抽取錯誤。")
    write_text(DIR_OVERVIEW / "待人工複核.md", "\n".join(review) + "\n")


def main() -> int:
    ensure_dirs()
    moved = organize_files()
    source_records, extraction_issues = generate_source_notes()

    interpretation_records: list[Record] = []
    changed_chars = 0
    for path in sorted(DIR_INTERPRETATIONS.glob("*.md")):
        record, changed = process_interpretation(path)
        interpretation_records.append(record)
        changed_chars += changed

    records = interpretation_records + source_records
    reference_map = find_interpretation_references(interpretation_records)
    update_interpretation_reference_blocks(interpretation_records, reference_map)
    generate_interpretation_reference_index(reference_map, interpretation_records)
    generate_concept_notes(records)
    update_law_related_sections(records)
    generate_overviews(records, moved, changed_chars, extraction_issues, reference_map)

    print(f"processed_interpretations={len(interpretation_records)}")
    print(f"source_notes={len(source_records)}")
    print(f"concepts={len(CONCEPTS)}")
    print(f"interpretation_reference_edges={sum(len(targets) for targets in reference_map.values())}")
    print(f"normalized_compat_chars={changed_chars}")
    print(f"pdf_extraction_issues={len(extraction_issues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
