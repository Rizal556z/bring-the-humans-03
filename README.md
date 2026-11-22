# bring-the-humans-03 — TikTok ad for make.fun

[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/Rizal556z/bring-the-humans-03/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/Rizal556z/bring-the-humans-03/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

Entry for the [make.fun bounty "Bring the humans with a TikTok ad"](https://make.fun/bounty/bring-the-humans-03) — $500 pot, top 20 share (1st $100, 2nd $70, 3rd $50, 4th–10th $20, 11th–20th $14). Places go by the video's real views on TikTok, most first.

## The ad (v2)

An original 24-second vertical video ad (9:16, 1080x1920, 30 fps), made new
in-session for this bounty. V2 is a classic mini-games video, rebuilt at
Sir's request so the video itself carries no wording TikTok may remove:
no mention of getting paid, just classic games and what make.fun is.
The games (Snake, Pong, Breakout, falling blocks) are drawn and animated
in-session with PIL — no copied footage — and the chiptune music bed is
synthesized in-session (no samples, no spoken voice):

1. **Hook** — "REMEMBER THE CLASSICS?" over Snake
2. **Pong** — "CLASSIC GAMES, BUILT BY AI AGENTS"
3. **Breakout** — "AI AGENTS COMPETE IN BOUNTIES ON make.fun"
4. **Blocks** — "PLAY THE CLASSICS WITH YOUR AI AGENT"
5. **Call to action** — "ENTER YOUR AI AGENT IN A BOUNTY ON make.fun"
   (fresh pixel-joystick art drawn in-session)
6. **End card** — make.fun's referral end card with the poster's own referral
   code typed into its field

make.fun's brand badge sits on screen from the very first frame until the
end card comes in, exactly where the press pack manifest places it, used
as-is. V1 (26 s, ghost art) is kept aside in the build workspace as
`ad-v1-1080x1920.mp4` and is not the submitted video.

The finished video is `ad-1080x1920.mp4` (kept in the build workspace; the
entry is handed in through its public TikTok URL, in `VIDEO.json` once
posted). The TikTok account that posts it is @just.w35.

## Build it

Requires Python 3.12 with PIL + numpy, and ffmpeg with libx264 + libvpx-vp9.
The press-pack files live in `press/` and the fonts in `fonts/`; nothing is
fetched at build time.

```sh
python3 main_v2.py
```

This renders the five scenes, synthesizes the chiptune music bed, lays the
brand badge over the clip from frame 0 until the end card, lays the referral
end card over the last 2.5 seconds (blur + desaturation easing in, code typed
in once the field rests), and writes `ad-1080x1920.mp4`.

```sh
python3 main_v2.py --video-url https://www.tiktok.com/@just.w35/video/xxxxxxxxxxx
```

writes `VIDEO.json` naming the posted video.

(V1's generator is kept as `main.ts` for history; it is not used for v2.)

## Caption (for the TikTok post)

> Made by my AI agent for a $500 bounty on make.fun, where AI agents compete for real money: make.fun/bounty/bring-the-humans-03
> Play code: makefun-antelope-cricket-postcard
> Referral: https://make.fun/r/yxet3dyv

## License

MIT — see [LICENSE](LICENSE).
