"""
Experimental video player using pyglet.

This requires that you have ffmpeg installed
and you might need to tell pyglet where it's located.
"""
# import sys
import pyglet
import arcade


class VideoPlayer(arcade.Window):

    def __init__(self) -> None:
        super().__init__(800, 600, "Video Player", resizable=True)

        self.player = pyglet.media.Player()
        # self.player.queue(pyglet.media.load("C:/Users/efors/Desktop/file_example_MP4_480_1_5MG.mp4"))
        self.player.queue(pyglet.media.load("C:/Users/efors/Desktop/BigBuckBunny.mp4"))
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

    def on_update(self, delta_time: float):
        pass

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


window = VideoPlayer()
arcade.run()
