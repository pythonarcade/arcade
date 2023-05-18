"""
Experimental stuff. API may change.
"""
from .video_player import VideoPlayer, VideoPlayerView
from .texture_render_target import RenderTargetTexture
from .shadertoy import Shadertoy, ShadertoyBuffer, ShadertoyBase
from .crt_filter import CRTFilter
from .bloom_filter import BloomFilter

# Keep cv2 an optional dependency
try:
    from .video_cv2 import VideoPlayerCV2, CV2PlayerView
except ImportError:
    pass

__all__ = [
    "VideoPlayer",
    "VideoPlayerView",
    "VideoPlayerCV2",
    "CV2PlayerView",
    "RenderTargetTexture",
    "Shadertoy",
    "ShadertoyBuffer",
    "ShadertoyBase",
    "CRTFilter",
    "BloomFilter",
]
