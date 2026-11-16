"""Parse 4 sources of 观音灵签 into sources.json: {source: {n: {level, palace, title, poem[4], meaning, jieyue}}}"""
import html, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

CN = {c: i for i, c in enumerate("零一二三四五六七八九")}


def cn2int(s):
    s = s.strip()
    if s.isdigit():
        return int(s)
    if s == "一百" or s == "百":
        return 100
    if "十" in s:
        a, b = s.split("十")
        return (CN[a] if a else 1) * 10 + (CN[b] if b else 0)
    return CN[s]


def text(path):
    b = open(path, "rb").read()
    m = re.search(rb"charset=[\"']?([\w-]+)", b[:3000])
    enc = (m.group(1).decode().lower() if m else "utf-8")
    enc = "gb18030" if enc in ("gb2312", "gbk", "gb18030") else enc
    t = b.decode(enc, errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    t = t.replace("　", " ").replace("\xa0", " ")
    lines = [l.strip() for l in t.split("\n")]
    return [l for l in lines if l]


def split_poem(lines):
    """join lines and split into 4 seven-char lines"""
    s = "".join(lines)
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = re.sub(r"[\s，,。；;、．.！!？?]", "", s)
    if len(s) != 28:
        return None, s
    return [s[i:i + 7] for i in range(0, 28, 7)], s


def clean(s):
    return re.sub(r"\s+", "", s).strip()


def parse_sy():
    out = {}
    for f in sorted(os.listdir(RAW)):
        if not re.match(r"sy_\d+\.html", f):
            continue
        L = text(os.path.join(RAW, f))
        for i, l in enumerate(L):
            m = re.fullmatch(r"第([一二三四五六七八九十百零]+)\s*(上|中|下)\s*签", l)
            if not m:
                continue
            n = cn2int(m.group(1))
            j = i + 1
            poem_lines = []
            while not re.match(r"[（(]解曰[）)]", L[j]):
                poem_lines.append(L[j]); j += 1
            j += 1
            k = j
            while not L[k].startswith("阅读更多"):
                k += 1
            jie = L[j:k - 1]
            shengyi = L[k - 1]
            j = k + 1
            palace = L[j]; j += 1
            title = L[j]; j += 1
            meaning = L[j]
            poem, raw = split_poem(poem_lines)
            out[n] = dict(level=m.group(2), palace=palace.replace("宫", "") + "宫",
                          title=re.sub(r"^【(古人)?】?|】$", "", title.replace("【古人】", "【")),
                          poem=poem, poem_raw=raw,
                          jieyue=clean("".join(jie)), meaning=clean(meaning), shengyi=shengyi)
    return out


def after(L, key, stop):
    i = L.index(key)
    res = []
    for l in L[i + 1:]:
        if l in stop:
            break
        res.append(l)
    return res


def parse_51():
    out = {}
    for n in range(1, 101):
        p = os.path.join(RAW, f"51_{n}.html")
        if not os.path.exists(p):
            continue
        L = text(p)
        head = next(l for l in L if re.match(r"观音灵签\s*第.+签\s*[:：]", l))
        title = re.sub(r"-抽签网$", "", clean(re.split(r"[:：]", head, 1)[1]))
        level = next(re.search(r"(上|中|下)签", l).group(1) for l in L if l.startswith("吉凶"))
        palace = next(re.search(r"(.宫)", l).group(1) for l in L if l.startswith("宫位"))
        poem, raw = split_poem(after(L, "诗曰", {"诗意"}))
        meaning = clean("".join(after(L, "诗意", {"解曰"})))
        jie = clean("".join(after(L, "解曰", {"仙机", "圣意"})))
        out[n] = dict(level=level, palace=palace, title=title, poem=poem, poem_raw=raw,
                      meaning=meaning, jieyue=jie)
    return out


def parse_72ju():
    out = {}
    for n in range(1, 101):
        p = os.path.join(RAW, f"72ju_{n}.html")
        if not os.path.exists(p):
            continue
        L = text(p)
        i = L.index(f"观音第{n}签")
        L = L[i:]
        g = lambda k: L[L.index(k) + 1]
        poem, raw = split_poem(after(L, "签文", {"卦解"}))
        # NOTE: 72ju labels are swapped: 卦解 holds 解曰 text, 解曰 holds 诗意 text
        out[n] = dict(level=g("吉凶")[0], palace=g("宫位"), title=g("古人"), poem=poem,
                      poem_raw=raw, jieyue=clean("".join(after(L, "卦解", {"解曰"}))),
                      meaning=clean("".join(after(L, "解曰", {"详解"}))))
    return out


def parse_zy():
    out = {}
    for f in os.listdir(RAW):
        if not f.startswith("zy_id"):
            continue
        L = text(os.path.join(RAW, f))
        hd = next((l for l in L if re.fullmatch(r"观音灵签\s*第\d+签概述", l)), None)
        if not hd:
            print("zy no header", f); continue
        n = int(re.search(r"\d+", hd).group())
        L = L[L.index(hd):]
        if "签诗" in L[:8]:
            poem, raw = split_poem(after(L, "签诗", {"诗意", "本签精髓"}))
        else:
            poem, raw = split_poem(after(L, hd, {"吉凶宫位:", "吉凶宫位："}))
        lp = next((l for l in L[:10] if re.search(r"(上|中|下)签.宫", l)), "")
        m = re.search(r"(上上|上|中|下下|下)签(.宫)", lp)
        title = None
        for k, l in enumerate(L):
            if re.fullmatch(r"观音灵签\s*第\d+签图和典故", l):
                title = L[k + 1]; break
        out[n] = dict(level=m.group(1) if m else lp, palace=m.group(2) if m else None, title=title,
                      poem=poem, poem_raw=raw,
                      meaning=clean("".join(after(L, "诗意", {"解曰"}))),
                      jieyue=clean("".join(after(L, "解曰", {"整体解译"}))))
    return out


def parse_lc():
    """Taiwan temple (五甲龍成宮), traditional chars; reference only."""
    out = {}
    for f in os.listdir(RAW):
        if not f.startswith("lc_id"):
            continue
        L = text(os.path.join(RAW, f))
        for k, l in enumerate(L):
            m = re.fullmatch(r"第([一二三四五六七八九十百零]+)籤", l)
            if m and k + 1 < len(L) and re.search(r"[，,、。]$", L[k + 1]):
                n = cn2int(m.group(1))
                poem, raw = split_poem(after(L, l, {"詩　意", "詩 意", "詩意"}))
                mk = next((x for x in L if re.fullmatch(r"詩\s*意", x)), None)
                jk = next((x for x in L if re.fullmatch(r"解\s*曰", x)), None)
                out[n] = dict(poem=poem, poem_raw=raw,
                              meaning=clean("".join(after(L, mk, {jk}))) if mk else None,
                              jieyue=clean("".join(after(L, jk, {"解　說", "解 說", "解說"}))) if jk else None)
                break
    return out


def parse_tw():
    """temples.tw 觀音一百籤 (poems only), traditional; reference only."""
    out = {}
    L = text(os.path.join(RAW, "temples_yin100.html"))
    for l in L:
        m = re.fullmatch(r"第([一二三四五六七八九十百零]+)籤\)\s*(.+)", l)
        if m:
            poem, raw = split_poem([m.group(2)])
            out[cn2int(m.group(1))] = dict(poem=poem, poem_raw=raw)
    return out


if __name__ == "__main__":
    which = sys.argv[1:] or ["sy", "51", "72ju", "zy", "lc", "tw"]
    res = {}
    for w in which:
        try:
            res[w] = globals()["parse_" + w]()
        except Exception as e:
            import traceback; traceback.print_exc()
        print(w, len(res.get(w, {})), "bad poems:",
              [n for n, d in res.get(w, {}).items() if not d["poem"]])
    json.dump(res, open(os.path.join(HERE, "sources.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
