"""Shared utility functions used across all notebooks."""

import json
import os
from pathlib import Path
from typing import Any

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Project paths ──────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PAGE_IMAGES_DIR = DATA_DIR / "page_images"
OCR_RESULTS_DIR = DATA_DIR / "ocr_results"
TRANSLATIONS_DIR = DATA_DIR / "translations"
INPAINTED_DIR = DATA_DIR / "inpainted"
OUTPUT_DIR = DATA_DIR / "output"
FONTS_DIR = PROJECT_ROOT / "fonts"
SAMPLES_DIR = PROJECT_ROOT / "samples"


# ── JSON I/O ───────────────────────────────────────────────────────────────────

def save_json(data: Any, path: str | Path) -> None:
    """Save data as JSON with pretty formatting."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: str | Path) -> Any:
    """Load JSON data from file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Image I/O ──────────────────────────────────────────────────────────────────

def save_image(image: Image.Image, path: str | Path) -> None:
    """Save a PIL Image to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(path))


def load_image(path: str | Path) -> Image.Image:
    """Load an image as PIL Image."""
    return Image.open(str(path)).convert("RGB")


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR format."""
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR image to PIL Image."""
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


# ── Visualization ──────────────────────────────────────────────────────────────

def draw_bboxes(
    image: Image.Image,
    text_blocks: list[dict],
    color: str = "red",
    width: int = 2,
    show_text: bool = False,
) -> Image.Image:
    """Draw bounding boxes on a copy of the image.

    Args:
        image: Input PIL Image.
        text_blocks: List of dicts with 'bbox' key [x0, y0, x1, y1].
        color: Bounding box color.
        width: Line width.
        show_text: If True, draw the text above each box.

    Returns:
        New image with bounding boxes drawn.
    """
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for block in text_blocks:
        bbox = block["bbox"]
        draw.rectangle(bbox, outline=color, width=width)
        if show_text and "text" in block:
            text = block["text"][:40]  # Truncate for display
            draw.text((bbox[0], bbox[1] - 14), text, fill=color, font=font)

    return img_copy


def display_images(
    images: list[Image.Image],
    titles: list[str] | None = None,
    figsize: tuple[int, int] | None = None,
    cols: int = 2,
) -> None:
    """Display multiple images side-by-side in a matplotlib figure."""
    n = len(images)
    if figsize is None:
        figsize = (8 * min(n, cols), 8 * ((n + cols - 1) // cols))
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    if rows * cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    for i, img in enumerate(images):
        axes[i].imshow(np.array(img))
        if titles and i < len(titles):
            axes[i].set_title(titles[i], fontsize=14)
        axes[i].axis("off")

    # Hide empty subplots
    for i in range(n, len(axes)):
        axes[i].axis("off")

    plt.tight_layout()
    plt.show()


def display_comparison(
    original: Image.Image,
    modified: Image.Image,
    title_left: str = "Original",
    title_right: str = "Modified",
    figsize: tuple[int, int] = (16, 8),
) -> None:
    """Display original and modified images side-by-side."""
    display_images([original, modified], [title_left, title_right], figsize=figsize)


# ── Text block helpers ─────────────────────────────────────────────────────────

def normalize_bbox(bbox: list | tuple) -> list[int]:
    """Ensure bbox is [x0, y0, x1, y1] with x0<x1 and y0<y1."""
    x0, y0, x1, y1 = bbox
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def sample_background_color(
    image: Image.Image, bbox: list[int], margin: int = 5
) -> tuple[int, int, int]:
    """Sample the most common color around a bounding box to estimate background."""
    x0, y0, x1, y1 = bbox
    w, h = image.size

    # Sample a thin strip around the bbox
    regions = []
    # Top strip
    if y0 - margin > 0:
        regions.append(image.crop((max(0, x0), max(0, y0 - margin), min(w, x1), y0)))
    # Bottom strip
    if y1 + margin < h:
        regions.append(image.crop((max(0, x0), y1, min(w, x1), min(h, y1 + margin))))

    if not regions:
        return (255, 255, 255)  # Default white

    # Combine sampled pixels
    pixels = []
    for region in regions:
        arr = np.array(region).reshape(-1, 3)
        pixels.append(arr)
    all_pixels = np.concatenate(pixels, axis=0)

    # Return the median color (robust to outliers)
    median_color = np.median(all_pixels, axis=0).astype(int)
    return tuple(median_color.tolist())


def estimate_text_color(
    image: Image.Image, bbox: list[int], bg_color: tuple[int, int, int]
) -> tuple[int, int, int]:
    """Estimate text color within a bounding box by finding the most different color from background."""
    x0, y0, x1, y1 = bbox
    region = np.array(image.crop((x0, y0, x1, y1))).reshape(-1, 3)

    if len(region) == 0:
        return (0, 0, 0)

    # Calculate distance from background for each pixel
    bg = np.array(bg_color)
    distances = np.linalg.norm(region.astype(float) - bg.astype(float), axis=1)

    # Pixels far from background are likely text
    threshold = np.percentile(distances, 70)
    text_pixels = region[distances > threshold]

    if len(text_pixels) == 0:
        return (0, 0, 0)

    median_color = np.median(text_pixels, axis=0).astype(int)
    return tuple(median_color.tolist())
