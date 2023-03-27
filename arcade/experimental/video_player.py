"""
Experimental video player using pyglet.

This requires that you have ffmpeg installed
and you might need to tell pyglet where it's located.
"""
# import sys
import pyglet
import arcade


class VideoPlayer(arcade.View):
    """
    Can be used to add effects like rain to the background of the game.
    Make sure to inherit this view and call super for `__init__` and `on_draw`.
    """

    def __init__(self, path: str) -> None:
        super().__init__()

        self.player = pyglet.media.Player()
        # Used this because it will throw SIGSEGV when passed a Path like object, which is not very descriptive.
        if not issubclass(type(path), str):
            raise TypeError(f"The path is required to be a str object and not a {type(path)} object")
        self.player.queue(pyglet.media.load(path))
        self.player.play()

    def on_draw(self):
        self.clear()
        # video_width, video_height = self.get_video_size()
        # print((video_width, video_height), self.player.source.duration, self.player.time)

        with self.ctx.pyglet_rendering():
            self.ctx.disable(self.ctx.BLEND)
            video_texture = self.player.texture
            if video_texture:
                video_texture.blit(
                    0,
                    0,
                    width=self.width,
                    height=self.height,
                )

    def get_video_size(self):
        if not self.player.source or not self.player.source.video_format:
            return 0, 0
        video_format = self.player.source.video_format
        width = video_format.width
        height = video_format.height
        if video_format.sample_aspect > 1:
            width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            height /= video_format.sample_aspect
        return width, height
