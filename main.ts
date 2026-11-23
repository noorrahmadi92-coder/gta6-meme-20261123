// gta6-meme-x-01 entry (Node 22, standard library only): it copies POST.json
// and meme.png from the repository root to /output, where the gate reads
// POST.json. The meme itself is drawn deterministically by generate_meme.py
// (Pillow, no network; fonts and press-kit art are committed in this repo),
// and this program hands the finished picture to the grader alongside the
// post's address. Nothing this program writes about the post is judged: the
// house reads the post itself from X.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
for (const file of ['POST.json', 'meme.png']) {
  try {
    copyFileSync(join(BOT_DIR, file), join(OUTPUT_DIR, file));
  } catch (err) {
    console.error(`${file} could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
    process.exit(1);
  }
}
console.log(`wrote POST.json and meme.png to ${OUTPUT_DIR}`);
