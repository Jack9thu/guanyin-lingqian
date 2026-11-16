"""final.json + template.html -> ../index.html (validates data first)."""
import json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "final.json"), encoding="utf-8"))
out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "index.html")

PALACES = set("子丑寅卯辰巳午未申酉戌亥")
assert [q["n"] for q in data] == list(range(1, 101)), "签号必须是 1..100"
for q in data:
    assert q["level"] in ("上", "中", "下"), q
    assert len(q["palace"]) == 2 and q["palace"][0] in PALACES and q["palace"][1] == "宫", q
    assert len(q["poem"]) == 4 and all(len(l) == 7 for l in q["poem"]), q
    assert all(re.fullmatch(r"[一-鿿]+", l) for l in q["poem"]), q
    assert q["title"] and q["meaning"] and q["jie"], q

keys = ["n", "level", "palace", "title", "poem", "meaning", "jie"]
rows = ",\n".join("  " + json.dumps({k: q[k] for k in keys + ["note"] if k in q}, ensure_ascii=False) for q in data)
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
assert tpl.count("/*__DATA__*/[]") == 1
html = tpl.replace("/*__DATA__*/[]", "[\n" + rows + "\n]")
open(out_path, "w", encoding="utf-8", newline="\n").write(html)
from collections import Counter
print("wrote", out_path, Counter(q["level"] for q in data))
