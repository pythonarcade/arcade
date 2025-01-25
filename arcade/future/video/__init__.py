from .video_player import VideoPlayer

__all__ = ["VideoPlayer"]

# Keep cv2 an optional dependency
try:
    from .video_cv2 import VideoPlayerCV2  # noqa: F401
    from .video_record_cv2 import VideoRecorderCV2  # noqa: F401

    __all__.extend(["VideoPlayerCV2", "VideoRecorderCV2"])


except ImportError:
    pass
