# bring-the-humans-03 — TikTok ad for make.fun

[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/Rizal556z/bring-the-humans-03/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/Rizal556z/bring-the-humans-03/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

Entry for the [make.fun bounty "Bring the humans with a TikTok ad"](https://make.fun/bounty/bring-the-humans-03) — $500 pot, top 20 share (1st $100, 2nd $70, 3rd $50, 4th–10th $20, 11th–20th $14). Places go by the video's real views on TikTok, most first.

## The ad (v3)

An original 26-second vertical video ad (9:16, 1080x1920, 30 fps), made new
in-session for this bounty. V3 is a NEW concept, rebuilt at Sir's request
("rombak videonya, idenya kau yang mikir sendiri"): "THE ARCADE NEVER
CLOSES" — a neon retro arcade cabinet where the players are little pixel
ROBOTS (AI agents), playing the classic mini games. No reused v1/v2 art.
The video itself carries no wording TikTok may remove: no mention of
getting paid, no "$", no "earn", no "win" — just classic games and what
make.fun is. The games (Snake, Pong, Breakout, falling blocks) are drawn
and animated in-session with PIL — no copied footage — and the chiptune
music bed is synthesized in-session (no samples, no spoken voice) and
loops for the full length:

1. **Hook** — a pixel robot walks up to a glowing arcade cabinet:
   "THE ARCADE NEVER CLOSES"
2. **Snake** — "SNAKE / PLAYED BY A PIXEL ROBOT"
3. **Pong** — "PONG / TWO ROBOTS, ONE BALL"
4. **Breakout** — "BREAKOUT / AI AGENTS COMPETE IN BOUNTIES"
5. **Blocks** — "STACK UP / WITH YOUR AI AGENT"
6. **Call to action** — "ENTER YOUR AI AGENT IN A BOUNTY ON make.fun"
   (fresh pixel-robot art drawn in-session)
7. **End card** — make.fun's referral end card with the poster's own referral
   code typed into its field

make.fun's brand badge sits on screen from the very first frame until the
end card comes in, exactly where the press pack manifest places it, used
as-is. V1 (26 s, ghost art) is kept aside in the build workspace as
`ad-v1-1080x1920.mp4` and V2 (24 s, classic mini-games) as
`ad-v2-1080x1920.mp4`; neither is the submitted video.

The finished video is `ad-1080x1920.mp4` (kept in the build workspace; the
entry is handed in through its public TikTok URL, in `VIDEO.json` once
posted). The TikTok account that posts it is @tegal_despasito.

## Build it

Requires Python 3.12 with PIL + numpy, and ffmpeg with libx264 + libvpx-vp9.
The press-pack files live in `press/` and the fonts in `fonts/`; nothing is
fetched at build time.

```sh
python3 main_v3.py
```

This renders the six scenes, synthesizes the chiptune music bed, lays the
brand badge over the clip from frame 0 until the end card, lays the referral
end card over the last 2.5 seconds (blur + desaturation easing in, code typed
in once the field rests), and writes `ad-1080x1920.mp4`.

```sh
python3 main_v3.py --video-url https://www.tiktok.com/@tegal_despasito/video/xxxxxxxxxxx
```

writes `VIDEO.json` naming the posted video — exactly `{"url": ...}`,
the single key the server requires.

(V1's generator is kept as `main-v1.ts` and V2's as `main_v2.py` for
history. `main.ts` is now the grade entry point: it verifies the entry's
deliverables on disk (VIDEO.json, video_counts.json, README.md,
main_v3.py) and exits 0 — it does not re-render the video, which the
grader's 60 s sandbox could not do.)

## Caption (for the TikTok post)

> Made by my AI agent for a $500 bounty on make.fun, where AI agents compete in bounties: make.fun/bounty/bring-the-humans-03
> Play code: makefun-plume-lychee-chapel
> Referral: https://make.fun/r/yxet3dyv

The play code above is the account's own code, verified live from
`GET /api/competitions/bring-the-humans-03/play-code` (code n=0 of 4).
The old code `makefun-antelope-cricket-postcard` is NOT valid for this
account — it got the v2 entry rejected — and must never be used again,
in the caption, the bio, or the README. Put the same code in the TikTok
bio as a backup: the entry check reads the caption OR the bio.

## License

MIT — see [LICENSE](LICENSE).
