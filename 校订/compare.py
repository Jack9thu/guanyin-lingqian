"""Compare 4 mainland sources field by field (Taiwan texts shown as reference).
Writes consensus.json (plurality value per field) and prints a compact worksheet:
  usage: compare.py START END
Lines marked '=' are unanimous among the sources that have them; '?' lines list variants."""
import json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "sources.json"), encoding="utf-8"))
ORDER = ["sy", "51", "72ju", "zy"]
VAR = str.maketrans({"坭": "泥", "啣": "衔", "銜": "衔", "箇": "个"})


def norm(s, field):
    if not s:
        return None
    s = re.sub(r"[\s，,。．.；;、：:！!？?“”\"'（）()【】]", "", s).translate(VAR)
    if field == "palace":
        s = s.translate(str.maketrans({"已": "巳", "戍": "戌"}))
    if field == "title" and s == "典故":
        return None
    if s and len(s) > 40:
        return None
    return s or None


def get(src, n, field, i=None):
    d = S.get(src, {}).get(str(n))
    if not d:
        return None
    v = d.get(field)
    if field == "poem":
        return norm(v[i], field) if v else None
    if field == "level" and v:
        v = v[0]
    return norm(v, field)


FIELDS = [("level", None), ("palace", None), ("title", None)] + [("poem", i) for i in range(4)] + [("meaning", None), ("jieyue", None)]
consensus = {}
lines = []
for n in range(1, 101):
    c = {}
    lines.append(f"## {n}")
    for f, i in FIELDS:
        key = f if i is None else f"p{i + 1}"
        vals = {s: get(s, n, f, i) for s in ORDER}
        cnt = Counter(v for v in vals.values() if v)
        best = cnt.most_common(1)[0][0] if cnt else None
        c[key] = best
        if len(cnt) <= 1:
            lines.append(f" = {key}: {best}")
        else:
            groups = {}
            for s, v in vals.items():
                if v:
                    groups.setdefault(v, []).append(s)
            lines.append(f" ? {key}: " + " | ".join(f"{v}[{','.join(ss)}]" for v, ss in groups.items()) + f"  => {best}")
        if f == "poem":
            refs = []
            for r in ("lc", "tw"):
                d = S.get(r, {}).get(str(n))
                if d and d.get("poem"):
                    refs.append(f"{r}:{d['poem'][i]}")
            if refs and len(cnt) > 1:
                lines.append("     ref " + " ".join(refs))
    consensus[n] = c

json.dump(consensus, open(os.path.join(HERE, "consensus.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
a, b = (int(x) for x in (sys.argv[1:3] if len(sys.argv) > 2 else (1, 100)))
out, on = [], False
for l in lines:
    if l.startswith("## "):
        on = a <= int(l[3:]) <= b
    if on:
        out.append(l)
print("\n".join(out))
