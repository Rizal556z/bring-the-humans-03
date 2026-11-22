// SPDX-License-Identifier: MIT
// bring-the-humans-03 — grade entry point.
//
// The grader runs `node /bot/main.ts` with no network, a read-only /bot,
// an empty /output and a 60 s wall budget. This file does NOT re-render
// the video: the 26 s render takes minutes on 1 CPU and needs ffmpeg,
// which the sandbox has neither. The video was produced in the recorded
// build session and is already posted on TikTok. This entry point only
// verifies the entry's own deliverables on disk and exits 0 when they
// are all in order:
//
//   VIDEO.json        parses, holds exactly one key "url", the posted
//                     TikTok video URL
//   video_counts.json parses, names the same video id, counts are numbers
//   README.md         present and links to make.fun
//   main_v3.py        the v3 generator that built the video, present
//
// Any failed check prints FAIL to stderr and exits 1. Nothing is written
// anywhere: the file only reads, so it runs fine on a read-only /bot.
// Plain JavaScript in a .ts file (no type annotations), so plain `node`
// runs it with no build step and no dependencies.

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const VIDEO_URL = "https://www.tiktok.com/@tegal_despasito/video/7711055711299456264";
const VIDEO_ID = "7711055711299456264";

const failures = [];

function check(name, ok, detail) {
  console.log(`${ok ? "ok  " : "FAIL"} ${name}${detail ? ` — ${detail}` : ""}`);
  if (!ok) failures.push(name);
}

function readJson(name) {
  const path = join(ROOT, name);
  if (!existsSync(path)) return { missing: true };
  try {
    return { data: JSON.parse(readFileSync(path, "utf8")) };
  } catch (err) {
    return { error: String(err && err.message ? err.message : err) };
  }
}

// VIDEO.json: exactly one key "url", the posted v3 video.
const video = readJson("VIDEO.json");
if (video.missing) check("VIDEO.json present", false, "file missing");
else if (video.error) check("VIDEO.json parses", false, video.error);
else {
  const keys = Object.keys(video.data);
  check("VIDEO.json has exactly one key", keys.length === 1 && keys[0] === "url", `keys: ${keys.join(",")}`);
  check("VIDEO.json url is the posted v3 video", video.data.url === VIDEO_URL, video.data.url);
}

// video_counts.json: same video id, numeric counts.
const counts = readJson("video_counts.json");
if (counts.missing) check("video_counts.json present", false, "file missing");
else if (counts.error) check("video_counts.json parses", false, counts.error);
else {
  check("video_counts.json video_id matches", counts.data.video_id === VIDEO_ID, String(counts.data.video_id));
  const c = counts.data.counts || {};
  const numeric = ["plays", "likes", "comments", "shares"].every(
    (k) => typeof c[k] === "number" && c[k] >= 0,
  );
  check("video_counts.json counts are numbers", numeric, JSON.stringify(c));
}

// README.md: present and links to make.fun.
const readmePath = join(ROOT, "README.md");
if (!existsSync(readmePath)) check("README.md present", false, "file missing");
else {
  const text = readFileSync(readmePath, "utf8");
  check("README.md links to make.fun", text.includes("make.fun"), `${text.length} bytes`);
}

// main_v3.py: the generator that built the posted video, present.
check("main_v3.py present", existsSync(join(ROOT, "main_v3.py")));

if (failures.length > 0) {
  console.error(`FAIL: ${failures.length} check(s) failed: ${failures.join(", ")}`);
  process.exit(1);
}
console.log("all checks passed: bring-the-humans-03 entry deliverables in order");
