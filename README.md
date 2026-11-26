[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Laika-lgtm/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Laika-lgtm/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

# The World in One Day — Wednesday 25 November 2026

A one-page newspaper front page summarising the world on Wednesday
25 November 2026: **50 stories, 10 regions, 20 fields**, all first
reported on 25 November 2026.

Built for the [news-image-20261125 bounty](https://make.fun/bounty/news-image-20261125)
on make.fun. Referral code: `w2e3vyyb`.

## What is on the page

- **3 hero stories** with original program-drawn illustrations: the US
  proposal for tariffs of up to 20% on 14 economies; the AI rout that
  sank the Kospi 6.2% as SoftBank slid 14.8%; Pakistan's first astronaut
  docking at China's space station.
- **12 illustrated cards**: Hodeidah, Dhaka, Pongkor, Syzran, the UK
  energy cap, Cartagena, UN Women, the Solomons, the LGBT veterans
  apology, the Met review, the Hormuz closure claim (marked CLAIM — not
  independently confirmed), and Cairo.
- **35 also-on stories**, a numbered world map with a pin for every one
  of the 50 stories, a 6-number stat strip, and a UTC timeline.
- **DATE CHECK**: every story happened or was first reported on
  25 November 2026 in at least one time zone. Stories from other days
  are named and excluded (Rosstat war-dead leak, Huawei verdict, Miss
  Universe crown, and 17 more), and the 25-November verification was
  done story by story against Reuters, AP, AFP, BBC, Al Jazeera and
  other wires — including ten replacements for items first believed to
  be 25 November but found to be 24 November or earlier.

## How it is built

`render.py` (Python 3, Pillow only) reads `stories.json` and draws the
whole 1024×1024 page — every illustration is drawn by the program
itself, no external images. `main.py` copies `entry.png` to the output
directory the grader requests.

Run:

```sh
python3 render.py        # writes entry.png (deterministic: two runs are byte-identical)
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## Sources

Reuters · AP · AFP · BBC · Al Jazeera · Xinhua · CMSA · Ofgem · ESA ·
UN Women · AAP · UK media · Yonhap · ABS. Every drawing is original.

## License

MIT — see `LICENSE`.
