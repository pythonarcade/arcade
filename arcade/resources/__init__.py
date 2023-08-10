from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union
from arcade.utils import warning, ReplacementWarning

#: The absolute path to this directory
RESOURCE_DIR = Path(__file__).parent.resolve()
SYSTEM_PATH = RESOURCE_DIR / "system"
ASSET_PATH = RESOURCE_DIR / "assets"

handles: Dict[str, List[Path]] = {
    "resources": [SYSTEM_PATH, ASSET_PATH],
    "assets": [ASSET_PATH],
    "system": [SYSTEM_PATH],
}

__all__ = [
    "resolve_resource_path",
    "resolve",
    "add_resource_handle",
    "get_resource_handle_paths",
]


@warning(
    warning_type=ReplacementWarning,
    new_name="resolve"
)
def resolve_resource_path(path: Union[str, Path]) -> Path:
    """
    Attempts to resolve a path to a resource including resource handles.

    If the path is a string it tries to resolve it as a resource handle
    or convert it to a Path object.

    If the path is a Path object it will ``Path.resolve()`` it
    unless it's not absolute and return it.

    Example::

        resolve(":resources:images/cards/cardBack_blue1.png")
        resolve(":my_handle:music/combat.wav")

    :param Union[str, Path] path: A Path or string
    """
    return resolve(path)


def resolve(path: Union[str, Path]) -> Path:
    """
    Attempts to resolve a path to a resource including resource handles.

    If the path is a string it tries to resolve it as a resource handle
    or convert it to a Path object.

    If the path is a Path object it will ``Path.resolve()`` it
    unless it's not absolute and return it.

    Example::

        resolve(":resources:images/cards/cardBack_blue1.png")
        resolve(":my_handle:music/combat.wav")

    :param Union[str, Path] path: A Path or string
    """
    # Convert to a Path object and resolve resource handle
    if isinstance(path, str):
        path = path.strip()  # Allow for silly mistakes with extra spaces

        # If the path starts with a colon, it's a resource handle
        if path.startswith(':'):
            path = path[1:]
            handle, resource = path.split(":")
            while resource.startswith('/') or resource.startswith('\\'):
                resource = resource[1:]

            # Iterate through the paths in reverse order to find the first
            # match. This allows for overriding of resources.
            paths = get_resource_handle_paths(handle)
            for handle_path in reversed(paths):
                path = handle_path / resource
                if path.exists():
                    break
            else:
                searched_paths = '\n'.join(f"-> {p}" for p in reversed(paths))
                raise FileNotFoundError((
                    f"Cannot locate resource '{resource}' using handle "
                    f"'{handle}' in any of the following paths:\n"
                    f"{searched_paths}"
                ))

            # Always convert into a Path object
            path = Path(handle_path / resource)
        else:
            path = Path(path)

    # Always return absolute paths
    # Check for the existence of the file and provide useful feedback to
    # avoid deep stack trace into pathlib
    try:
        # If the path is absolute, just return it. We assume it's valid and resolved.
        if path.is_absolute():
            return path
        return path.resolve(strict=True)
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot locate resource : {path}")


def add_resource_handle(handle: str, path: Union[str, Path]) -> None:
    """
    Add a resource handle or path to an existing handle.

    A handle can point to multiple paths. If a resource is not found in
    the first path, it will look in the next path, and so on. The search
    is done in reverse order, so the last path added is searched first.

    :param str handle: The name of the handle
    :param Union[str, Path] path: The absolute path to a directory
    """
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, Path):
        path = path
    else:
        raise TypeError("Path for resource handle must be a string or Path object")

    if not path.is_absolute():
        raise RuntimeError(
            f"Path for resource handle must be absolute, not relative ('{path}'). "
            "See https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve"
        )

    if not path.exists():
        raise FileNotFoundError(f"Directory '{path}' for handle '{handle}' does not exist")

    paths = handles.setdefault(handle, [])
    # Don't allow duplicate paths
    if path not in paths:
        paths.append(path)


def get_resource_handle_paths(handle: str) -> List[Path]:
    """
    Returns the paths for a resource handle.

    :param str handle: The name of the handle
    """
    try:
        return handles[handle]
    except KeyError:
        raise KeyError(f"Unknown resource handle \"{handle}\"")


# Metadata for the resource list: utils\create_resource_list.py
_resource_list_skip_extensions = [
    '.glsl',
    '.md',
    '.py',
    '.yml',
    '.url',
    '.txt',
    '.tiled-project',
    '.ttf',
    '.pyc',
]
_resource_list_ignore_paths = {
    RESOURCE_DIR / "assets" / "cache",
    RESOURCE_DIR / "assets" / "onscreen_controls"
}

# RESOURCE LIST : (Truncate file from here if auto generating resource list)
image_alien_blue_climb1 = ':assets:images/alien/alienBlue_climb1.png'
image_alien_blue_climb2 = ':assets:images/alien/alienBlue_climb2.png'
image_alien_blue_front = ':assets:images/alien/alienBlue_front.png'
image_alien_blue_jump = ':assets:images/alien/alienBlue_jump.png'
image_alien_blue_walk1 = ':assets:images/alien/alienBlue_walk1.png'
image_alien_blue_walk2 = ':assets:images/alien/alienBlue_walk2.png'
image_female_adventurer_climb0 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_climb0.png'
image_female_adventurer_climb1 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_climb1.png'
image_female_adventurer_fall = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_fall.png'
image_female_adventurer_idle = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_idle.png'
image_female_adventurer_jump = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_jump.png'
image_female_adventurer_walk0 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk0.png'
image_female_adventurer_walk1 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk1.png'
image_female_adventurer_walk2 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk2.png'
image_female_adventurer_walk3 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk3.png'
image_female_adventurer_walk4 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk4.png'
image_female_adventurer_walk5 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk5.png'
image_female_adventurer_walk6 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk6.png'
image_female_adventurer_walk7 = ':assets:images/animated_characters/female_adventurer/femaleAdventurer_walk7.png'
image_female_person_climb0 = ':assets:images/animated_characters/female_person/femalePerson_climb0.png'
image_female_person_climb1 = ':assets:images/animated_characters/female_person/femalePerson_climb1.png'
image_female_person_fall = ':assets:images/animated_characters/female_person/femalePerson_fall.png'
image_female_person_idle = ':assets:images/animated_characters/female_person/femalePerson_idle.png'
image_female_person_jump = ':assets:images/animated_characters/female_person/femalePerson_jump.png'
image_female_person_walk0 = ':assets:images/animated_characters/female_person/femalePerson_walk0.png'
image_female_person_walk1 = ':assets:images/animated_characters/female_person/femalePerson_walk1.png'
image_female_person_walk2 = ':assets:images/animated_characters/female_person/femalePerson_walk2.png'
image_female_person_walk3 = ':assets:images/animated_characters/female_person/femalePerson_walk3.png'
image_female_person_walk4 = ':assets:images/animated_characters/female_person/femalePerson_walk4.png'
image_female_person_walk5 = ':assets:images/animated_characters/female_person/femalePerson_walk5.png'
image_female_person_walk6 = ':assets:images/animated_characters/female_person/femalePerson_walk6.png'
image_female_person_walk7 = ':assets:images/animated_characters/female_person/femalePerson_walk7.png'
image_male_adventurer_climb0 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_climb0.png'
image_male_adventurer_climb1 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_climb1.png'
image_male_adventurer_fall = ':assets:images/animated_characters/male_adventurer/maleAdventurer_fall.png'
image_male_adventurer_idle = ':assets:images/animated_characters/male_adventurer/maleAdventurer_idle.png'
image_male_adventurer_jump = ':assets:images/animated_characters/male_adventurer/maleAdventurer_jump.png'
image_male_adventurer_walk0 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk0.png'
image_male_adventurer_walk1 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk1.png'
image_male_adventurer_walk2 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk2.png'
image_male_adventurer_walk3 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk3.png'
image_male_adventurer_walk4 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk4.png'
image_male_adventurer_walk5 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk5.png'
image_male_adventurer_walk6 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk6.png'
image_male_adventurer_walk7 = ':assets:images/animated_characters/male_adventurer/maleAdventurer_walk7.png'
image_male_person_climb0 = ':assets:images/animated_characters/male_person/malePerson_climb0.png'
image_male_person_climb1 = ':assets:images/animated_characters/male_person/malePerson_climb1.png'
image_male_person_fall = ':assets:images/animated_characters/male_person/malePerson_fall.png'
image_male_person_idle = ':assets:images/animated_characters/male_person/malePerson_idle.png'
image_male_person_jump = ':assets:images/animated_characters/male_person/malePerson_jump.png'
image_male_person_walk0 = ':assets:images/animated_characters/male_person/malePerson_walk0.png'
image_male_person_walk1 = ':assets:images/animated_characters/male_person/malePerson_walk1.png'
image_male_person_walk2 = ':assets:images/animated_characters/male_person/malePerson_walk2.png'
image_male_person_walk3 = ':assets:images/animated_characters/male_person/malePerson_walk3.png'
image_male_person_walk4 = ':assets:images/animated_characters/male_person/malePerson_walk4.png'
image_male_person_walk5 = ':assets:images/animated_characters/male_person/malePerson_walk5.png'
image_male_person_walk6 = ':assets:images/animated_characters/male_person/malePerson_walk6.png'
image_male_person_walk7 = ':assets:images/animated_characters/male_person/malePerson_walk7.png'
image_robot_climb0 = ':assets:images/animated_characters/robot/robot_climb0.png'
image_robot_climb1 = ':assets:images/animated_characters/robot/robot_climb1.png'
image_robot_fall = ':assets:images/animated_characters/robot/robot_fall.png'
image_robot_idle = ':assets:images/animated_characters/robot/robot_idle.png'
image_robot_jump = ':assets:images/animated_characters/robot/robot_jump.png'
image_robot_walk0 = ':assets:images/animated_characters/robot/robot_walk0.png'
image_robot_walk1 = ':assets:images/animated_characters/robot/robot_walk1.png'
image_robot_walk2 = ':assets:images/animated_characters/robot/robot_walk2.png'
image_robot_walk3 = ':assets:images/animated_characters/robot/robot_walk3.png'
image_robot_walk4 = ':assets:images/animated_characters/robot/robot_walk4.png'
image_robot_walk5 = ':assets:images/animated_characters/robot/robot_walk5.png'
image_robot_walk6 = ':assets:images/animated_characters/robot/robot_walk6.png'
image_robot_walk7 = ':assets:images/animated_characters/robot/robot_walk7.png'
image_zombie_climb0 = ':assets:images/animated_characters/zombie/zombie_climb0.png'
image_zombie_climb1 = ':assets:images/animated_characters/zombie/zombie_climb1.png'
image_zombie_fall = ':assets:images/animated_characters/zombie/zombie_fall.png'
image_zombie_idle = ':assets:images/animated_characters/zombie/zombie_idle.png'
image_zombie_jump = ':assets:images/animated_characters/zombie/zombie_jump.png'
image_zombie_walk0 = ':assets:images/animated_characters/zombie/zombie_walk0.png'
image_zombie_walk1 = ':assets:images/animated_characters/zombie/zombie_walk1.png'
image_zombie_walk2 = ':assets:images/animated_characters/zombie/zombie_walk2.png'
image_zombie_walk3 = ':assets:images/animated_characters/zombie/zombie_walk3.png'
image_zombie_walk4 = ':assets:images/animated_characters/zombie/zombie_walk4.png'
image_zombie_walk5 = ':assets:images/animated_characters/zombie/zombie_walk5.png'
image_zombie_walk6 = ':assets:images/animated_characters/zombie/zombie_walk6.png'
image_zombie_walk7 = ':assets:images/animated_characters/zombie/zombie_walk7.png'
image_abstract_1 = ':assets:images/backgrounds/abstract_1.jpg'
image_abstract_2 = ':assets:images/backgrounds/abstract_2.jpg'
image_instructions_0 = ':assets:images/backgrounds/instructions_0.png'
image_instructions_1 = ':assets:images/backgrounds/instructions_1.png'
image_stars = ':assets:images/backgrounds/stars.png'
image_card_back_blue1 = ':assets:images/cards/cardBack_blue1.png'
image_card_back_blue2 = ':assets:images/cards/cardBack_blue2.png'
image_card_back_blue3 = ':assets:images/cards/cardBack_blue3.png'
image_card_back_blue4 = ':assets:images/cards/cardBack_blue4.png'
image_card_back_blue5 = ':assets:images/cards/cardBack_blue5.png'
image_card_back_green1 = ':assets:images/cards/cardBack_green1.png'
image_card_back_green2 = ':assets:images/cards/cardBack_green2.png'
image_card_back_green3 = ':assets:images/cards/cardBack_green3.png'
image_card_back_green4 = ':assets:images/cards/cardBack_green4.png'
image_card_back_green5 = ':assets:images/cards/cardBack_green5.png'
image_card_back_red1 = ':assets:images/cards/cardBack_red1.png'
image_card_back_red2 = ':assets:images/cards/cardBack_red2.png'
image_card_back_red3 = ':assets:images/cards/cardBack_red3.png'
image_card_back_red4 = ':assets:images/cards/cardBack_red4.png'
image_card_back_red5 = ':assets:images/cards/cardBack_red5.png'
image_card_clubs10 = ':assets:images/cards/cardClubs10.png'
image_card_clubs2 = ':assets:images/cards/cardClubs2.png'
image_card_clubs3 = ':assets:images/cards/cardClubs3.png'
image_card_clubs4 = ':assets:images/cards/cardClubs4.png'
image_card_clubs5 = ':assets:images/cards/cardClubs5.png'
image_card_clubs6 = ':assets:images/cards/cardClubs6.png'
image_card_clubs7 = ':assets:images/cards/cardClubs7.png'
image_card_clubs8 = ':assets:images/cards/cardClubs8.png'
image_card_clubs9 = ':assets:images/cards/cardClubs9.png'
image_card_clubs_a = ':assets:images/cards/cardClubsA.png'
image_card_clubs_j = ':assets:images/cards/cardClubsJ.png'
image_card_clubs_k = ':assets:images/cards/cardClubsK.png'
image_card_clubs_q = ':assets:images/cards/cardClubsQ.png'
image_card_diamonds10 = ':assets:images/cards/cardDiamonds10.png'
image_card_diamonds2 = ':assets:images/cards/cardDiamonds2.png'
image_card_diamonds3 = ':assets:images/cards/cardDiamonds3.png'
image_card_diamonds4 = ':assets:images/cards/cardDiamonds4.png'
image_card_diamonds5 = ':assets:images/cards/cardDiamonds5.png'
image_card_diamonds6 = ':assets:images/cards/cardDiamonds6.png'
image_card_diamonds7 = ':assets:images/cards/cardDiamonds7.png'
image_card_diamonds8 = ':assets:images/cards/cardDiamonds8.png'
image_card_diamonds9 = ':assets:images/cards/cardDiamonds9.png'
image_card_diamonds_a = ':assets:images/cards/cardDiamondsA.png'
image_card_diamonds_j = ':assets:images/cards/cardDiamondsJ.png'
image_card_diamonds_k = ':assets:images/cards/cardDiamondsK.png'
image_card_diamonds_q = ':assets:images/cards/cardDiamondsQ.png'
image_card_hearts10 = ':assets:images/cards/cardHearts10.png'
image_card_hearts2 = ':assets:images/cards/cardHearts2.png'
image_card_hearts3 = ':assets:images/cards/cardHearts3.png'
image_card_hearts4 = ':assets:images/cards/cardHearts4.png'
image_card_hearts5 = ':assets:images/cards/cardHearts5.png'
image_card_hearts6 = ':assets:images/cards/cardHearts6.png'
image_card_hearts7 = ':assets:images/cards/cardHearts7.png'
image_card_hearts8 = ':assets:images/cards/cardHearts8.png'
image_card_hearts9 = ':assets:images/cards/cardHearts9.png'
image_card_hearts_a = ':assets:images/cards/cardHeartsA.png'
image_card_hearts_j = ':assets:images/cards/cardHeartsJ.png'
image_card_hearts_k = ':assets:images/cards/cardHeartsK.png'
image_card_hearts_q = ':assets:images/cards/cardHeartsQ.png'
image_card_joker = ':assets:images/cards/cardJoker.png'
image_card_spades10 = ':assets:images/cards/cardSpades10.png'
image_card_spades2 = ':assets:images/cards/cardSpades2.png'
image_card_spades3 = ':assets:images/cards/cardSpades3.png'
image_card_spades4 = ':assets:images/cards/cardSpades4.png'
image_card_spades5 = ':assets:images/cards/cardSpades5.png'
image_card_spades6 = ':assets:images/cards/cardSpades6.png'
image_card_spades7 = ':assets:images/cards/cardSpades7.png'
image_card_spades8 = ':assets:images/cards/cardSpades8.png'
image_card_spades9 = ':assets:images/cards/cardSpades9.png'
image_card_spades_a = ':assets:images/cards/cardSpadesA.png'
image_card_spades_j = ':assets:images/cards/cardSpadesJ.png'
image_card_spades_k = ':assets:images/cards/cardSpadesK.png'
image_card_spades_q = ':assets:images/cards/cardSpadesQ.png'
image_back_buildings = ':assets:images/cybercity_background/back-buildings.png'
image_far_buildings = ':assets:images/cybercity_background/far-buildings.png'
image_foreground = ':assets:images/cybercity_background/foreground.png'
image_bee = ':assets:images/enemies/bee.png'
image_fish_green = ':assets:images/enemies/fishGreen.png'
image_fish_pink = ':assets:images/enemies/fishPink.png'
image_fly = ':assets:images/enemies/fly.png'
image_frog = ':assets:images/enemies/frog.png'
image_frog_move = ':assets:images/enemies/frog_move.png'
image_ladybug = ':assets:images/enemies/ladybug.png'
image_mouse = ':assets:images/enemies/mouse.png'
image_saw = ':assets:images/enemies/saw.png'
image_saw_half = ':assets:images/enemies/sawHalf.png'
image_slime_block = ':assets:images/enemies/slimeBlock.png'
image_slime_blue = ':assets:images/enemies/slimeBlue.png'
image_slime_blue_move = ':assets:images/enemies/slimeBlue_move.png'
image_slime_green = ':assets:images/enemies/slimeGreen.png'
image_slime_purple = ':assets:images/enemies/slimePurple.png'
image_worm_green = ':assets:images/enemies/wormGreen.png'
image_worm_green_dead = ':assets:images/enemies/wormGreen_dead.png'
image_worm_green_move = ':assets:images/enemies/wormGreen_move.png'
image_worm_pink = ':assets:images/enemies/wormPink.png'
image_coin_bronze = ':assets:images/items/coinBronze.png'
image_coin_gold = ':assets:images/items/coinGold.png'
image_coin_gold_ll = ':assets:images/items/coinGold_ll.png'
image_coin_gold_lr = ':assets:images/items/coinGold_lr.png'
image_coin_gold_ul = ':assets:images/items/coinGold_ul.png'
image_coin_gold_ur = ':assets:images/items/coinGold_ur.png'
image_coin_silver = ':assets:images/items/coinSilver.png'
image_coin_silver_test = ':assets:images/items/coinSilver_test.png'
image_flag_green1 = ':assets:images/items/flagGreen1.png'
image_flag_green2 = ':assets:images/items/flagGreen2.png'
image_flag_green_down = ':assets:images/items/flagGreen_down.png'
image_flag_red1 = ':assets:images/items/flagRed1.png'
image_flag_red2 = ':assets:images/items/flagRed2.png'
image_flag_red_down = ':assets:images/items/flagRed_down.png'
image_flag_yellow1 = ':assets:images/items/flagYellow1.png'
image_flag_yellow2 = ':assets:images/items/flagYellow2.png'
image_flag_yellow_down = ':assets:images/items/flagYellow_down.png'
image_gem_blue = ':assets:images/items/gemBlue.png'
image_gem_green = ':assets:images/items/gemGreen.png'
image_gem_red = ':assets:images/items/gemRed.png'
image_gem_yellow = ':assets:images/items/gemYellow.png'
image_gold_1 = ':assets:images/items/gold_1.png'
image_gold_2 = ':assets:images/items/gold_2.png'
image_gold_3 = ':assets:images/items/gold_3.png'
image_gold_4 = ':assets:images/items/gold_4.png'
image_key_blue = ':assets:images/items/keyBlue.png'
image_key_green = ':assets:images/items/keyGreen.png'
image_key_red = ':assets:images/items/keyRed.png'
image_key_yellow = ':assets:images/items/keyYellow.png'
image_ladder_mid = ':assets:images/items/ladderMid.png'
image_ladder_top = ':assets:images/items/ladderTop.png'
image_star = ':assets:images/items/star.png'
image_car_idle = ':assets:images/miami_synth_parallax/car/car-idle.png'
image_car_running0 = ':assets:images/miami_synth_parallax/car/car-running0.png'
image_car_running1 = ':assets:images/miami_synth_parallax/car/car-running1.png'
image_car_running2 = ':assets:images/miami_synth_parallax/car/car-running2.png'
image_car_running3 = ':assets:images/miami_synth_parallax/car/car-running3.png'
image_back = ':assets:images/miami_synth_parallax/layers/back.png'
image_buildings = ':assets:images/miami_synth_parallax/layers/buildings.png'
image_highway = ':assets:images/miami_synth_parallax/layers/highway.png'
image_palms = ':assets:images/miami_synth_parallax/layers/palms.png'
image_sun = ':assets:images/miami_synth_parallax/layers/sun.png'
image_bumper = ':assets:images/pinball/bumper.png'
image_pool_cue_ball = ':assets:images/pinball/pool_cue_ball.png'
image_laser_blue01 = ':assets:images/space_shooter/laserBlue01.png'
image_laser_red01 = ':assets:images/space_shooter/laserRed01.png'
image_meteor_grey_big1 = ':assets:images/space_shooter/meteorGrey_big1.png'
image_meteor_grey_big2 = ':assets:images/space_shooter/meteorGrey_big2.png'
image_meteor_grey_big3 = ':assets:images/space_shooter/meteorGrey_big3.png'
image_meteor_grey_big4 = ':assets:images/space_shooter/meteorGrey_big4.png'
image_meteor_grey_med1 = ':assets:images/space_shooter/meteorGrey_med1.png'
image_meteor_grey_med2 = ':assets:images/space_shooter/meteorGrey_med2.png'
image_meteor_grey_small1 = ':assets:images/space_shooter/meteorGrey_small1.png'
image_meteor_grey_small2 = ':assets:images/space_shooter/meteorGrey_small2.png'
image_meteor_grey_tiny1 = ':assets:images/space_shooter/meteorGrey_tiny1.png'
image_meteor_grey_tiny2 = ':assets:images/space_shooter/meteorGrey_tiny2.png'
image_player_life1_blue = ':assets:images/space_shooter/playerLife1_blue.png'
image_player_life1_green = ':assets:images/space_shooter/playerLife1_green.png'
image_player_life1_orange = ':assets:images/space_shooter/playerLife1_orange.png'
image_player_ship1_blue = ':assets:images/space_shooter/playerShip1_blue.png'
image_player_ship1_green = ':assets:images/space_shooter/playerShip1_green.png'
image_player_ship1_orange = ':assets:images/space_shooter/playerShip1_orange.png'
image_player_ship2_orange = ':assets:images/space_shooter/playerShip2_orange.png'
image_player_ship3_orange = ':assets:images/space_shooter/playerShip3_orange.png'
image_codepage_437 = ':assets:images/spritesheets/codepage_437.png'
image_explosion = ':assets:images/spritesheets/explosion.png'
image_number_sheet = ':assets:images/spritesheets/number_sheet.png'
image_tiles = ':assets:images/spritesheets/tiles.png'
image_anim = ':assets:images/test_textures/anim.gif'
image_diffuse = ':assets:images/test_textures/normal_mapping/diffuse.jpg'
image_normal = ':assets:images/test_textures/normal_mapping/normal.jpg'
image_test_texture = ':assets:images/test_textures/test_texture.png'
image_xy_square = ':assets:images/test_textures/xy_square.png'
image_bomb = ':assets:images/tiles/bomb.png'
image_box_crate = ':assets:images/tiles/boxCrate.png'
image_box_crate_double = ':assets:images/tiles/boxCrate_double.png'
image_box_crate_single = ':assets:images/tiles/boxCrate_single.png'
image_brick_brown = ':assets:images/tiles/brickBrown.png'
image_brick_grey = ':assets:images/tiles/brickGrey.png'
image_brick_texture_white = ':assets:images/tiles/brickTextureWhite.png'
image_bridge_a = ':assets:images/tiles/bridgeA.png'
image_bridge_b = ':assets:images/tiles/bridgeB.png'
image_bush = ':assets:images/tiles/bush.png'
image_cactus = ':assets:images/tiles/cactus.png'
image_dirt = ':assets:images/tiles/dirt.png'
image_dirt_center = ':assets:images/tiles/dirtCenter.png'
image_dirt_center_rounded = ':assets:images/tiles/dirtCenter_rounded.png'
image_dirt_cliff_alt_left = ':assets:images/tiles/dirtCliffAlt_left.png'
image_dirt_cliff_alt_right = ':assets:images/tiles/dirtCliffAlt_right.png'
image_dirt_cliff_left = ':assets:images/tiles/dirtCliff_left.png'
image_dirt_cliff_right = ':assets:images/tiles/dirtCliff_right.png'
image_dirt_corner_left = ':assets:images/tiles/dirtCorner_left.png'
image_dirt_corner_right = ':assets:images/tiles/dirtCorner_right.png'
image_dirt_half = ':assets:images/tiles/dirtHalf.png'
image_dirt_half_left = ':assets:images/tiles/dirtHalf_left.png'
image_dirt_half_mid = ':assets:images/tiles/dirtHalf_mid.png'
image_dirt_half_right = ':assets:images/tiles/dirtHalf_right.png'
image_dirt_hill_left = ':assets:images/tiles/dirtHill_left.png'
image_dirt_hill_right = ':assets:images/tiles/dirtHill_right.png'
image_dirt_left = ':assets:images/tiles/dirtLeft.png'
image_dirt_mid = ':assets:images/tiles/dirtMid.png'
image_dirt_right = ':assets:images/tiles/dirtRight.png'
image_door_closed_mid = ':assets:images/tiles/doorClosed_mid.png'
image_door_closed_top = ':assets:images/tiles/doorClosed_top.png'
image_grass = ':assets:images/tiles/grass.png'
image_grass_center = ':assets:images/tiles/grassCenter.png'
image_grass_center_round = ':assets:images/tiles/grassCenter_round.png'
image_grass_cliff_alt_left = ':assets:images/tiles/grassCliffAlt_left.png'
image_grass_cliff_alt_right = ':assets:images/tiles/grassCliffAlt_right.png'
image_grass_cliff_left = ':assets:images/tiles/grassCliff_left.png'
image_grass_cliff_right = ':assets:images/tiles/grassCliff_right.png'
image_grass_corner_left = ':assets:images/tiles/grassCorner_left.png'
image_grass_corner_right = ':assets:images/tiles/grassCorner_right.png'
image_grass_half = ':assets:images/tiles/grassHalf.png'
image_grass_half_left = ':assets:images/tiles/grassHalf_left.png'
image_grass_half_mid = ':assets:images/tiles/grassHalf_mid.png'
image_grass_half_right = ':assets:images/tiles/grassHalf_right.png'
image_grass_hill_left = ':assets:images/tiles/grassHill_left.png'
image_grass_hill_right = ':assets:images/tiles/grassHill_right.png'
image_grass_left = ':assets:images/tiles/grassLeft.png'
image_grass_mid = ':assets:images/tiles/grassMid.png'
image_grass_right = ':assets:images/tiles/grassRight.png'
image_grass_sprout = ':assets:images/tiles/grass_sprout.png'
image_ladder_mid = ':assets:images/tiles/ladderMid.png'
image_ladder_top = ':assets:images/tiles/ladderTop.png'
image_lava = ':assets:images/tiles/lava.png'
image_lava_top_high = ':assets:images/tiles/lavaTop_high.png'
image_lava_top_low = ':assets:images/tiles/lavaTop_low.png'
image_lever_left = ':assets:images/tiles/leverLeft.png'
image_lever_mid = ':assets:images/tiles/leverMid.png'
image_lever_right = ':assets:images/tiles/leverRight.png'
image_lock_red = ':assets:images/tiles/lockRed.png'
image_lock_yellow = ':assets:images/tiles/lockYellow.png'
image_mushroom_red = ':assets:images/tiles/mushroomRed.png'
image_planet = ':assets:images/tiles/planet.png'
image_planet_center = ':assets:images/tiles/planetCenter.png'
image_planet_center_rounded = ':assets:images/tiles/planetCenter_rounded.png'
image_planet_cliff_alt_left = ':assets:images/tiles/planetCliffAlt_left.png'
image_planet_cliff_alt_right = ':assets:images/tiles/planetCliffAlt_right.png'
image_planet_cliff_left = ':assets:images/tiles/planetCliff_left.png'
image_planet_cliff_right = ':assets:images/tiles/planetCliff_right.png'
image_planet_corner_left = ':assets:images/tiles/planetCorner_left.png'
image_planet_corner_right = ':assets:images/tiles/planetCorner_right.png'
image_planet_half = ':assets:images/tiles/planetHalf.png'
image_planet_half_left = ':assets:images/tiles/planetHalf_left.png'
image_planet_half_mid = ':assets:images/tiles/planetHalf_mid.png'
image_planet_half_right = ':assets:images/tiles/planetHalf_right.png'
image_planet_hill_left = ':assets:images/tiles/planetHill_left.png'
image_planet_hill_right = ':assets:images/tiles/planetHill_right.png'
image_planet_left = ':assets:images/tiles/planetLeft.png'
image_planet_mid = ':assets:images/tiles/planetMid.png'
image_planet_right = ':assets:images/tiles/planetRight.png'
image_plant_purple = ':assets:images/tiles/plantPurple.png'
image_rock = ':assets:images/tiles/rock.png'
image_sand = ':assets:images/tiles/sand.png'
image_sand_center = ':assets:images/tiles/sandCenter.png'
image_sand_center_rounded = ':assets:images/tiles/sandCenter_rounded.png'
image_sand_cliff_alt_left = ':assets:images/tiles/sandCliffAlt_left.png'
image_sand_cliff_alt_right = ':assets:images/tiles/sandCliffAlt_right.png'
image_sand_cliff_left = ':assets:images/tiles/sandCliff_left.png'
image_sand_cliff_right = ':assets:images/tiles/sandCliff_right.png'
image_sand_corner_left = ':assets:images/tiles/sandCorner_left.png'
image_sand_corner_right = ':assets:images/tiles/sandCorner_right.png'
image_sand_half = ':assets:images/tiles/sandHalf.png'
image_sand_half_left = ':assets:images/tiles/sandHalf_left.png'
image_sand_half_mid = ':assets:images/tiles/sandHalf_mid.png'
image_sand_half_right = ':assets:images/tiles/sandHalf_right.png'
image_sand_hill_left = ':assets:images/tiles/sandHill_left.png'
image_sand_hill_right = ':assets:images/tiles/sandHill_right.png'
image_sand_left = ':assets:images/tiles/sandLeft.png'
image_sand_mid = ':assets:images/tiles/sandMid.png'
image_sand_right = ':assets:images/tiles/sandRight.png'
image_sign_exit = ':assets:images/tiles/signExit.png'
image_sign_left = ':assets:images/tiles/signLeft.png'
image_sign_right = ':assets:images/tiles/signRight.png'
image_snow = ':assets:images/tiles/snow.png'
image_snow_center = ':assets:images/tiles/snowCenter.png'
image_snow_center_rounded = ':assets:images/tiles/snowCenter_rounded.png'
image_snow_cliff_alt_left = ':assets:images/tiles/snowCliffAlt_left.png'
image_snow_cliff_alt_right = ':assets:images/tiles/snowCliffAlt_right.png'
image_snow_cliff_left = ':assets:images/tiles/snowCliff_left.png'
image_snow_cliff_right = ':assets:images/tiles/snowCliff_right.png'
image_snow_corner_left = ':assets:images/tiles/snowCorner_left.png'
image_snow_corner_right = ':assets:images/tiles/snowCorner_right.png'
image_snow_half = ':assets:images/tiles/snowHalf.png'
image_snow_half_left = ':assets:images/tiles/snowHalf_left.png'
image_snow_half_mid = ':assets:images/tiles/snowHalf_mid.png'
image_snow_half_right = ':assets:images/tiles/snowHalf_right.png'
image_snow_hill_left = ':assets:images/tiles/snowHill_left.png'
image_snow_hill_right = ':assets:images/tiles/snowHill_right.png'
image_snow_left = ':assets:images/tiles/snowLeft.png'
image_snow_mid = ':assets:images/tiles/snowMid.png'
image_snow_right = ':assets:images/tiles/snowRight.png'
image_snow_pile = ':assets:images/tiles/snow_pile.png'
image_spikes = ':assets:images/tiles/spikes.png'
image_stone = ':assets:images/tiles/stone.png'
image_stone_center = ':assets:images/tiles/stoneCenter.png'
image_stone_center_rounded = ':assets:images/tiles/stoneCenter_rounded.png'
image_stone_cliff_alt_left = ':assets:images/tiles/stoneCliffAlt_left.png'
image_stone_cliff_alt_right = ':assets:images/tiles/stoneCliffAlt_right.png'
image_stone_cliff_left = ':assets:images/tiles/stoneCliff_left.png'
image_stone_cliff_right = ':assets:images/tiles/stoneCliff_right.png'
image_stone_corner_left = ':assets:images/tiles/stoneCorner_left.png'
image_stone_corner_right = ':assets:images/tiles/stoneCorner_right.png'
image_stone_half = ':assets:images/tiles/stoneHalf.png'
image_stone_half_left = ':assets:images/tiles/stoneHalf_left.png'
image_stone_half_mid = ':assets:images/tiles/stoneHalf_mid.png'
image_stone_half_right = ':assets:images/tiles/stoneHalf_right.png'
image_stone_hill_left = ':assets:images/tiles/stoneHill_left.png'
image_stone_hill_right = ':assets:images/tiles/stoneHill_right.png'
image_stone_left = ':assets:images/tiles/stoneLeft.png'
image_stone_mid = ':assets:images/tiles/stoneMid.png'
image_stone_right = ':assets:images/tiles/stoneRight.png'
image_switch_green = ':assets:images/tiles/switchGreen.png'
image_switch_green_pressed = ':assets:images/tiles/switchGreen_pressed.png'
image_switch_red = ':assets:images/tiles/switchRed.png'
image_switch_red_pressed = ':assets:images/tiles/switchRed_pressed.png'
image_torch1 = ':assets:images/tiles/torch1.png'
image_torch2 = ':assets:images/tiles/torch2.png'
image_torch_off = ':assets:images/tiles/torchOff.png'
image_water = ':assets:images/tiles/water.png'
image_water_top_high = ':assets:images/tiles/waterTop_high.png'
image_water_top_low = ':assets:images/tiles/waterTop_low.png'
image_tank_blue_barrel1 = ':assets:images/topdown_tanks/tankBlue_barrel1.png'
image_tank_blue_barrel1_outline = ':assets:images/topdown_tanks/tankBlue_barrel1_outline.png'
image_tank_blue_barrel2 = ':assets:images/topdown_tanks/tankBlue_barrel2.png'
image_tank_blue_barrel2_outline = ':assets:images/topdown_tanks/tankBlue_barrel2_outline.png'
image_tank_blue_barrel3 = ':assets:images/topdown_tanks/tankBlue_barrel3.png'
image_tank_blue_barrel3_outline = ':assets:images/topdown_tanks/tankBlue_barrel3_outline.png'
image_tank_body_big_red = ':assets:images/topdown_tanks/tankBody_bigRed.png'
image_tank_body_big_red_outline = ':assets:images/topdown_tanks/tankBody_bigRed_outline.png'
image_tank_body_blue = ':assets:images/topdown_tanks/tankBody_blue.png'
image_tank_body_blue_outline = ':assets:images/topdown_tanks/tankBody_blue_outline.png'
image_tank_body_dark = ':assets:images/topdown_tanks/tankBody_dark.png'
image_tank_body_dark_large = ':assets:images/topdown_tanks/tankBody_darkLarge.png'
image_tank_body_dark_large_outline = ':assets:images/topdown_tanks/tankBody_darkLarge_outline.png'
image_tank_body_dark_outline = ':assets:images/topdown_tanks/tankBody_dark_outline.png'
image_tank_body_green = ':assets:images/topdown_tanks/tankBody_green.png'
image_tank_body_green_outline = ':assets:images/topdown_tanks/tankBody_green_outline.png'
image_tank_body_huge = ':assets:images/topdown_tanks/tankBody_huge.png'
image_tank_body_huge_outline = ':assets:images/topdown_tanks/tankBody_huge_outline.png'
image_tank_body_red = ':assets:images/topdown_tanks/tankBody_red.png'
image_tank_body_red_outline = ':assets:images/topdown_tanks/tankBody_red_outline.png'
image_tank_body_sand = ':assets:images/topdown_tanks/tankBody_sand.png'
image_tank_body_sand_outline = ':assets:images/topdown_tanks/tankBody_sand_outline.png'
image_tank_dark_barrel1 = ':assets:images/topdown_tanks/tankDark_barrel1.png'
image_tank_dark_barrel1_outline = ':assets:images/topdown_tanks/tankDark_barrel1_outline.png'
image_tank_dark_barrel2 = ':assets:images/topdown_tanks/tankDark_barrel2.png'
image_tank_dark_barrel2_outline = ':assets:images/topdown_tanks/tankDark_barrel2_outline.png'
image_tank_dark_barrel3 = ':assets:images/topdown_tanks/tankDark_barrel3.png'
image_tank_dark_barrel3_outline = ':assets:images/topdown_tanks/tankDark_barrel3_outline.png'
image_tank_green_barrel1 = ':assets:images/topdown_tanks/tankGreen_barrel1.png'
image_tank_green_barrel1_outline = ':assets:images/topdown_tanks/tankGreen_barrel1_outline.png'
image_tank_green_barrel2 = ':assets:images/topdown_tanks/tankGreen_barrel2.png'
image_tank_green_barrel2_outline = ':assets:images/topdown_tanks/tankGreen_barrel2_outline.png'
image_tank_green_barrel3 = ':assets:images/topdown_tanks/tankGreen_barrel3.png'
image_tank_green_barrel3_outline = ':assets:images/topdown_tanks/tankGreen_barrel3_outline.png'
image_tank_red_barrel1 = ':assets:images/topdown_tanks/tankRed_barrel1.png'
image_tank_red_barrel1_outline = ':assets:images/topdown_tanks/tankRed_barrel1_outline.png'
image_tank_red_barrel2 = ':assets:images/topdown_tanks/tankRed_barrel2.png'
image_tank_red_barrel2_outline = ':assets:images/topdown_tanks/tankRed_barrel2_outline.png'
image_tank_red_barrel3 = ':assets:images/topdown_tanks/tankRed_barrel3.png'
image_tank_red_barrel3_outline = ':assets:images/topdown_tanks/tankRed_barrel3_outline.png'
image_tank_sand_barrel1 = ':assets:images/topdown_tanks/tankSand_barrel1.png'
image_tank_sand_barrel1_outline = ':assets:images/topdown_tanks/tankSand_barrel1_outline.png'
image_tank_sand_barrel2 = ':assets:images/topdown_tanks/tankSand_barrel2.png'
image_tank_sand_barrel2_outline = ':assets:images/topdown_tanks/tankSand_barrel2_outline.png'
image_tank_sand_barrel3 = ':assets:images/topdown_tanks/tankSand_barrel3.png'
image_tank_sand_barrel3_outline = ':assets:images/topdown_tanks/tankSand_barrel3_outline.png'
image_tank_blue = ':assets:images/topdown_tanks/tank_blue.png'
image_tank_dark = ':assets:images/topdown_tanks/tank_dark.png'
image_tank_green = ':assets:images/topdown_tanks/tank_green.png'
image_tank_red = ':assets:images/topdown_tanks/tank_red.png'
image_tank_sand = ':assets:images/topdown_tanks/tank_sand.png'
image_tile_grass1 = ':assets:images/topdown_tanks/tileGrass1.png'
image_tile_grass2 = ':assets:images/topdown_tanks/tileGrass2.png'
image_tile_grass_road_corner_l_l = ':assets:images/topdown_tanks/tileGrass_roadCornerLL.png'
image_tile_grass_road_corner_l_r = ':assets:images/topdown_tanks/tileGrass_roadCornerLR.png'
image_tile_grass_road_corner_u_l = ':assets:images/topdown_tanks/tileGrass_roadCornerUL.png'
image_tile_grass_road_corner_u_r = ':assets:images/topdown_tanks/tileGrass_roadCornerUR.png'
image_tile_grass_road_crossing = ':assets:images/topdown_tanks/tileGrass_roadCrossing.png'
image_tile_grass_road_crossing_round = ':assets:images/topdown_tanks/tileGrass_roadCrossingRound.png'
image_tile_grass_road_east = ':assets:images/topdown_tanks/tileGrass_roadEast.png'
image_tile_grass_road_north = ':assets:images/topdown_tanks/tileGrass_roadNorth.png'
image_tile_grass_road_split_e = ':assets:images/topdown_tanks/tileGrass_roadSplitE.png'
image_tile_grass_road_split_n = ':assets:images/topdown_tanks/tileGrass_roadSplitN.png'
image_tile_grass_road_split_s = ':assets:images/topdown_tanks/tileGrass_roadSplitS.png'
image_tile_grass_road_split_w = ':assets:images/topdown_tanks/tileGrass_roadSplitW.png'
image_tile_grass_road_transition_e = ':assets:images/topdown_tanks/tileGrass_roadTransitionE.png'
image_tile_grass_road_transition_e_dirt = ':assets:images/topdown_tanks/tileGrass_roadTransitionE_dirt.png'
image_tile_grass_road_transition_n = ':assets:images/topdown_tanks/tileGrass_roadTransitionN.png'
image_tile_grass_road_transition_n_dirt = ':assets:images/topdown_tanks/tileGrass_roadTransitionN_dirt.png'
image_tile_grass_road_transition_s = ':assets:images/topdown_tanks/tileGrass_roadTransitionS.png'
image_tile_grass_road_transition_s_dirt = ':assets:images/topdown_tanks/tileGrass_roadTransitionS_dirt.png'
image_tile_grass_road_transition_w = ':assets:images/topdown_tanks/tileGrass_roadTransitionW.png'
image_tile_grass_road_transition_w_dirt = ':assets:images/topdown_tanks/tileGrass_roadTransitionW_dirt.png'
image_tile_grass_transition_e = ':assets:images/topdown_tanks/tileGrass_transitionE.png'
image_tile_grass_transition_n = ':assets:images/topdown_tanks/tileGrass_transitionN.png'
image_tile_grass_transition_s = ':assets:images/topdown_tanks/tileGrass_transitionS.png'
image_tile_grass_transition_w = ':assets:images/topdown_tanks/tileGrass_transitionW.png'
image_tile_sand1 = ':assets:images/topdown_tanks/tileSand1.png'
image_tile_sand2 = ':assets:images/topdown_tanks/tileSand2.png'
image_tile_sand_road_corner_l_l = ':assets:images/topdown_tanks/tileSand_roadCornerLL.png'
image_tile_sand_road_corner_l_r = ':assets:images/topdown_tanks/tileSand_roadCornerLR.png'
image_tile_sand_road_corner_u_l = ':assets:images/topdown_tanks/tileSand_roadCornerUL.png'
image_tile_sand_road_corner_u_r = ':assets:images/topdown_tanks/tileSand_roadCornerUR.png'
image_tile_sand_road_crossing = ':assets:images/topdown_tanks/tileSand_roadCrossing.png'
image_tile_sand_road_crossing_round = ':assets:images/topdown_tanks/tileSand_roadCrossingRound.png'
image_tile_sand_road_east = ':assets:images/topdown_tanks/tileSand_roadEast.png'
image_tile_sand_road_north = ':assets:images/topdown_tanks/tileSand_roadNorth.png'
image_tile_sand_road_split_e = ':assets:images/topdown_tanks/tileSand_roadSplitE.png'
image_tile_sand_road_split_n = ':assets:images/topdown_tanks/tileSand_roadSplitN.png'
image_tile_sand_road_split_s = ':assets:images/topdown_tanks/tileSand_roadSplitS.png'
image_tile_sand_road_split_w = ':assets:images/topdown_tanks/tileSand_roadSplitW.png'
image_tracks_double = ':assets:images/topdown_tanks/tracksDouble.png'
image_tracks_large = ':assets:images/topdown_tanks/tracksLarge.png'
image_tracks_small = ':assets:images/topdown_tanks/tracksSmall.png'
image_tree_brown_large = ':assets:images/topdown_tanks/treeBrown_large.png'
image_tree_brown_small = ':assets:images/topdown_tanks/treeBrown_small.png'
image_tree_green_large = ':assets:images/topdown_tanks/treeGreen_large.png'
image_tree_green_small = ':assets:images/topdown_tanks/treeGreen_small.png'
music_1918 = ':assets:music/1918.mp3'
music_funkyrobot = ':assets:music/funkyrobot.mp3'
sound_coin1 = ':assets:sounds/coin1.wav'
sound_coin2 = ':assets:sounds/coin2.wav'
sound_coin3 = ':assets:sounds/coin3.wav'
sound_coin4 = ':assets:sounds/coin4.wav'
sound_coin5 = ':assets:sounds/coin5.wav'
sound_error1 = ':assets:sounds/error1.wav'
sound_error2 = ':assets:sounds/error2.wav'
sound_error3 = ':assets:sounds/error3.wav'
sound_error4 = ':assets:sounds/error4.wav'
sound_error5 = ':assets:sounds/error5.wav'
sound_explosion1 = ':assets:sounds/explosion1.wav'
sound_explosion2 = ':assets:sounds/explosion2.wav'
sound_fall1 = ':assets:sounds/fall1.wav'
sound_fall2 = ':assets:sounds/fall2.wav'
sound_fall3 = ':assets:sounds/fall3.wav'
sound_fall4 = ':assets:sounds/fall4.wav'
sound_gameover1 = ':assets:sounds/gameover1.wav'
sound_gameover2 = ':assets:sounds/gameover2.wav'
sound_gameover3 = ':assets:sounds/gameover3.wav'
sound_gameover4 = ':assets:sounds/gameover4.wav'
sound_gameover5 = ':assets:sounds/gameover5.wav'
sound_hit1 = ':assets:sounds/hit1.wav'
sound_hit2 = ':assets:sounds/hit2.wav'
sound_hit3 = ':assets:sounds/hit3.wav'
sound_hit4 = ':assets:sounds/hit4.wav'
sound_hit5 = ':assets:sounds/hit5.wav'
sound_hurt1 = ':assets:sounds/hurt1.wav'
sound_hurt2 = ':assets:sounds/hurt2.wav'
sound_hurt3 = ':assets:sounds/hurt3.wav'
sound_hurt4 = ':assets:sounds/hurt4.wav'
sound_hurt5 = ':assets:sounds/hurt5.wav'
sound_jump1 = ':assets:sounds/jump1.wav'
sound_jump2 = ':assets:sounds/jump2.wav'
sound_jump3 = ':assets:sounds/jump3.wav'
sound_jump4 = ':assets:sounds/jump4.wav'
sound_jump5 = ':assets:sounds/jump5.wav'
sound_laser1 = ':assets:sounds/laser1.mp3'
sound_laser1 = ':assets:sounds/laser1.ogg'
sound_laser1 = ':assets:sounds/laser1.wav'
sound_laser2 = ':assets:sounds/laser2.wav'
sound_laser3 = ':assets:sounds/laser3.wav'
sound_laser4 = ':assets:sounds/laser4.wav'
sound_laser5 = ':assets:sounds/laser5.wav'
sound_lose1 = ':assets:sounds/lose1.wav'
sound_lose2 = ':assets:sounds/lose2.wav'
sound_lose3 = ':assets:sounds/lose3.wav'
sound_lose4 = ':assets:sounds/lose4.wav'
sound_lose5 = ':assets:sounds/lose5.wav'
sound_phase_jump1 = ':assets:sounds/phaseJump1.ogg'
sound_phase_jump1 = ':assets:sounds/phaseJump1.wav'
sound_rock_hit2 = ':assets:sounds/rockHit2.ogg'
sound_rock_hit2 = ':assets:sounds/rockHit2.wav'
sound_secret2 = ':assets:sounds/secret2.wav'
sound_secret4 = ':assets:sounds/secret4.wav'
sound_upgrade1 = ':assets:sounds/upgrade1.wav'
sound_upgrade2 = ':assets:sounds/upgrade2.wav'
sound_upgrade3 = ':assets:sounds/upgrade3.wav'
sound_upgrade4 = ':assets:sounds/upgrade4.wav'
sound_upgrade5 = ':assets:sounds/upgrade5.wav'
map_dirt = ':assets:tiled_maps/dirt.json'
map_grass = ':assets:tiled_maps/grass.json'
map_items = ':assets:tiled_maps/items.json'
map_level_1 = ':assets:tiled_maps/level_1.json'
map_level_2 = ':assets:tiled_maps/level_2.json'
map_map = ':assets:tiled_maps/map.json'
map_map2_level_1 = ':assets:tiled_maps/map2_level_1.json'
map_map2_level_2 = ':assets:tiled_maps/map2_level_2.json'
map_map_with_ladders = ':assets:tiled_maps/map_with_ladders.json'
map_more_tiles = ':assets:tiled_maps/more_tiles.json'
map_pymunk_test_map = ':assets:tiled_maps/pymunk_test_map.json'
map_spritesheet = ':assets:tiled_maps/spritesheet.json'
map_standard_tileset = ':assets:tiled_maps/standard_tileset.json'
map_test_map_1 = ':assets:tiled_maps/test_map_1.json'
map_test_map_2 = ':assets:tiled_maps/test_map_2.json'
map_test_map_3 = ':assets:tiled_maps/test_map_3.json'
map_test_map_5 = ':assets:tiled_maps/test_map_5.json'
map_test_map_6 = ':assets:tiled_maps/test_map_6.json'
map_test_map_7 = ':assets:tiled_maps/test_map_7.json'
map_test_objects = ':assets:tiled_maps/test_objects.json'
video_earth = ':assets:video/earth.mp4'
gui_button_square_blue = ':system:gui_basic_assets/button_square_blue.png'
gui_button_square_blue_pressed = ':system:gui_basic_assets/button_square_blue_pressed.png'
gui_larger = ':system:gui_basic_assets/icons/larger.png'
gui_smaller = ':system:gui_basic_assets/icons/smaller.png'
gui_shield_gold = ':system:gui_basic_assets/items/shield_gold.png'
gui_sword_gold = ':system:gui_basic_assets/items/sword_gold.png'
gui_red_button_hover = ':system:gui_basic_assets/red_button_hover.png'
gui_red_button_normal = ':system:gui_basic_assets/red_button_normal.png'
gui_red_button_press = ':system:gui_basic_assets/red_button_press.png'
gui_slider_bar = ':system:gui_basic_assets/slider_bar.png'
gui_slider_thumb = ':system:gui_basic_assets/slider_thumb.png'
gui_circle_switch_off = ':system:gui_basic_assets/toggle/circle_switch_off.png'
gui_circle_switch_on = ':system:gui_basic_assets/toggle/circle_switch_on.png'
gui_switch_green = ':system:gui_basic_assets/toggle/switch_green.png'
gui_switch_red = ':system:gui_basic_assets/toggle/switch_red.png'
gui_dark_blue_gray_panel = ':system:gui_basic_assets/window/dark_blue_gray_panel.png'
gui_grey_panel = ':system:gui_basic_assets/window/grey_panel.png'
