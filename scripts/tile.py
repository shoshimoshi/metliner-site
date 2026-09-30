#!/usr/bin/env python3
"""
Metliner map tiler.
Turn a big transit-map image into a DZI (Deep Zoom) tile pyramid for OpenSeadragon.

Usage:
  python3 tile.py SOURCE_IMAGE OUTPUT_DIR NAME
      -> writes OUTPUT_DIR/NAME.dzi and OUTPUT_DIR/NAME_files/<level>/<col>_<row>.jpg

  python3 tile.py --thumb SOURCE_IMAGE OUTPUT_THUMB.jpg [WIDTH]
      -> writes a small cover thumbnail (default width 640)
"""
import sys, os, math, shutil
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

TILE = 512
OVERLAP = 1
FMT = 'jpg'
QUALITY = 82

def make_thumb(src, out, width=640):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    hh = max(1, round(h * width / w))
    im.resize((width, hh), Image.LANCZOS).save(out, quality=86)
    print(f"thumb {out} -> {width}x{hh}")

def tile(src, outdir, name):
    im = Image.open(src).convert('RGB')
    W, H = im.size
    files_dir = os.path.join(outdir, f"{name}_files")
    if os.path.exists(files_dir):
        shutil.rmtree(files_dir)
    os.makedirs(files_dir, exist_ok=True)
    max_level = math.ceil(math.log2(max(W, H)))
    total = 0
    for level in range(max_level, -1, -1):
        scale = 2 ** (max_level - level)
        lw = max(1, math.ceil(W / scale))
        lh = max(1, math.ceil(H / scale))
        lim = im if scale == 1 else im.resize((lw, lh), Image.LANCZOS)
        ldir = os.path.join(files_dir, str(level))
        os.makedirs(ldir, exist_ok=True)
        cols = math.ceil(lw / TILE)
        rows = math.ceil(lh / TILE)
        for r in range(rows):
            for c in range(cols):
                x, y = c * TILE, r * TILE
                left  = max(0, x - OVERLAP)
                upper = max(0, y - OVERLAP)
                right = min(lw, x + TILE + OVERLAP)
                lower = min(lh, y + TILE + OVERLAP)
                lim.crop((left, upper, right, lower)).save(
                    os.path.join(ldir, f"{c}_{r}.{FMT}"), quality=QUALITY)
                total += 1
    dzi = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<Image xmlns="http://schemas.microsoft.com/deepzoom/2008" '
           f'Format="{FMT}" Overlap="{OVERLAP}" TileSize="{TILE}">\n'
           f'  <Size Width="{W}" Height="{H}"/>\n</Image>')
    with open(os.path.join(outdir, f"{name}.dzi"), 'w') as f:
        f.write(dzi)
    print(f"{name}: {W}x{H} -> {total} tiles ({max_level+1} levels)")
    return total

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--thumb':
        src, out = args[1], args[2]
        width = int(args[3]) if len(args) > 3 else 640
        make_thumb(src, out, width)
    else:
        src, outdir, name = args[0], args[1], args[2]
        os.makedirs(outdir, exist_ok=True)
        tile(src, outdir, name)
