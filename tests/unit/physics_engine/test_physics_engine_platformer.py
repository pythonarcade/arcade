import arcade

CHARACTER_SCALING = 0.5
GRAVITY = 0.5


def test_physics_engine(window):
    window.background_color = arcade.color.AMAZON

    character_list = arcade.SpriteList()
    character_sprite = arcade.Sprite(
        ":resources:images/animated_characters/female_person/femalePerson_idle.png",
        scale=CHARACTER_SCALING,
    )
    character_sprite.center_x = 150
    character_sprite.center_y = 110
    character_list.append(character_sprite)

    wall_list = arcade.SpriteList()
    for x in range(0, 1200, 64):
        sprite = arcade.Sprite(
            ":resources:images/tiles/boxCrate_double.png",
            scale=CHARACTER_SCALING,
        )
        sprite.center_x = x
        sprite.center_y = 32
        wall_list.append(sprite)

    platform_list = arcade.SpriteList[arcade.Sprite]()
    platform = arcade.Sprite(
        ":resources:images/tiles/boxCrate_double.png",
        scale=CHARACTER_SCALING,
        center_x=64,
        center_y=256,
    )
    platform.boundary_left = 0  # 0 in particular was problematic, see #2658
    platform.boundary_right = 128
    platform.change_x = 8
    platform_list.append(platform)

    physics_engine = arcade.PhysicsEnginePlatformer(
        character_sprite,
        walls=wall_list,
        platforms=platform_list,
        gravity_constant=GRAVITY,
    )

    def on_draw():
        window.clear()
        wall_list.draw()
        character_list.draw()

    def update(td):
        physics_engine.update()

    window.on_draw = on_draw
    window.on_update = update

    physics_engine.enable_multi_jump(2)
    physics_engine.jumps_since_ground = 0
    assert physics_engine.can_jump() is True
    character_sprite.change_y = 15
    physics_engine.increment_jump_counter()

    window.test(frames=7)

    assert physics_engine.can_jump() is True
    assert platform.center_x == 80  # it bounced against the boundary_right
    assert platform.change_x == -8
    character_sprite.change_y = 15
    physics_engine.increment_jump_counter()

    window.test(frames=6)

    assert physics_engine.can_jump() is False
    assert platform.center_x == 32  # right at the boundary
    assert platform.change_x == -8  # still going left
    physics_engine.disable_multi_jump()

    window.test(frames=3)

    assert platform.center_x == 32 + 24  # it bounced against the boundary_left
    assert platform.change_x == +8
