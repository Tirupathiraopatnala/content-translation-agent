#!/usr/bin/env python3
"""Download Google Noto Sans fonts for Indian language scripts."""

import os
import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

# Google Fonts direct download URLs for Noto Sans Indic fonts
FONT_URLS = {
    # Hindi (Devanagari)
    "NotoSansDevanagari-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    # Tamil
    "NotoSansTamil-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosanstamil/NotoSansTamil%5Bwdth%2Cwght%5D.ttf",
    # Bengali
    "NotoSansBengali-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansbengali/NotoSansBengali%5Bwdth%2Cwght%5D.ttf",
    # Punjabi (Gurmukhi)
    "NotoSansGurmukhi-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansgurmukhi/NotoSansGurmukhi%5Bwdth%2Cwght%5D.ttf",
    # Gujarati
    "NotoSansGujarati-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansgujarati/NotoSansGujarati%5Bwdth%2Cwght%5D.ttf",
}


def download_fonts():
    """Download all required Noto Sans Indic fonts."""
    FONTS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in FONT_URLS.items():
        dest = FONTS_DIR / filename
        if dest.exists():
            print(f"  [skip] {filename} already exists")
            continue

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
    print("Downloading Noto Sans Indic fonts...")
    download_fonts()
    print("Font download complete.")
