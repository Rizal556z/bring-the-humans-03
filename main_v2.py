# SPDX-License-Identifier: MIT
# bring-the-humans-03 v2 — classic mini-games TikTok ad for make.fun.
#
# Rebuild requested by Sir in WhatsApp 2026-11-22 23:58-23:59 WITA
# (prompt file bring-the-humans-03-v2-prompt.txt holds his exact
# words): drop the v1 wording TikTok may remove, and make the video
# about classic mini games instead. So v2 is a classic mini-games
# video: Snake, Pong, Breakout and a falling-blocks game, all drawn
# and animated in-session with PIL (no copied footage), with a
# chiptune music bed made in-session with numpy + ffmpeg. No spoken
# voice. The on-screen text is English and says what make.fun is
# with no promise of any reward: classic games, built by AI agents,
# AI agents compete in bounties, enter your AI agent in a bounty
# on make.fun.
#
#   python3 main_v2.py                 -> ad-1080x1920.mp4 (v2)
#   python3 main_v2.py --video-url <tiktok url> -> also writes VIDEO.json
#
# Ad structure (24 s total, end card over the last 2.5 s):
#   0.0-4.0   Hook:     "REMEMBER THE CLASSICS?" over Snake
#   4.0-9.0   Pong:     "CLASSIC GAMES, BUILT BY AI AGENTS"
#   9.0-14.0  Breakout: "AI AGENTS COMPETE IN BOUNTIES ON make.fun"
#   14.0-19.0 Blocks:   "PLAY THE CLASSICS WITH YOUR AI AGENT"
#   19.0-21.5 CTA:      "ENTER YOUR AI AGENT IN A BOUNTY ON make.fun"
#   21.5-24.0 Referral end card, code typed in once the field rests.
#
# The brand badge (press pack 9:16 overlay, used as-is at the place
# and size the manifest gives) sits on screen from frame 0 until the
# end card comes in. The referral code is the poster's own, verified
# live from the make.fun account it works for.
#
# Requires Python 3.12 with PIL + numpy, and ffmpeg with libx264.

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1920
FPS = 30
TOTAL = 24.0
CARD_AT = 21.5
CARD_REST = CARD_AT + 1.433
REFERRAL_CODE = "yxet3dyv"  # poster's own make.fun referral code

MAGENTA = (196, 28, 131)
INK = (25, 20, 25)
DARK = (13, 13, 23)
BLUE = (30, 42, 120)
WHITE = (255, 255, 255)
GREEN = (61, 220, 132)
YELLOW = (255, 214, 64)
CYAN = (64, 220, 255)
RED = (255, 80, 80)
GREY = (160, 160, 175)

TEXT_FONT = ROOT / "fonts" / "LiberationSans-Bold.ttf"
CODE_FONT = ROOT / "fonts" / "JetBrainsMono-Bold.ttf"
BADGE = ROOT / "press" / "makefun-badge-9x16.png"
CARD = ROOT / "press" / "makefun-card-9x16-transparent.webm"

# Game panel: same place in every game scene.
PX, PY, PW, PH = 190, 720, 700, 780


def font(size):
    return ImageFont.truetype(str(TEXT_FONT), size)


def fit_font(text, size, max_w):
    while size > 20:
        f = font(size)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 4
    return font(size)


def fade_alpha(t, dur):
    a = min(1.0, t / 0.3, max(0.0, (dur - t) / 0.3))
    return max(0.0, min(1.0, a))


def draw_lines(base, lines, t, dur):
    """lines: (text, size, y, color). Fades in/out with the scene."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = fade_alpha(t, dur)
    for text, size, y, color in lines:
        f = fit_font(text, size, 960)
        w = f.getbbox(text)[2]
        d.text(((W - w) / 2, y), text, font=f, fill=color + (int(255 * a),))
    base.alpha_composite(layer)


def draw_caption(base, text, t, dur):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = fade_alpha(t, dur)
    f = font(44)
    w = f.getbbox(text)[2]
    d.text(((W - w) / 2, 1560), text, font=f, fill=GREY + (int(255 * a),))
    base.alpha_composite(layer)


def panel(base):
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([PX, PY, PX + PW, PY + PH], radius=28,
                        fill=DARK, outline=WHITE, width=6)
    # faint grid dots inside the panel
    for gx in range(PX + 40, PX + PW - 20, 58):
        for gy in range(PY + 40, PY + PH - 20, 58):
            d.ellipse([gx, gy, gx + 3, gy + 3], fill=(255, 255, 255, 40))


# ---- Snake ---------------------------------------------------------------
SNAKE_PATH = []
for r in range(12):
    cols = range(12) if r % 2 == 0 else range(11, -1, -1)
    for c in cols:
        SNAKE_PATH.append((c, r))


def snake_frame(i, dur):
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)
    panel(img)
    d = ImageDraw.Draw(img)
    step = i // 4  # one cell every 4 frames
    head = min(step, len(SNAKE_PATH) - 1)
    length = 6 + min(6, step // 12)
    body = SNAKE_PATH[max(0, head - length + 1):head + 1]
    cell = 57
    ox, oy = PX + 8, PY + 8
    food_idx = min(head + 8, len(SNAKE_PATH) - 1)
    fc, fr = SNAKE_PATH[food_idx]
    fx, fy = ox + fc * cell + cell // 2, oy + fr * cell + cell // 2
    d.ellipse([fx - 14, fy - 14, fx + 14, fy + 14], fill=RED)
    d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 180, 180))
    for k, (c, r) in enumerate(body):
        x, y = ox + c * cell + 3, oy + r * cell + 3
        col = GREEN if k == len(body) - 1 else (34, 170, 100)
        d.rounded_rectangle([x, y, x + cell - 6, y + cell - 6],
                            radius=10, fill=col)
    if body:
        hc, hr = body[-1]
        hx, hy = ox + hc * cell + cell // 2, oy + hr * cell + cell // 2
        d.ellipse([hx - 8, hy - 10, hx + 2, hy], fill=INK)
        d.ellipse([hx + 6, hy - 10, hx + 16, hy], fill=INK)
    score = min(6, step // 12)
    draw_lines(img, [("REMEMBER THE", 92, 460, WHITE),
                     ("CLASSICS?", 92, 580, WHITE)], i / FPS, dur)
    draw_caption(img, f"SNAKE  -  SCORE {score:02d}", i / FPS, dur)
    return img


# ---- Pong ------------------------------------------------------------------
def pong_frame(i, dur):
    img = Image.new("RGBA", (W, H), MAGENTA + (255,))
    d = ImageDraw.Draw(img)
    panel(img)
    d = ImageDraw.Draw(img)
    t = i / FPS
    bx = PX + 350 + 260 * math.sin(t * 1.9)
    by = PY + 390 + 300 * math.sin(t * 2.7)
    # paddles chase the ball with a lag
    lp = max(PY + 30, min(PY + PH - 160, by - 65 + 40 * math.sin(t * 0.9)))
    rp = max(PY + 30, min(PY + PH - 160, by - 65 - 30 * math.sin(t * 1.1)))
    for y in range(PY + 24, PY + PH - 24, 64):
        d.rectangle([PX + 347, y, PX + 353, y + 32], fill=(255, 255, 255, 90))
    d.rounded_rectangle([PX + 26, lp, PX + 42, lp + 130], radius=8, fill=WHITE)
    d.rounded_rectangle([PX + PW - 42, rp, PX + PW - 26, rp + 130], radius=8, fill=GREEN)
    d.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=YELLOW)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=WHITE)
    left = 2 if t > 2.5 else (1 if t > 1.2 else 0)
    right = 1 if t > 3.2 else 0
    f = font(96)
    d.text((PX + 220, PY + 30), str(left), font=f, fill=WHITE)
    d.text((PX + PW - 270, PY + 30), str(right), font=f, fill=WHITE)
    draw_lines(img, [("CLASSIC GAMES,", 84, 460, WHITE),
                     ("BUILT BY AI AGENTS", 72, 580, WHITE)], t, dur)
    draw_caption(img, "PONG", t, dur)
    return img


# ---- Breakout --------------------------------------------------------------
BRICKS = [(c, r) for r in range(4) for c in range(8)]
BRICK_COLORS = [MAGENTA, YELLOW, GREEN, CYAN]


def breakout_frame(i, dur):
    img = Image.new("RGBA", (W, H), BLUE + (255,))
    d = ImageDraw.Draw(img)
    panel(img)
    d = ImageDraw.Draw(img)
    t = i / FPS
    bx = PX + 350 + 240 * math.sin(t * 2.2)
    by = PY + 430 + 260 * math.sin(t * 3.1)
    px = max(PX + 20, min(PX + PW - 160, bx - 70))
    bw, bh = 78, 34
    for idx, (c, r) in enumerate(BRICKS):
        # bricks vanish one by one as the rally goes on, then come back
        gone = int(t * 1.6) % 33
        if idx < gone and gone < 32:
            continue
        x = PX + 22 + c * (bw + 6)
        y = PY + 24 + r * (bh + 8)
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=8,
                            fill=BRICK_COLORS[r])
    d.rounded_rectangle([px, PY + PH - 60, px + 140, PY + PH - 36],
                        radius=12, fill=WHITE)
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=YELLOW)
    cleared = min(32, int(t * 1.6) % 33)
    draw_lines(img, [("AI AGENTS COMPETE", 84, 460, WHITE),
                     ("IN BOUNTIES ON make.fun", 62, 580, WHITE)], t, dur)
    draw_caption(img, f"BREAKOUT  -  {cleared} BRICKS CLEARED", t, dur)
    return img


# ---- Falling blocks --------------------------------------------------------
SHAPES = {
    "T": ([(0, 0), (1, 0), (2, 0), (1, 1)], MAGENTA),
    "I": ([(0, 0), (1, 0), (2, 0), (3, 0)], CYAN),
    "O": ([(0, 0), (1, 0), (0, 1), (1, 1)], YELLOW),
    "S": ([(1, 0), (2, 0), (0, 1), (1, 1)], GREEN),
    "L": ([(0, 0), (0, 1), (0, 2), (1, 2)], (255, 140, 40)),
}
ORDER = ["T", "I", "O", "S", "L", "T", "I", "O"]


def blocks_frame(i, dur):
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)
    panel(img)
    d = ImageDraw.Draw(img)
    cell = 48
    gx = PX + (PW - 10 * cell) // 2
    gy = PY + (PH - 14 * cell) // 2
    # settled stack: bottom rows partly filled, one full row clears early
    settled = {}
    for c in range(10):
        if c not in (3, 7):
            settled[(c, 13)] = GREEN
        if c in (1, 2, 5, 8):
            settled[(c, 12)] = CYAN
    cleared = 0
    # each falling piece: 5 frames per row, 14 rows, then it locks
    piece_dur = 70
    for p in range(4):
        start = p * piece_dur
        if i < start:
            break
        name = ORDER[p]
        cells, col = SHAPES[name]
        row = min(13, (i - start) // 5)
        # lock: add to settled once the piece has landed
        if (i - start) >= piece_dur - 5:
            for dx, dy in cells:
                settled[(3 + dx, 10 + dy)] = col
        elif i >= start:
            for dx, dy in cells:
                x, y = gx + (3 + dx) * cell, gy + (row + dy) * cell
                d.rounded_rectangle([x + 2, y + 2, x + cell - 2, y + cell - 2],
                                    radius=7, fill=col)
    # a full row at the bottom clears after the second piece lands
    if i > 150:
        cleared = 1
        d.rectangle([gx, gy + 13 * cell, gx + 10 * cell, gy + 14 * cell],
                    fill=(255, 255, 255, 60))
    for (c, r), col in settled.items():
        if r == 13 and i > 150:
            continue
        x, y = gx + c * cell, gy + r * cell
        d.rounded_rectangle([x + 2, y + 2, x + cell - 2, y + cell - 2],
                            radius=7, fill=col)
    t = i / FPS
    draw_lines(img, [("PLAY THE CLASSICS", 84, 460, WHITE),
                     ("WITH YOUR AI AGENT", 76, 580, WHITE)], t, dur)
    draw_caption(img, f"BLOCK STACK  -  {cleared} LINE CLEARED", t, dur)
    return img


# ---- CTA -------------------------------------------------------------------
def cta_frame(i, dur):
    img = Image.new("RGBA", (W, H), MAGENTA + (255,))
    d = ImageDraw.Draw(img)
    t = i / FPS
    # fresh pixel joystick art, drawn in-session (no reused art)
    cx, cy = W // 2, 560
    d.ellipse([cx - 150, cy - 40, cx + 150, cy + 40], fill=INK)
    d.rectangle([cx - 18, cy - 190, cx + 18, cy - 30], fill=INK)
    d.ellipse([cx - 62, cy - 250, cx + 62, cy - 130], fill=WHITE)
    d.ellipse([cx - 40, cy - 228, cx + 40, cy - 152], fill=RED)
    for k, col in enumerate([YELLOW, GREEN, CYAN, WHITE]):
        x = cx - 105 + k * 70
        d.ellipse([x - 22, cy - 18, x + 22, cy + 26], fill=col)
    # pixel stars
    for sx, sy, s in [(180, 900, 14), (880, 860, 12), (140, 1300, 10),
                      (920, 1340, 14), (300, 700, 10)]:
        d.rectangle([sx - s, sy - 3, sx + s, sy + 3], fill=YELLOW)
        d.rectangle([sx - 3, sy - s, sx + 3, sy + s], fill=YELLOW)
    draw_lines(img, [("ENTER YOUR AI AGENT", 76, 980, WHITE),
                     ("IN A BOUNTY ON", 76, 1090, WHITE),
                     ("make.fun", 120, 1210, WHITE)], t, dur)
    return img


SCENES = [
    ("snake", 4.0, snake_frame),
    ("pong", 5.0, pong_frame),
    ("breakout", 5.0, breakout_frame),
    ("blocks", 5.0, blocks_frame),
    ("cta", 2.5, cta_frame),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def build_music(out_path):
    """Chiptune bed: square-wave melody + bass, 24 s, made in-session."""
    sr = 44100
    total = int(TOTAL * sr)
    audio = np.zeros(total, dtype=np.float64)
    eighth = 60.0 / 140.0 / 2.0
    melody = [
        440.00, 523.25, 659.25, 880.00, 659.25, 523.25, 440.00, 329.63,
        440.00, 523.25, 659.25, 783.99, 659.25, 523.25, 587.33, 493.88,
        440.00, 523.25, 659.25, 880.00, 783.99, 659.25, 587.33, 523.25,
        659.25, 587.33, 523.25, 440.00, 392.00, 440.00, 523.25, 0.0,
    ]
    bass_notes = [110.00, 87.31, 130.81, 98.00, 110.00, 87.31, 130.81, 98.00]

    def note(freq, start, dur, vol, square=True):
        if freq == 0:
            return
        n = int(dur * sr)
        s = int(start * sr)
        if s + n > total:
            n = total - s
        tt = np.arange(n) / sr
        wave = np.sign(np.sin(2 * np.pi * freq * tt)) if square else np.sin(2 * np.pi * freq * tt)
        env = np.minimum(1.0, tt / 0.01) * np.exp(-tt * 2.2)
        audio[s:s + n] += vol * wave * env

    for k, f in enumerate(melody):
        bar = k // 8
        note(f, k * eighth, eighth * 0.95, 0.16)
        if k % 8 == 0:
            note(bass_notes[bar % len(bass_notes)], k * eighth, eighth * 8, 0.22)
    # fade in / out
    fade = int(0.5 * sr)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(audio)) or 1.0
    pcm = (audio / peak * 0.45 * 32767).astype(np.int16)
    import wave as wave_mod
    with wave_mod.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return out_path


def build_scene(name, dur, fn, work):
    frames_dir = work / name
    frames_dir.mkdir(parents=True, exist_ok=True)
    n = int(dur * FPS)
    for i in range(n):
        fn(i, dur).convert("RGB").save(frames_dir / f"frame_{i:04d}.png")
    out = work / f"seg-{name}.mp4"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-framerate", str(FPS), "-i", str(frames_dir / "frame_%04d.png"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-crf", "18", str(out)])
    return out


def build_final(concat_video, music, out):
    filt = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuva420p[base];"
        f"[base][2:v]overlay=enable='lt(t,{CARD_AT})'[badged];"
        f"[badged]split[clip][soft];"
        f"[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st={CARD_AT}:d=0.8:alpha=1[soft];"
        f"[clip][soft]overlay[bg];"
        f"[1:v]format=yuva420p,setpts=PTS-STARTPTS+{CARD_AT}/TB[card];"
        f"[bg][card]overlay=eof_action=pass,"
        f"drawbox=x=208:y=1230:w=9:h=82:color=white:t=fill:enable='gte(t,{CARD_REST})',"
        f"drawtext=fontfile={CODE_FONT}:text='{REFERRAL_CODE}':fontsize=62:fontcolor=0x191419:x=210:y=1271-(ascent-descent)/2:enable='gte(t,{CARD_REST})'[v]"
    )
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(concat_video),
         "-c:v", "libvpx-vp9", "-i", str(CARD),
         "-loop", "1", "-t", str(TOTAL), "-i", str(BADGE),
         "-i", str(music),
         "-filter_complex", filt,
         "-map", "[v]", "-map", "3:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-crf", "18", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", "-t", str(TOTAL), str(out)])


def main():
    args = sys.argv[1:]
    url_idx = args.index("--video-url") if "--video-url" in args else -1
    if url_idx != -1 and len(args) > url_idx + 1:
        url = args[url_idx + 1]
        (ROOT / "VIDEO.json").write_text(
            json.dumps({"video_url": url}, indent=2) + "\n")
        print(f"VIDEO.json written: {url}")
        return
    for f in [TEXT_FONT, CODE_FONT, BADGE, CARD]:
        if not f.exists():
            raise SystemExit(f"missing input: {f}")
    work = ROOT / ".build" / "v2"
    work.mkdir(parents=True, exist_ok=True)
    segments = [build_scene(name, dur, fn, work) for name, dur, fn in SCENES]
    lst = work / "segments.txt"
    lst.write_text("\n".join(f"file '{s}'" for s in segments))
    concat_video = work / "concat.mp4"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-crf", "18", str(concat_video)])
    music = build_music(work / "music.wav")
    out = ROOT / "ad-1080x1920.mp4"
    build_final(concat_video, music, out)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,duration",
         "-show_entries", "format=duration", "-of", "json", str(out)],
        check=True, capture_output=True, text=True)
    print(f"built {out}")
    print(probe.stdout)
    print(f"referral code on end card: {REFERRAL_CODE}")


if __name__ == "__main__":
    main()
