"""
Experimental stuff. API may change.
"""
from .video_player import VideoPlayer, VideoPlayerView
from .texture_render_target import RenderTargetTexture
from .shadertoy import Shadertoy, ShadertoyBuffer, ShadertoyBase
from .crt_filter import CRTFilter
from .bloom_filter import BloomFilter

def raiseModuleNotFoundError():
    raise ModuleNotFoundError("cv2 is not installed. Run 'pip install opencv-python'")

# Keep cv2 an optional dependency
try:
    from .video_cv2 import VideoPlayerCV2, CV2PlayerView
except ImportError:
    VideoPlayerCV2 = CV2PlayerView = raiseModuleNotFoundError

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
