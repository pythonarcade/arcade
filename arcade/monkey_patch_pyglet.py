import pyglet
import arcade
import arcade.sound_wav_monkeypatch as mps

pyglet.media.codecs.wave.get_decoders = mps.get_decoders
pyglet.media.codecs.wave.WaveDecoder = mps.WaveDecoder
pyglet.media.codecs.wave.WaveSource = mps.WaveSource

# --- Mac OS ---
import platform
if platform.system() == 'Darwin':

    from pyglet.window.cocoa import *

    def _create(self):
        # Create a temporary autorelease pool for this method.
        pool = NSAutoreleasePool.alloc().init()

        if self._nswindow:
            # The window is about the be recreated so destroy everything
            # associated with the old window, then destroy the window itself.
            nsview = self.canvas.nsview
            self.canvas = None
            self._nswindow.orderOut_(None)
            self._nswindow.close()
            self.context.detach()
            self._nswindow.release()
            self._nswindow = None
            nsview.release()
            self._delegate.release()
            self._delegate = None

        # Determine window parameters.
        content_rect = NSMakeRect(0, 0, self._width, self._height)
        WindowClass = PygletWindow
        if self._fullscreen:
            style_mask = NSBorderlessWindowMask
        else:
            if self._style not in self._style_masks:
                self._style = self.WINDOW_STYLE_DEFAULT
            style_mask = self._style_masks[self._style]
            if self._resizable:
                style_mask |= NSResizableWindowMask
            if self._style == BaseWindow.WINDOW_STYLE_TOOL:
                WindowClass = PygletToolWindow

        # First create an instance of our NSWindow subclass.

        # FIX ME:
        # Need to use this initializer to have any hope of multi-monitor support.
        # But currently causes problems on Mac OS X Lion.  So for now, we initialize the
        # window without including screen information.
        #
        # self._nswindow = WindowClass.alloc().initWithContentRect_styleMask_backing_defer_screen_(
        #     content_rect,           # contentRect
        #     style_mask,             # styleMask
        #     NSBackingStoreBuffered, # backing
        #     False,                  # defer
        #     self.screen.get_nsscreen())  # screen

        self._nswindow = WindowClass.alloc().initWithContentRect_styleMask_backing_defer_(
            content_rect,  # contentRect
            style_mask,  # styleMask
            NSBackingStoreBuffered,  # backing
            False)  # defer

        if self._fullscreen:
            # BUG: I suspect that this doesn't do the right thing when using
            # multiple monitors (which would be to go fullscreen on the monitor
            # where the window is located).  However I've no way to test.
            blackColor = NSColor.blackColor()
            self._nswindow.setBackgroundColor_(blackColor)
            self._nswindow.setOpaque_(True)
            self.screen.capture_display()
            self._nswindow.setLevel_(quartz.CGShieldingWindowLevel())
            self.context.set_full_screen()
            self._center_window()
            self._mouse_in_window = True
        else:
            self._set_nice_window_location()
            self._mouse_in_window = self._mouse_in_content_rect()

        # Then create a view and set it as our NSWindow's content view.
        self._nsview = PygletView.alloc().initWithFrame_cocoaWindow_(content_rect, self)
        self._nswindow.setContentView_(self._nsview)
        self._nswindow.makeFirstResponder_(self._nsview)

        # Create a canvas with the view as its drawable and attach context to it.
        self.canvas = CocoaCanvas(self.display, self.screen, self._nsview)
        self.context.attach(self.canvas)

        # Configure the window.
        self._nswindow.setAcceptsMouseMovedEvents_(True)
        self._nswindow.setReleasedWhenClosed_(False)
        self._nswindow.useOptimizedDrawing_(True)
        self._nswindow.setPreservesContentDuringLiveResize_(False)

        # Set the delegate.
        self._delegate = PygletDelegate.alloc().initWithWindow_(self)

        # Configure CocoaWindow.
        self.set_caption(self._caption)
        if self._minimum_size is not None:
            self.set_minimum_size(*self._minimum_size)
        if self._maximum_size is not None:
            self.set_maximum_size(*self._maximum_size)

        self.context.update_geometry()
        self.switch_to()
        self.set_vsync(self._vsync)
        self.set_visible(self._visible)

        pool.drain()


    pyglet.window.cocoa.CocoaWindow._create = _create


    def get_size(self):
        window_frame = self._nswindow.frame()
        rect = self._nswindow.contentRectForFrameRect_(window_frame)
        return int(rect.size.width), int(rect.size.height)


    pyglet.window.cocoa.CocoaWindow.get_size = get_size


    def set_minimum_size(self, width, height):
        self._minimum_size = NSSize(width, height)

        if self._nswindow is not None:
            self._nswindow.setContentMinSize_(self._minimum_size)


    pyglet.window.cocoa.CocoaWindow.set_minimum_size = set_minimum_size


    def set_maximum_size(self, width, height):
        self._maximum_size = NSSize(width, height)

        if self._nswindow is not None:
            self._nswindow.setContentMaxSize_(self._maximum_size)


    pyglet.window.cocoa.CocoaWindow.set_maximum_size = set_maximum_size
