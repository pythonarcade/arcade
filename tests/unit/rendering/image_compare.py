"""Pixel-diff helper for the reference-image comparison harness (SC-003,
FR-011, T005).

No third-party image-diff dependency is added — this uses PIL, which is
already an Arcade dependency. Comparisons are done with PIL's own C-level
``ImageChops``/``ImageStat`` operations rather than a per-pixel Python loop,
since a naive loop over an 800x600 image is slow enough to matter in a test
suite.
"""

from __future__ import annotations

from dataclasses import dataclass

import PIL.Image
import PIL.ImageChops
import PIL.ImageStat

#: SC-003 tolerance: no more than this fraction of pixels may differ from the
#: baseline by more than MAX_PER_CHANNEL_DELTA (out of 255).
MAX_DIFFERING_PIXEL_FRACTION = 0.02
MAX_PER_CHANNEL_DELTA = 10

#: SC-003 tolerance: whole-image mean absolute per-channel difference, as a
#: fraction of the full 0-255 range.
MAX_MEAN_ABS_DIFFERENCE_FRACTION = 0.01


@dataclass
class ImageDiffResult:
    differing_pixel_fraction: float
    mean_abs_difference_fraction: float

    @property
    def within_tolerance(self) -> bool:
        return (
            self.differing_pixel_fraction <= MAX_DIFFERING_PIXEL_FRACTION
            and self.mean_abs_difference_fraction <= MAX_MEAN_ABS_DIFFERENCE_FRACTION
        )

    def __str__(self) -> str:
        return (
            f"{self.differing_pixel_fraction:.2%} of pixels differ by more than "
            f"{MAX_PER_CHANNEL_DELTA}/255 per channel "
            f"(tolerance: {MAX_DIFFERING_PIXEL_FRACTION:.2%}); "
            f"mean abs difference: {self.mean_abs_difference_fraction:.2%} "
            f"(tolerance: {MAX_MEAN_ABS_DIFFERENCE_FRACTION:.2%})"
        )


def compare_images(actual: PIL.Image.Image, expected: PIL.Image.Image) -> ImageDiffResult:
    """Compare two images against the SC-003 tolerance.

    Args:
        actual: The newly rendered image.
        expected: The checked-in baseline image.

    Returns:
        An :class:`ImageDiffResult` describing how different the images are.
        Check ``.within_tolerance`` to see if they pass SC-003.
    """
    if actual.size != expected.size:
        raise ValueError(f"Image size mismatch: {actual.size} != {expected.size}")

    actual_rgb = actual.convert("RGB")
    expected_rgb = expected.convert("RGB")

    diff = PIL.ImageChops.difference(actual_rgb, expected_rgb)

    mean_abs_difference_fraction = sum(PIL.ImageStat.Stat(diff).mean) / (3 * 255)

    per_channel_masks = [
        channel.point(lambda v: 255 if v > MAX_PER_CHANNEL_DELTA else 0)
        for channel in diff.split()
    ]
    combined_mask = per_channel_masks[0]
    for mask in per_channel_masks[1:]:
        combined_mask = PIL.ImageChops.lighter(combined_mask, mask)

    histogram = combined_mask.histogram()
    differing_pixels = sum(histogram[1:])  # index 0 == "no difference"
    total_pixels = combined_mask.size[0] * combined_mask.size[1]
    differing_pixel_fraction = differing_pixels / total_pixels

    return ImageDiffResult(
        differing_pixel_fraction=differing_pixel_fraction,
        mean_abs_difference_fraction=mean_abs_difference_fraction,
    )
