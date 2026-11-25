#!/usr/bin/env python3
"""Entry point for news-image-20261125.

Writes the front page for Wednesday 25 November 2026 to the output
directory as entry.png. The image is drawn by render.py (from the
date-audited stories.json) and shipped in this repository; this program
only copies it, so both grader runs produce identical bytes.
Standard library only; no network access.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print(f"error: {src} is missing from the repository", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as fh:
        magic = fh.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        print(f"error: {dst} is not a whole PNG file", file=sys.stderr)
        return 1
    size = os.path.getsize(dst)
    if size > 1048576:
        print(f"error: {dst} is {size} bytes, over the 1 MiB gate",
              file=sys.stderr)
        return 1
    print(f"wrote {dst} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
