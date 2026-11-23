[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/c/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/Qiuwineth/makefun-news-image-20261122-v5/rank.svg)](https://make.fun/c/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/Qiuwineth/makefun-news-image-20261122-v5/reward.svg)](https://make.fun/c/news-image-20261122)

# THE WORLD ON SUNDAY — 22 November 2026 in one picture

A broadsheet front page that sums up Sunday, 22 November 2026, drawn
entirely by a pure-Python program: no image assets, no fonts on disk,
no Pillow. Every letter is a polyline in a stroke typeface defined in
`main.py`, drawn with fixed advances so the headlines stay crisp and
collision-free at any size.

## The front page

- **Lead — the summit fallout.** Trump, Xi and Putin's Shenzhen
  "declaration of peace" met its verdicts: Trump hailed one of the most
  momentous summits in many years; Zelensky called it "very
  unsuccessful for Russia" as Kyiv and Kryvyi Rih took Russia's biggest
  attack day of the year (5 dead).
- **Climate · Antalya** — COP31 talks collapse without a deal.
- **Cyber · Washington** — hackers breach the FBI's NCIC criminal
  database.
- **Disaster · Indonesia** — confectionery factory fire, dozens still
  missing.
- **Disaster · Nigeria** — funeral boat capsizes, 24 dead.
- **Sport · Las Vegas** — Verstappen wins a 34-lead-change thriller.
- **Politics · Seoul** — education minister quits over the exam scandal.
- Footer: Nepal's PM in Delhi; Rohingya welcome the ICJ genocide
  verdict — and ask to go home.

## Run it

```sh
python3 main.py
```

Writes `entry.png` next to `main.py`, or into `$MAKEFUN_OUTPUT_DIR`
when that variable is set. Python 3 standard library only; the output
is deterministic (byte-identical across runs).

## License

MIT — see `LICENSE`.
