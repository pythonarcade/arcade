"""
Experimental stuff. API may change.
"""
from __future__ import annotations

from .video_player import VideoPlayer, VideoPlayerView
from .texture_render_target import RenderTargetTexture
from .shadertoy import Shadertoy, ShadertoyBuffer, ShadertoyBase
from .crt_filter import CRTFilter
from .bloom_filter import BloomFilter

__all__ = [
    "VideoPlayer",
    "VideoPlayerView",
    "RenderTargetTexture",
    "Shadertoy",
    "ShadertoyBuffer",
    "ShadertoyBase",
    "CRTFilter",
    "BloomFilter",
]

# Keep cv2 an optional dependency
try:
    from .video_cv2 import CV2PlayerView, VideoPlayerCV2  # noqa: F401

    __all__.extend([
        "VideoPlayerCV2",
        "CV2PlayerView",
    ])

except ImportError:
        pass
