from PIL import Image

from src.utils import (
    build_text_edit_mask,
    compute_non_text_change_ratio,
    preserve_non_text_regions,
)


def test_build_text_edit_mask_respects_padding_and_bounds() -> None:
    mask = build_text_edit_mask(
        image_size=(10, 10),
        text_blocks=[{"bbox": [2, 2, 4, 4]}, {"bbox": [-3, -1, 1, 1]}],
        padding=1,
    )

    assert mask.shape == (10, 10)
    assert mask[0, 0] == 255  # clipped bbox is still included
    assert mask[1, 1] == 255
    assert mask[4, 4] == 255
    assert mask[9, 9] == 0


def test_preserve_non_text_regions_locks_pixels_outside_text() -> None:
    original = Image.new("RGB", (8, 8), (255, 255, 255))
    translated = Image.new("RGB", (8, 8), (0, 0, 255))

    result = preserve_non_text_regions(
        original=original,
        translated=translated,
        text_blocks=[{"bbox": [2, 2, 6, 6]}],
    )

    result_pixels = result.load()

    # Outside text block should match original (white)
    assert result_pixels[0, 0] == (255, 255, 255)
    # Inside text block should keep translated content (blue)
    assert result_pixels[3, 3] == (0, 0, 255)


def test_compute_non_text_change_ratio_detects_leakage() -> None:
    original = Image.new("RGB", (6, 6), (255, 255, 255))
    candidate = original.copy()
    pix = candidate.load()

    # one change inside editable text region
    pix[2, 2] = (0, 0, 0)
    # one change outside text region
    pix[0, 0] = (0, 0, 0)

    ratio = compute_non_text_change_ratio(
        original=original,
        candidate=candidate,
        text_blocks=[{"bbox": [2, 2, 4, 4]}],
    )

    # 1 changed pixel out of 32 non-text pixels
    assert abs(ratio - (1 / 32)) < 1e-9
