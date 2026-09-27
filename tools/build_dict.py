#!/usr/bin/env python3
"""Собирает dict-en-ru.txt (англ. слово <TAB> перевод) из WikDict en-ru (Викисловарь, CC BY-SA)
с ранжированием по частотному словарю MUSE en-ru. Источники скачиваются в каталог из argv[1]:
  https://download.wikdict.com/dictionaries/sqlite/2/en-ru.sqlite3
  https://dl.fbaipublicfiles.com/arrival/dictionaries/en-ru.txt  (как muse-en-ru.txt)
"""
import re, sqlite3, sys, unicodedata, collections, os

src = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) > 2 else "dict-en-ru.txt"

BAD_SENSE = re.compile(r"vulgar|offensive|slang|sexual|derogat|pejorat|obscene|condom|penis|vagin|genital|\bsex|drug|narcot|ethnic slur|racial|homosexual|prostitut|fornicat|masturb|erotic|porn", re.I)
BAD_RU = re.compile(r"гондон|презерв|секс|сук[аи]|бляд|хуй|хуё|пизд|жоп|дерьм|говн|срат|ебат|ёбан|еба|наркот|проститут|шлюх|педик|пидор|член\b|мудак|залуп|минет|оргазм|порн|эрот", re.I)
EN_OK = re.compile(r"^[a-z][a-z' \-]{0,24}$")

def strip_marks(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if ch not in ("́", "̀"))
    return unicodedata.normalize("NFC", s)

def clean_ru(t):
    t = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", t)
    t = strip_marks(t).strip()
    t = re.sub(r"\s+", " ", t)
    if not t or not re.fullmatch(r"[А-Яа-яЁё][А-Яа-яЁё \-]*", t): return ""
    if len(t.split()) > 3 or BAD_RU.search(t): return ""
    return t

muse = collections.defaultdict(list)
for line in open(os.path.join(src, "muse-en-ru.txt"), encoding="utf-8"):
    p = line.split()
    if len(p) == 2: muse[p[0].lower()].append(p[1].lower())

def muse_hit(en, ru):
    r = ru.lower().replace("ё", "е")
    for m in muse.get(en, []):
        m = m.replace("ё", "е")
        if m == r: return 2
        k = 3 if min(len(m), len(r)) <= 5 else 4
        if len(m) >= k and len(r) >= k and m[:k] == r[:k]: return 1
    return 0

db = sqlite3.connect(os.path.join(src, "en-ru.sqlite3"))
rows = db.execute("select written_rep, sense, trans_list, coalesce(score,0), coalesce(importance,0) from translation where is_good")
cands = collections.defaultdict(dict)
for en, sense, tl, score, imp in rows:
    if not en or en != en.lower() or not EN_OK.match(en): continue
    if sense and BAD_SENSE.search(sense): continue
    for pos, t in enumerate((tl or "").split(" | ")):
        ru = clean_ru(t)
        if not ru: continue
        key = ru.lower()
        mh = muse_hit(en, ru)
        w = imp * 10 + mh * 15 + score / 100.0 - pos * 0.05 + (0.3 if not sense else 0)
        if key not in cands[en] or cands[en][key][0] < w:
            cands[en][key] = (w, ru, mh)

n = 0
with open(out_path, "w", encoding="utf-8") as f:
    for en in sorted(cands):
        best = sorted(cands[en].values(), key=lambda x: -x[0])
        picked, seen = [], set()
        for w, ru, mh in best:
            stem = ru.lower().replace("ё", "е")[:5]
            if stem in seen: continue
            if picked and not mh: continue
            seen.add(stem); picked.append(ru)
            if len(picked) == 2: break
        if picked:
            f.write(en + "\t" + ", ".join(picked) + "\n"); n += 1
print(n, "entries ->", out_path)
