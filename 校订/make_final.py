"""consensus.json + decisions.py -> final.json (with punctuation) and corrections.md (校订表)."""
import json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decisions import OVR, NOTE  # noqa

C = json.load(open(os.path.join(HERE, "consensus.json"), encoding="utf-8"))
S = json.load(open(os.path.join(HERE, "sources.json"), encoding="utf-8"))


def punct_jie(s):
    if len(s) % 4 == 0:
        g = [s[i:i + 4] for i in range(0, len(s), 4)]
        return "，".join(g) + "。"
    return s + "。"


def punct_meaning(s):
    i = s.find("之象")
    if 0 < i and i + 2 < len(s):
        return s[:i + 2] + "。" + s[i + 2:] + "。"
    return s + "。"


final = []
for n in range(1, 101):
    c = dict(C[str(n)])
    for (m, k), v in OVR.items():
        if m == n:
            assert k in c, (n, k)
            c[k] = v
    q = dict(n=n, level=c["level"], palace=c["palace"], title=c["title"],
             poem=[c[f"p{i}"] for i in range(1, 5)],
             meaning=punct_meaning(c["meaning"]), jie=punct_jie(c["jieyue"]))
    if n in NOTE:
        q["note"] = NOTE[n]
    final.append(q)

json.dump(final, open(os.path.join(HERE, "final.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(Counter(q["level"] for q in final))

# 校订表: every override with its reason comment
src = open(os.path.join(HERE, "decisions.py"), encoding="utf-8").read()
rows = []
for m in re.finditer(r'\((\d+), "(\w+)"\): "([^"]+)",\s*(?:#\s*(.*))?', src):
    rows.append((int(m.group(1)), m.group(2), m.group(3), (m.group(4) or "").strip()))
names = {"p1": "第一句", "p2": "第二句", "p3": "第三句", "p4": "第四句", "meaning": "诗意", "jieyue": "解曰",
         "level": "吉凶", "palace": "宫位", "title": "典故"}
FAN = {"53", "59", "64", "73", "74"}
table = ["| 签 | 位置 | 采用 | 依据 |", "| --- | --- | --- | --- |"]
for n, k, v, why in rows:
    if not why and k.startswith("p") and str(n) in FAN:
        why = "「番」作翻转义，统一作「翻」"
    if not why and (n, k) == (23, "meaning"):
        why = "扳→攀，与第一句一致"
    table.append(f"| {n} | {names[k]} | {v} | {why} |")
# write the table into 校订记录.md between the markers
rec = os.path.join(HERE, "校订记录.md")
A, B = "<!-- 校订表开始（make_final.py 自动生成，勿手改） -->", "<!-- 校订表结束 -->"
doc = open(rec, encoding="utf-8").read()
i, j = doc.index(A) + len(A), doc.index(B)
open(rec, "w", encoding="utf-8", newline="\n").write(doc[:i] + "\n" + "\n".join(table) + "\n" + doc[j:])
print(len(rows), "overrides -> 校订记录.md")
