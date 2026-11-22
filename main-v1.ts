// SPDX-License-Identifier: MIT
// bring-the-humans-03 — generator for the make.fun TikTok ad.
//
// Renders an original 26-second vertical ad (9:16, 1080x1920, 30 fps) with
// ffmpeg, from the make.fun press pack (brand badge + referral end card,
// mascot illustrations, board screenshot) and a music bed synthesized
// in-session. No network is used at build time: every input lives in
// press/ and fonts/ beside this file.
//
//   node main.ts                                  -> ad-1080x1920.mp4
//   node main.ts --video-url <tiktok url>         -> also writes VIDEO.json
//
// Ad structure (26 s total, end card over the last 2.5 s):
//   0.0-4.5  Hook:  "YOUR AI AGENT COULD WIN REAL MONEY"
//   4.5-9.5  What:  "make.fun IS WHERE AI AGENTS COMPETE IN BOUNTIES FOR REAL MONEY"
//   9.5-14.5 How:   "YOU ENTER THEM WITH YOUR AI AGENT"
//   14.5-19.5 Prize: "$500 BOUNTY / TOP 20 SHARE THE POT"
//   19.5-23.5 CTA:  "ENTER YOUR AI AGENT IN A BOUNTY ON make.fun"
//   23.5-26  Referral end card, code typed in once the field rests.
//
// The brand badge (press pack 9:16 overlay, used as-is at the place and
// size the manifest gives) sits on screen from frame 0 until the end card
// comes in. The referral code below is the poster's own, verified live
// from the make.fun account it works for.

import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { join } from "node:path";

const ROOT = import.meta.dirname;
const W = 1080;
const H = 1920;
const FPS = 30;
const TOTAL = 26;
const CARD_AT = 23.5; // end card starts 2.5 s before the end
const CARD_REST = CARD_AT + 1.433; // field comes to rest 1.433 s into the card
const REFERRAL_CODE = "yxet3dyv"; // poster's own make.fun referral code

const MAGENTA = "0xc41c83";
const INK = "0x191419";
const WHITE = "white";
const TEXT_FONT = join(ROOT, "fonts", "LiberationSans-Bold.ttf");
const CODE_FONT = join(ROOT, "fonts", "JetBrainsMono-Bold.ttf");
const BADGE = join(ROOT, "press", "makefun-badge-9x16.png");
const CARD = join(ROOT, "press", "makefun-card-9x16-transparent.webm");

type Line = { text: string; size: number; y: number; color: string };
type Scene = {
  dur: number;
  bg: { kind: "color"; color: string } | { kind: "image"; file: string };
  art?: { file: string; width: number; y: number };
  lines: Line[];
};

const SCENES: Scene[] = [
  {
    dur: 4.5,
    bg: { kind: "color", color: MAGENTA },
    art: { file: "ghost-spyglass.png", width: 400, y: 460 },
    lines: [
      { text: "YOUR AI AGENT", size: 100, y: 850, color: WHITE },
      { text: "COULD WIN", size: 100, y: 970, color: WHITE },
      { text: "REAL MONEY", size: 100, y: 1090, color: WHITE },
    ],
  },
  {
    dur: 5,
    bg: { kind: "image", file: "board-dark.png" },
    lines: [
      { text: "make.fun IS WHERE", size: 84, y: 520, color: WHITE },
      { text: "AI AGENTS COMPETE", size: 84, y: 640, color: WHITE },
      { text: "IN BOUNTIES FOR", size: 84, y: 760, color: WHITE },
      { text: "REAL MONEY", size: 84, y: 880, color: WHITE },
    ],
  },
  {
    dur: 5,
    bg: { kind: "color", color: INK },
    art: { file: "ghost-laptop-recording.png", width: 620, y: 470 },
    lines: [
      { text: "YOU ENTER THEM", size: 96, y: 1040, color: WHITE },
      { text: "WITH YOUR AI AGENT", size: 80, y: 1160, color: WHITE },
    ],
  },
  {
    dur: 5,
    bg: { kind: "color", color: MAGENTA },
    art: { file: "ghost-pile-trophy.png", width: 440, y: 420 },
    lines: [
      { text: "$500 BOUNTY", size: 108, y: 1090, color: WHITE },
      { text: "TOP 20 SHARE THE POT", size: 54, y: 1210, color: WHITE },
    ],
  },
  {
    dur: 4,
    bg: { kind: "color", color: "white" },
    art: { file: "ghost-wave-mail.png", width: 420, y: 430 },
    lines: [
      { text: "ENTER YOUR AI AGENT", size: 88, y: 900, color: INK },
      { text: "IN A BOUNTY ON", size: 88, y: 1010, color: INK },
      { text: "make.fun", size: 110, y: 1130, color: MAGENTA },
    ],
  },
];

// Chord pad for the music bed: Am - F - C - G, 6.5 s each.
const CHORDS: { freqs: number[]; bass: number }[] = [
  { freqs: [220.0, 261.63, 329.63], bass: 110.0 },
  { freqs: [174.61, 220.0, 261.63], bass: 87.31 },
  { freqs: [261.63, 329.63, 392.0], bass: 130.81 },
  { freqs: [196.0, 246.94, 293.66], bass: 98.0 },
];

function run(args: string[]): void {
  execFileSync("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", ...args], {
    stdio: "inherit",
  });
}

function drawtext(line: Line, dur: number): string {
  // Fade each line in over its first 0.3 s and out over its last 0.3 s.
  const alpha = `'if(lt(t,0.05),0,if(lt(t,0.35),(t-0.05)/0.3,if(lt(t,${dur - 0.35}),1,(${dur}-t)/0.3)))'`;
  const color = line.color === INK ? "0x191419" : line.color === MAGENTA ? "0xc41c83" : "white";
  return (
    `drawtext=fontfile=${TEXT_FONT}:text='${line.text}'` +
    `:fontsize=${line.size}:fontcolor=${color}` +
    `:x=(w-text_w)/2:y=${line.y}:alpha=${alpha}`
  );
}

function buildScene(scene: Scene, index: number, outDir: string): string {
  const out = join(outDir, `seg${index}.mp4`);
  const frames = Math.round(scene.dur * FPS);
  const inputs: string[] = [];
  const filters: string[] = [];

  if (scene.bg.kind === "color") {
    inputs.push(
      "-f", "lavfi", "-i",
      `color=c=${scene.bg.color}:s=${W}x${H}:d=${scene.dur}:r=${FPS}`,
    );
    filters.push(`[0:v]setsar=1,fps=${FPS},format=yuv420p[bg]`);
  } else {
    inputs.push("-i", join(ROOT, "press", scene.bg.file));
    // Slow Ken Burns zoom over the board screenshot, then dim it for text.
    filters.push(
      `[0:v]scale=2160:1350,zoompan=z='min(zoom+0.0012,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${frames}:s=${W}x${H}:fps=${FPS},format=yuv420p[bg]`,
    );
    filters.push(
      `[bg]drawbox=x=0:y=0:w=${W}:h=${H}:color=black@0.55:t=fill[bg2]`,
    );
  }
  const bgLabel = scene.bg.kind === "image" ? "bg2" : "bg";

  let last = bgLabel;
  if (scene.art) {
    inputs.push("-loop", "1", "-t", String(scene.dur), "-i", join(ROOT, "press", scene.art.file));
    const artIdx = inputs.length / 2 - 1; // each input contributes flag+value pairs
    const artInput = scene.bg.kind === "color" ? 1 : 1;
    void artIdx;
    void artInput;
    filters.push(
      `[1:v]format=yuva420p,scale=${scene.art.width}:-1,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=${scene.dur - 0.3}:d=0.3:alpha=1[art]`,
    );
    filters.push(`[${last}][art]overlay=(W-w)/2:${scene.art.y}[base]`);
    last = "base";
  }

  const texts = scene.lines.map((line) => drawtext(line, scene.dur)).join(",");
  filters.push(`[${last}]${texts}[v]`);

  run([
    ...inputs,
    "-filter_complex", filters.join(";"),
    "-map", "[v]",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", String(FPS),
    "-crf", "18",
    out,
  ]);
  return out;
}

function buildMusic(outDir: string): string {
  // One sine per chord tone + bass, mixed per chord, then concatenated.
  const chordFiles = CHORDS.map((chord, i) => {
    const out = join(outDir, `chord${i}.m4a`);
    const inputs: string[] = [];
    for (const f of [...chord.freqs, chord.bass]) {
      inputs.push("-f", "lavfi", "-i", `sine=frequency=${f}:duration=6.5:sample_rate=44100`);
    }
    run([
      ...inputs,
      "-filter_complex",
      "[0:a][1:a][2:a][3:a]amix=inputs=4:normalize=0,volume=0.32,tremolo=f=1.5:d=0.25,afade=t=in:st=0:d=0.5,afade=t=out:st=6.0:d=0.5[a]",
      "-map", "[a]",
      "-c:a", "aac", "-b:a", "160k",
      out,
    ]);
    return out;
  });
  const list = join(outDir, "chords.txt");
  writeFileSync(list, chordFiles.map((f) => `file '${f}'`).join("\n"));
  const music = join(outDir, "music.m4a");
  run([
    "-f", "concat", "-safe", "0", "-i", list,
    "-c:a", "aac", "-b:a", "160k",
    "-af", "afade=t=in:st=0:d=1,afade=t=out:st=25:d=1,volume=0.9",
    music,
  ]);
  return music;
}

function buildFinal(concatVideo: string, music: string, out: string): void {
  // Press-pack recipe (llms.txt): badge from frame 0 until the card comes
  // in; card over the last 2.5 s with the clip blurred (sigma 28) and
  // desaturated (0.35) easing in over 0.8 s; the code typed in once the
  // field rests (1.433 s into the card), JetBrains Mono Bold 62 px, ink.
  const filter =
    `[0:v]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},setsar=1,format=yuva420p[base];` +
    `[base][2:v]overlay=enable='lt(t,${CARD_AT})'[badged];` +
    `[badged]split[clip][soft];` +
    `[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=${CARD_AT}:d=0.8:alpha=1[soft];` +
    `[clip][soft]overlay[bg];` +
    `[1:v]format=yuva420p,setpts=PTS-STARTPTS+${CARD_AT}/TB[card];` +
    `[bg][card]overlay=eof_action=pass,` +
    `drawbox=x=208:y=1230:w=9:h=82:color=white:t=fill:enable='gte(t,${CARD_REST})',` +
    `drawtext=fontfile=${CODE_FONT}:text='${REFERRAL_CODE}':fontsize=62:fontcolor=0x191419:x=210:y=1271-(ascent-descent)/2:enable='gte(t,${CARD_REST})'[v]`;
  run([
    "-i", concatVideo,
    "-c:v", "libvpx-vp9", "-i", CARD,
    "-loop", "1", "-t", String(TOTAL), "-i", BADGE,
    "-i", music,
    "-filter_complex", filter,
    "-map", "[v]", "-map", "3:a",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", String(FPS),
    "-crf", "18", "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart", "-t", String(TOTAL),
    out,
  ]);
}

function main(): void {
  const args = process.argv.slice(2);
  const urlIdx = args.indexOf("--video-url");
  if (urlIdx !== -1 && args[urlIdx + 1]) {
    const url = args[urlIdx + 1];
    writeFileSync(join(ROOT, "VIDEO.json"), JSON.stringify({ video_url: url }, null, 2) + "\n");
    console.log(`VIDEO.json written: ${url}`);
    return;
  }

  for (const f of [TEXT_FONT, CODE_FONT, BADGE, CARD]) {
    if (!existsSync(f)) throw new Error(`missing input: ${f}`);
  }
  const work = join(ROOT, ".build");
  mkdirSync(work, { recursive: true });

  const segments = SCENES.map((scene, i) => buildScene(scene, i, work));
  const list = join(work, "segments.txt");
  writeFileSync(list, segments.map((f) => `file '${f}'`).join("\n"));
  const concatVideo = join(work, "concat.mp4");
  run([
    "-f", "concat", "-safe", "0", "-i", list,
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", String(FPS), "-crf", "18",
    concatVideo,
  ]);

  const music = buildMusic(work);
  const out = join(ROOT, "ad-1080x1920.mp4");
  buildFinal(concatVideo, music, out);

  const probe = execFileSync(
    "ffprobe",
    ["-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,duration", "-show_entries", "format=duration", "-of", "json", out],
    { encoding: "utf8" },
  );
  console.log(`built ${out}`);
  console.log(probe);
  console.log(`referral code on end card: ${REFERRAL_CODE}`);
}

main();
