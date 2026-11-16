"""Download 观音灵签 pages from 4 sources into raw/ (polite, resumable)."""
import os, re, sys, time, urllib.request, ssl

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        return
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            data = urllib.request.urlopen(req, timeout=30, context=ctx).read()
            open(path, "wb").write(data)
            time.sleep(0.6)
            return
        except Exception as e:  # noqa
            print("retry", url, e, file=sys.stderr)
            time.sleep(3)
    print("FAILED", url, file=sys.stderr)


# 1. temple: shuiyuegong (10 pages x 10)
for pid in [294, 401, 424, 561, 579, 593, 607, 620, 635, 650]:
    get(f"https://www.shuiyuegong.com.my/?page_id={pid}", os.path.join(RAW, f"sy_{pid}.html"))

# 2. 51chouqian & 3. 72ju
for n in range(1, 101):
    get(f"https://www.51chouqian.com/guanyinlingqian/{n}.html", os.path.join(RAW, f"51_{n}.html"))
    get(f"https://www.72ju.net/guanyin/?act=jq&qid={n}", os.path.join(RAW, f"72ju_{n}.html"))

# 4. zhouyi.cc: ids from index page
idx = open(os.path.join(RAW, "zy_list.html"), encoding="utf-8", errors="replace").read()
ids = sorted(set(re.findall(r"guanyin/(\d+)\.html", idx)), key=int)
for i in ids:
    get(f"https://m.zhouyi.cc/lingqian/guanyin/{i}.html", os.path.join(RAW, f"zy_id{i}.html"))
print("done", len(os.listdir(RAW)))
