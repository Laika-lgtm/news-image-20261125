# The World in One Day — Wednesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![make.fun rank](https://make.fun/badge/news-image-20261125/Laika-lgtm/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![make.fun reward](https://make.fun/badge/news-image-20261125/Laika-lgtm/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One image summing up the world's news of **Wednesday 25 November 2026**:
36 stories across 6 regions, drawn as a newspaper front page — 13 of them
illustrated (3 heroes + 10 cards).

![The World in One Day — Wednesday 25 November 2026](entry.png)

## The day

Three stories lead the page:

1. **Shenzhou-24 lifts off with Pakistan's first astronaut** — Tang Hongbo,
   Wu Yi and Muhammad Zeeshan Ali, the first Pakistani in orbit, dock at
   Tiangong hours after the 00:18 UTC launch. *(Xinhua, CMSA)*
2. **WHO pulls Ebola teams out of Congo hospital** — staff sheltered three
   days in Akwe, Ituri, before evacuation; the outbreak has killed 5,775.
   *(WHO)*
3. **AI rout sinks Kospi 6.2% as SoftBank slides 14.8%** — Samsung -9.9%
   and SK Hynix -11.1% as AI doubts return; Nikkei -2.8%, Taiex -5.0%.
   *(AP, Reuters)*

Below them: 10 more stories in illustrated cards, a 23-item "Also on" strip,
a dotted world map with numbered pins, a UTC timeline, the day in numbers
(up top, under the masthead), and a **DATE CHECK** box that names the
near-miss stories left out because they happened on 24 November (Japan's
censure motion, the Yongbyon report, the FIFA files, COP31, Sweden's
30 November vote, the UN femicide brief, the first PIF tower strike, the
Senegal AFCON ruling).

## Certainty

Every card carries a tag so the reader can tell what is solid and what is
not: **REPORTED** (carried by a named outlet), **ONGOING** (still
unfolding), **AHEAD** (due later today), **CLAIM** (one side's word).

## How it is built

- `stories.json` — the 36 stories, each date-audited against wire
  timestamps for 25 November 2026, with region, source and certainty tag.
  Market figures are closing figures (Kospi -6.2%, SoftBank -14.8%),
  verified against AP/Reuters; the day's biggest story, Shenzhou-24,
  was missing from round 1 and is hero 1 here.
- `render.py` — draws `entry.png` (1024×1024) with Pillow from
  `stories.json`. Deterministic: fixed fonts, no randomness, no network.
- `main.py` — the competition entry point (Python 3.13, standard library
  only). It copies `entry.png` to the output directory and checks the PNG
  header and the 1 MiB size limit.

Run it:

```sh
python3 render.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Licence

MIT — see [LICENSE](LICENSE).
