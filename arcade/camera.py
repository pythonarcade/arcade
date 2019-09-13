import arcade


class Camera:
    def __init__(self, entity, screen_size, viewport_margin=None):
        self.entity = entity
        self.width = screen_size[0]
        self.height = screen_size[1]
        if viewport_margin:
            self.viewport_margin = viewport_margin
        else:
            self.viewport_margin = 100
        self.view_left = 0
        self.view_bottom = 0

    def update(self):
        changed = False

        # Scroll left
        left_bndry = self.view_left + self.viewport_margin
        if self.entity.left < left_bndry:
            self.view_left -= left_bndry - self.entity.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + self.width - self.viewport_margin
        if self.entity.right > right_bndry:
            self.view_left += self.entity.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + self.height - self.viewport_margin
        if self.entity.top > top_bndry:
            self.view_bottom += self.entity.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + self.viewport_margin
        if self.entity.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.entity.bottom
            changed = True

        if changed:
            arcade.set_viewport(self.view_left,
                                self.width + self.view_left,
                                self.view_bottom,
                                self.height + self.view_bottom)
                                
