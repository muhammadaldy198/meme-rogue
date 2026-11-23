// meme-rogue (make.fun): one image meme about an AI agent gone rogue.
// The picture itself is the entry — draw.py renders it deterministically
// from the spec in that file, and this program only carries the finished
// PNG from the repository to /output/entry.png, unchanged. It checks the
// file first (PNG signature + the 1 MiB gate) so a broken render fails
// here instead of shipping a bad image to the judge.
import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;
const SRC_NAME = "entry.png";
const OUT_DIR = "/output";
const OUT_PATH = join(OUT_DIR, SRC_NAME);

function fail(message: string): never {
  throw new Error("meme-rogue: " + message);
}

function readEntry(): Buffer {
  const here = dirname(fileURLToPath(import.meta.url));
  const src = join(here, SRC_NAME);
  if (!existsSync(src)) fail("entry.png missing from repository");
  const bytes = readFileSync(src);
  if (bytes.length < PNG_MAGIC.length) fail("entry.png too short to be a PNG");
  if (!bytes.subarray(0, PNG_MAGIC.length).equals(PNG_MAGIC)) {
    fail("entry.png is not a PNG");
  }
  if (bytes.length > MAX_BYTES) {
    fail(`entry.png ${bytes.length} bytes exceeds the 1 MiB gate`);
  }
  return bytes;
}

function writeOutput(bytes: Buffer): void {
  if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(OUT_PATH, bytes);
  chmodSync(OUT_PATH, 0o644);
  const written = statSync(OUT_PATH).size;
  if (written !== bytes.length) fail("short write to /output/entry.png");
}

const bytes = readEntry();
writeOutput(bytes);
console.log(`wrote ${OUT_PATH} (${bytes.length} bytes)`);
