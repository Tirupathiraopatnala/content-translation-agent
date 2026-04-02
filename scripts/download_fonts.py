#!/usr/bin/env python3
"""Download Google Noto Sans fonts for Indian language scripts."""

import os
import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

# Static (non-variable) Noto Sans font URLs — compatible with all Pillow versions.
# Variable fonts ([wdth,wght].ttf) cause rendering issues (boxes/squares) in older Pillow.
FONT_URLS = {
    # Hindi (Devanagari)
    "NotoSansDevanagari-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/static/NotoSansDevanagari-Regular.ttf",
    # Tamil
    "NotoSansTamil-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosanstamil/static/NotoSansTamil-Regular.ttf",
    # Bengali
    "NotoSansBengali-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansbengali/static/NotoSansBengali-Regular.ttf",
    # Punjabi (Gurmukhi)
    "NotoSansGurmukhi-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansgurmukhi/static/NotoSansGurmukhi-Regular.ttf",
    # Gujarati
    "NotoSansGujarati-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansgujarati/static/NotoSansGujarati-Regular.ttf",
}


def download_fonts(force: bool = False):
    """Download all required Noto Sans Indic fonts.

    Args:
        force: If True, re-download even if font file already exists.
    """
    FONTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in FONT_URLS.items():
        dest = FONTS_DIR / filename
        if dest.exists() and not force:
            print(f"  [skip] {filename} already exists")
            continue
        if dest.exists():
            dest.unlink()

        print(f"  [download] {filename} ...")
        try:
            urllib.request.urlretrieve(url, str(dest))
            size_kb = dest.stat().st_size / 1024
            print(f"  [done] {filename} ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"  [error] Failed to download {filename}: {e}")
            if dest.exists():
                dest.unlink()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    if force:
        print("Force re-downloading Noto Sans Indic fonts...")
    else:
        print("Downloading Noto Sans Indic fonts...")
    download_fonts(force=force)
    print("Font download complete.")
