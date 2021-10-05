"""
Simple demo showing runtime image replacement in texture atlas directly.
The right solution would normally be to replace the sprite with a new
one, but in instances were images are created manually by code and changing
over time at (not too frequently) we can update the underlying atlas directly.
"""
from itertools import cycle
import arcade

TEXTURE_PATHS = [
    ":resources:images/cards/cardClubs2.png",
    ":resources:images/cards/cardClubs3.png",
    ":resources:images/cards/cardClubs4.png",
    ":resources:images/cards/cardClubs5.png",
    ":resources:images/cards/cardClubs6.png",
    ":resources:images/cards/cardClubs7.png",
    ":resources:images/cards/cardClubs8.png",
    ":resources:images/cards/cardClubs9.png",
    ":resources:images/cards/cardClubsA.png",
    ":resources:images/cards/cardClubsJ.png",
    ":resources:images/cards/cardClubsK.png",
    ":resources:images/cards/cardClubsQ.png",
    ":resources:images/cards/cardDiamonds10.png",
    ":resources:images/cards/cardDiamonds2.png",
    ":resources:images/cards/cardDiamonds3.png",
    ":resources:images/cards/cardDiamonds4.png",
    ":resources:images/cards/cardDiamonds5.png",
    ":resources:images/cards/cardDiamonds6.png",
    ":resources:images/cards/cardDiamonds7.png",
    ":resources:images/cards/cardDiamonds8.png",
    ":resources:images/cards/cardDiamonds9.png",
    ":resources:images/cards/cardDiamondsA.png",
    ":resources:images/cards/cardDiamondsJ.png",
    ":resources:images/cards/cardDiamondsK.png",
    ":resources:images/cards/cardDiamondsQ.png",
    ":resources:images/cards/cardHearts10.png",
    ":resources:images/cards/cardHearts2.png",
    ":resources:images/cards/cardHearts3.png",
    ":resources:images/cards/cardHearts4.png",
    ":resources:images/cards/cardHearts5.png",
    ":resources:images/cards/cardHearts6.png",
    ":resources:images/cards/cardHearts7.png",
    ":resources:images/cards/cardHearts8.png",
    ":resources:images/cards/cardHearts9.png",
    ":resources:images/cards/cardHeartsA.png",
    ":resources:images/cards/cardHeartsJ.png",
    ":resources:images/cards/cardHeartsK.png",
    ":resources:images/cards/cardHeartsQ.png",
    ":resources:images/cards/cardJoker.png",
    ":resources:images/cards/cardSpades10.png",
    ":resources:images/cards/cardSpades2.png",
    ":resources:images/cards/cardSpades3.png",
    ":resources:images/cards/cardSpades4.png",
    ":resources:images/cards/cardSpades5.png",
    ":resources:images/cards/cardSpades6.png",
    ":resources:images/cards/cardSpades7.png",
    ":resources:images/cards/cardSpades8.png",
    ":resources:images/cards/cardSpades9.png",
    ":resources:images/cards/cardSpadesA.png",
    ":resources:images/cards/cardSpadesJ.png",
    ":resources:images/cards/cardSpadesK.png",
    ":resources:images/cards/cardSpadesQ.png",
]


class AtlasReplaceImage(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Replacing images in atlas")
        self.sprite_1 = arcade.Sprite(TEXTURE_PATHS[-1], center_x=200, center_y=300)
        self.sprite_2 = arcade.Sprite(TEXTURE_PATHS[-2], center_x=400, center_y=300)
        self.sprite_3 = arcade.Sprite(TEXTURE_PATHS[-3], center_x=600, center_y=300)
        self.spritelist = arcade.SpriteList()
        self.spritelist.extend([self.sprite_1, self.sprite_2, self.sprite_3])
        # Timer for texture change
        self.elapsed_time = 0
        self.texture_cycle = cycle(arcade.load_texture(p) for p in TEXTURE_PATHS)

    def on_draw(self):
        self.spritelist.draw()

    def on_update(self, delta_time: float):
        self.elapsed_time += delta_time
        # Change textures 
        if self.elapsed_time > 1.0:
            # Replace the internal images. They all have the same size (required)
            self.sprite_1.texture.image = next(self.texture_cycle).image
            self.sprite_2.texture.image = next(self.texture_cycle).image
            self.sprite_3.texture.image = next(self.texture_cycle).image
            # Update the internal texture image in the atlas
            self.spritelist.atlas.update_texture_image(self.sprite_1.texture)
            self.spritelist.atlas.update_texture_image(self.sprite_2.texture)
            self.spritelist.atlas.update_texture_image(self.sprite_3.texture)
            # Reset timer
            self.elapsed_time = 0


window = AtlasReplaceImage()
arcade.run()
