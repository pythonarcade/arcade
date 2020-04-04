import ctypes
from collections import deque
from typing import List, Tuple
import pyglet.gl as gl
from arcade.shader import Texture


class Framebuffer:
    """
    An offscreen render target also called a Framebuffer Object in OpenGL.
    This implementation is using texture attachments. When createing a
    Framebuffer we supply it with textures we want our scene rendered into.
    """
    active = None  # The framebuffer that is bound currently

    def __init__(self, color_attachments=None, depth_attachment=None):
        """Create a framebuffer.

        :param List[Texture] color_attachments: List of color attachments.
        :param Texture depth_attachment: A depth attachment (optional)
        """
        self._color_attachments = color_attachments
        self._depth_attachment = depth_attachment
        self._glo = gl.GLuint()  # The OpenGL alias/name
        self._samples = 0  # Leaving this at 0 for future sample support
        self._viewport = None
        self._depth_mask = True  # Determines of the depth buffer should be affected
        self._width = 0
        self._height = 0

        # Create the framebuffer object
        gl.glGenFramebuffers(1, self._glo)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

        # Ensure all attachments have the same size.
        # OpenGL do actually support different sizes,
        # but let's keep this simple with high compatibility.
        expected_size = (self._color_attachments[0] if self._color_attachments else self._depth_attachment).size
        for layer in [*self._color_attachments, self._depth_attachment]:
            if layer and layer.size != expected_size:
                raise ValueError("All framebuffer attachments should have the same size")

        self._width, self._height = expected_size
        self._viewport = 0, 0, self._width, self._height

        # Attach textures to it
        for i, tex in enumerate(self._color_attachments):
            # TODO: Possibly support attaching a specific mipmap level
            #       but we can read from specific mip levels from shaders.
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER,
                gl.GL_COLOR_ATTACHMENT0 + i,
                gl.GL_TEXTURE_2D,
                tex.glo,
                0,  # Level 0
            )

        # Ensure the framebuffer is sane!
        self._check_completness()

        # Set up draw buffers. This is simply a prepared list of attachments enums
        # we use in the use() method to activate the different color attachment layers
        layers = [gl.GL_COLOR_ATTACHMENT0 + i for i, _ in enumerate(self._color_attachments)]
        # pyglet wants this as a ctypes thingy, so let's prepare it
        self._draw_buffers = (ctypes.c_ulong * len(layers))(*layers)

        # Fall back to window
        Framebuffer.active.use()

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL id/name of the framebuffer"""
        return self._glo

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """The framebuffer's viewport.

        Two or four integer values can be assigned::

            # Explicitly set start and end values
            fb.viewport = 100, 100, 200, 200
            # Implies 0, 0, 100, 100
            fb.viewport = 100, 100
        """
        return self._viewport

    @viewport.setter
    def viewport(self, value):
        if not isinstance(value, tuple):
            raise ValueError("viewport should be a tuple with length 2 or 4")

        if len(value) == 2:
            self._viewport = 0, 0, *value
        elif len(value) == 4:
            self._viewport = value
        else:
            raise ValueError("viewport should be a tuple with length 2 or 4")

        # If the framebuffer is bound we need to set the viewport.
        # Otherwise it will be set on use()
        if Framebuffer.active == self:
             gl.glViewport(*self._viewport)

    @property
    def width(self) -> int:
        """The width of the framebuffer in pixels"""
        return self._width

    @property
    def height(self) -> int:
        """The height of the framebuffer in pixels"""
        return self._height

    @property
    def size(self) -> Tuple[int, int]:
        return self._width, self._height

    @property
    def samples(self) -> int:
        """Number of samples (MSAA)"""
        return self._samples

    @property
    def color_attachments(self) -> List[Texture]:
        """A list of color attachments"""
        return self._color_attachments

    @property
    def depth_attachment(self) -> Texture:
        """Depth attachment"""
        return self._depth_attachment

    @property
    def depth_mask(self) -> bool:
        """The depth mask. It determines of depth values should be written
        to the depth texture when depth testing is enabled.
        """
        return self._depth_mask

    @depth_mask.setter
    def depth_mask(self, value):
        self._depth_mask = value
        # Set state if framebuffer is active
        if Framebuffer.active == self:
            gl.glDepthMask(self._depth_mask)

    def use(self):
        """Bind the framebuffer making it the target of all redering commands"""
        # Don't bind the same framebuffer multiple times
        self._use()
        Framebuffer.active = self

    def _use(self):
        """Internal use that do not change the global active framebuffer"""
        if Framebuffer.active == self:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)
        # Note: gl.glDrawBuffer(GL_NONE) if no texture attachments (future)
        gl.glDrawBuffers(len(self._draw_buffers), self._draw_buffers)
        gl.glDepthMask(self._depth_mask)
        gl.glViewport(*self._viewport)

    def clear(self, color=(0.0, 0.0, 0.0, 0.0), depth=1.0):
        """Clears the framebuffer. This will also activate/use it"""
        self._use()
        gl.glClearColor(*color)
        if self.depth_attachment:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Ensure we don't change framebuffer unless it's already activated
        Framebuffer.active.use()

    def release(self, release_attachments=False):
        """Destroys the framebuffer object
        
        :param bool release_attachments: Also release the attachments
        """
        if gl.current_context is None:
            return

        gl.glDeleteFramebuffers(1, self._glo)
        if release_attachments:
            for tex in self._color_attachments:
                tex.release()
            if self._depth_attachment:
                self._depth_attachment.release()

    # NOTE: This is an experiment using a bind stack (can be explored later)
    # def __enter__(self):
    #     """Enter method for context manager"""
    #     self._stack.push(self)
    #     self.use()

    # def __exit__(self):
    #     """Exit method for context manager"""
    #     self._stack.pop()
    #     # TODO: Bind previous. if this is the window, how do we know the viewport etc?

    def __repr__(self):
        return "<Framebuffer glo={}>".format(self._glo)

    def _check_completness(self):
        """
        Checks the completness of the framebuffer.
        If the framebuffer is not complete, we cannot continue.
        """
        # See completness rules : https://www.khronos.org/opengl/wiki/Framebuffer_Object
        states = {gl.GL_FRAMEBUFFER_UNSUPPORTED: "Framebuffer unsupported. Try another format.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: "Framebuffer incomplete attachment.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: "Framebuffer missing attachment.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT: "Framebuffer unsupported dimension.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT: "Framebuffer incomplete formats.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER: "Framebuffer incomplete draw buffer.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER: "Framebuffer incomplete read buffer.",
                  gl.GL_FRAMEBUFFER_COMPLETE: "Framebuffer is complete."}

        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            raise ValueError("Framebuffer is incomplete. {}".format(states.get(status, "Unknown error")))
