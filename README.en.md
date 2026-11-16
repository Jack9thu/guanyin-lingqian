# Guanyin Lingqian (观音灵签)

[中文](README.md) | **English**

A web page for drawing from the 100 Guanyin fortune sticks (观音灵签): shake the stick cylinder, cast the moon blocks to ask for confirmation, then read the poem and its interpretation. It is a single HTML file with no external dependencies and works on phones and desktops.

**Try it online: <https://jack9thu.github.io/guanyin-lingqian/>**

You can also download `index.html` and open it in a browser; it works offline.

> A piece of traditional folk culture, for entertainment only. The page itself is in Chinese.

## How it works

Two modes can be switched at the top of the page:

| Mode | Casts needed | Limit |
| --- | --- | --- |
| Daily fortune (每日运势) | 1 "holy cast" | One stick while the tab stays open; cleared when the tab is closed |
| Fortune drawing (运势抽签) | 3 holy casts in a row | Unlimited, one question per stick; "Ask another question" after a stick is confirmed |

The flow is the same in both modes:

1. Think of your question, then tap the cylinder or "诚心求签" (draw a stick). The cylinder shakes for about 1.7 s and a stick drops beside it.
2. Tap "掷筊" to cast the moon blocks, once per tap, until you reach the number of holy casts (one flat side up, one round side up) the mode requires.
3. A "laughing cast" (both flat) or "yin cast" (both round) voids the stick; tap "重新求签" to start over.
4. Once confirmed, a card shows the stick number, its rank (upper in vermilion, middle in ochre, lower in grey), palace, story title, the poem set vertically, its meaning and the interpretation (解曰). A few sticks carry an editorial note.

You cannot switch modes while the shaking or casting animation is playing; at any other time you can. Each mode keeps its own progress, so switching away and back (mid-draw, after success, or after a failed cast) leaves everything as it was.

## Rules and parameters

- **Each cast**: holy 50%, laughing 25%, yin 25%. To change this, edit `P_SHENG` at the top of the script in `校订/template.html`; the remainder is split evenly between laughing and yin casts.
  - Daily fortune succeeds on one try with probability 50%, about 2 rounds on average.
  - Fortune drawing needs three holy casts in a row: 12.5% per try, about 8 rounds on average.
- **Daily stick**: after success, today's date and the stick number are stored in the browser's `sessionStorage`. Reloading or switching back shows the same stick; closing the tab clears it, so you can draw again next time. It also expires at midnight. Nothing is stored if the casts fail. Long-term records left in `localStorage` by older versions are removed when the page opens.
- Fortune-drawing results last only while the page is open (switching modes keeps them); reloading or closing resets them.
- The page remembers which mode you were last on (in `localStorage`; a preference only, no results).
- After a daily stick is confirmed, a "清除今日记录" (clear today's record) link appears at the bottom, for testing without closing the tab.
- If storage is disabled (e.g. some private-browsing modes), drawing still works; the daily stick just isn't locked.
- Stick numbers and casts use `crypto.getRandomValues`.
- All data stays in your own browser; the page makes no network requests and uploads nothing.

## The texts

The text is the most widely circulated mainland-Chinese edition of the Guanyin Lingqian (stick 1 is "钟离成道"). It was compiled by comparing four sources character by character (one temple website and three other websites), with the common Taiwanese edition as a reference, correcting more than fifty typos. Only the story titles are kept, not the story narratives of unclear origin. The rank distribution is 23 upper, 59 middle and 18 lower.

Sources, selection rules and every change are documented in [`校订/校订记录.en.md`](校订/校订记录.en.md) (the full change table is in the [Chinese version](校订/校订记录.md)).

## Files

```
guanyin-lingqian/
├── index.html         The finished page, a single file with the texts embedded (also the GitHub Pages home page)
├── LICENSE            MIT
└── 校订/              Tools for comparing sources and building the page (Python 3.8+, standard library only)
    ├── 校订记录.md     Sources, rules, change table (校订记录.en.md: English version)
    ├── sources.json    Parsed text from each source
    ├── decisions.py    Manual choices and editorial notes
    ├── fetch.py / parse.py / compare.py / make_final.py / build.py
    ├── template.html   Page template; build.py fills in the texts
    ├── favicon.svg     Icon source (vermilion seal with a Kaiti "签", glyph converted to paths), embedded in the template <head>
    └── consensus.json / final.json   Intermediate results
```

To change the page's look or logic, edit `校订/template.html`, then run `python -I build.py` inside `校订/` to regenerate `index.html` (see the revision record for the full pipeline). Editing `index.html` directly also works, but it will be overwritten on the next build.

## License

The code is released under the [MIT](LICENSE) license. The stick texts are traditional folk texts; see the revision record for their sources.
