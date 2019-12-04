from PIL import Image

class SpriteSheet:
    def __init__(self):
        self._image = None
        self._texture_atlas = None

    def load(self, image_file, mapping_file):
        self._image = Image.open(image_file)

