"""
THIS IS WORK IN PROGRESS. DO NOT USE.
"""

from typing import TYPE_CHECKING

from .base import TextureAtlasBase

if TYPE_CHECKING:
    from arcade import ArcadeContext


class BindlessTextureAtlas(TextureAtlasBase):
    """
    A texture atlas using bindless textures. This is an extension to OpenGL 4.3+
    and requires the ARB_bindless_texture extension or possibly vendor specific ones.

    Bindless textures are simply 64 bit integer names/handles for a texture that
    can be casted to a sampler in a shader meaning that you can have an unlimited
    amount of samplers in the same draw call. Likely a shader storage buffer is
    needed to store the handles.

    The max capacity is only limited by memory. Discrete GPUs support this
    feature and some iGPUs from 2019 and later. AMD + Intel Xe if
    latest drivers are installed.
    """

    def __init__(self, ctx: ArcadeContext):
        super().__init__(ctx)
