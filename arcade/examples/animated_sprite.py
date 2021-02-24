### ====================================================================================================
### IMPORTS
### ====================================================================================================
import arcade

# CREDITS
# https://gamekrazzy.itch.io/ for the 8-direction-character

# Create facing direction values
FACE_RIGHT = 0
FACE_LEFT = 1
FACE_UP = 2
FACE_DOWN = 3
FACE_UPRIGHT = 4
FACE_UPLEFT = 5
FACE_DOWNRIGHT = 6
FACE_DOWNLEFT = 7
NB_DIRECTIONS = 8

class TestArcade(arcade.Window):

    def update_character(self, delta_time):
        # First, Check if an attack has been requested
        if self.char_attack:
            # Calling this method only if the current animation is not "attack"
            if self.character.get_current_animation() != "attack":
                # Call the animation + rewind it
                self.character.select_animation("attack", True)
            self.char_attack = False

        # Second, check if the character is doing an attack : if yes, wait for the end of the animation
        ready = True
        if self.character.get_current_animation() == "attack":
            ready = self.character.is_finished()

        # Third, process the normal behavior if ready (walk/idle + position update)
        if ready:
            # Compute direction according to keyboard inputs
            move_horizontal = -1
            move_vertical   = -1
            moving = False
            if self.char_moves[FACE_UP] and not self.char_moves[FACE_DOWN]:
                move_vertical = FACE_UP
                moving = True
            if not self.char_moves[FACE_UP] and self.char_moves[FACE_DOWN]:
                move_vertical = FACE_DOWN
                moving = True
            if self.char_moves[FACE_LEFT] and not self.char_moves[FACE_RIGHT]:
                move_horizontal= FACE_LEFT
                moving = True
            if not self.char_moves[FACE_LEFT] and self.char_moves[FACE_RIGHT]:
                move_horizontal = FACE_RIGHT
                moving = True
            # Prepare moving steps
            dx = 0
            dy = 0
            # If the player is not moving
            if not moving:
                self.character.select_animation("idle")
            else:
                # If the character is actually moving in a known direction
                if move_vertical == -1:
                    direction = move_horizontal
                    dx = 2*(0.5-move_horizontal)*60*delta_time*self.speed
                elif move_horizontal == -1:
                    direction = move_vertical
                    dy = 2*(2.5-move_vertical)*60*delta_time*self.speed
                else:
                    dx = 2*(0.5-move_horizontal)*60*delta_time*self.speed
                    dy = 2*(2.5-move_vertical)*60*delta_time*self.speed
                    direction = 2*move_vertical + move_horizontal
                self.character.select_animation("walk")
                self.character.select_state(direction)
            # Move the character according to the direction
            self.character.center_x += dx
            self.character.center_y += dy

        # Finally, update animation frame according to selected animation and facing direction
        self.character.update_animation(delta_time)

    def __init__(self, width, height, title, fullScreen):
        # Init application window
        super().__init__(width, height, title, fullScreen)
        # Set application window background color
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        # Create number objects
        self.counter = 0
        self.numbers1 = arcade.AnimatedSprite()
        self.numbers2 = arcade.AnimatedSprite()
        self.numbers3 = arcade.AnimatedSprite()
        self.numbers1.add_animation(animation_name="digit",
                                    filepath=":resources:images/spritesheets/numbers.png",
                                    nb_frames_x=10,
                                    nb_frames_y=1,
                                    frame_width=80,
                                    frame_height=128,
                                    frame_start_index=0,
                                    frame_end_index=9,
                                    frame_duration=1 / 3,
                                    flipped_horizontally=False,
                                    flipped_vertically=False,
                                    loop_counter=0,
                                    back_and_forth=False,
                                    filter_color=(255, 255, 255))
        self.numbers2.add_animation(animation_name="digit",
                                    filepath=":resources:images/spritesheets/numbers.png",
                                    nb_frames_x=10,
                                    nb_frames_y=1,
                                    frame_width=80,
                                    frame_height=128,
                                    frame_start_index=9,
                                    frame_end_index=0,
                                    frame_duration=1 / 3,
                                    flipped_horizontally=False,
                                    flipped_vertically=False,
                                    loop_counter=0,
                                    back_and_forth=False,
                                    filter_color=(255, 255, 255))
        self.numbers3.add_animation(animation_name="digit",
                                    filepath=":resources:images/spritesheets/numbers.png",
                                    nb_frames_x=10,
                                    nb_frames_y=1,
                                    frame_width=80,
                                    frame_height=128,
                                    frame_start_index=0,
                                    frame_end_index=9,
                                    frame_duration=1 / 1,
                                    flipped_horizontally=False,
                                    flipped_vertically=False,
                                    loop_counter=0,
                                    back_and_forth=False,
                                    filter_color=(255, 255, 255))

        # Create yoyo AnimatedSprite objects
        self.yoyo1 = arcade.AnimatedSprite()
        self.yoyo2 = arcade.AnimatedSprite()
        self.yoyo3 = arcade.AnimatedSprite()

        # Add animation for yoyo1 (yoyo anim)
        self.yoyo1.add_animation(animation_name="yoyo",
                                 filepath=":resources:images/spritesheets/yoyo.png",
                                 nb_frames_x=3,
                                 nb_frames_y=4,
                                 frame_width=128,
                                 frame_height=128,
                                 frame_start_index=0,
                                 frame_end_index=11,
                                 frame_duration=1/15,
                                 flipped_horizontally=False,
                                 flipped_vertically=False,
                                 loop_counter=0,
                                 back_and_forth=True,
                                 filter_color=(255,255,255))
        # Add animation for yoyo2 (Idle anim)
        self.yoyo2.add_animation(animation_name="idle",
                                 filepath=":resources:images/spritesheets/yoyo.png",
                                 nb_frames_x=3,
                                 nb_frames_y=4,
                                 frame_width=128,
                                 frame_height=128,
                                 frame_start_index=0,
                                 frame_end_index=0,     # same index for start and end (only one frame here)
                                 frame_duration=1/15,
                                 flipped_horizontally=False,
                                 flipped_vertically=False,
                                 loop_counter=0,
                                 back_and_forth=False,
                                 filter_color=(0,255,0))
        # Add animation for yoyo2 (yoyo anim)
        self.yoyo2.add_animation(animation_name="yoyo",
                                 filepath=":resources:images/spritesheets/yoyo.png",
                                 nb_frames_x=3,
                                 nb_frames_y=4,
                                 frame_width=128,
                                 frame_height=128,
                                 frame_start_index=0,
                                 frame_end_index=11,
                                 frame_duration=1/15,
                                 flipped_horizontally=False,
                                 flipped_vertically=False,
                                 loop_counter=1,            # counter is limited to once
                                 back_and_forth=True,
                                 filter_color=(255,0,0))
        # Add animation for yoyo3 (yoyo anim)
        self.yoyo3.add_animation(animation_name="yoyo",
                                 filepath=":resources:images/spritesheets/yoyo.png",
                                 nb_frames_x=3,
                                 nb_frames_y=4,
                                 frame_width=128,
                                 frame_height=128,
                                 frame_start_index=0,
                                 frame_end_index=11,
                                 frame_duration=1 / 15,
                                 flipped_horizontally=False,
                                 flipped_vertically=False,
                                 loop_counter=0,
                                 back_and_forth=True,
                                 filter_color=(0, 0, 255))

        # Prepare structures for character move
        # This contains the states of moving keys (left, right, up, down)
        self.char_moves = [False, False, False, False]
        self.character = arcade.AnimatedSprite(8)

        # Add animations for the 8 direction character
        normal_index = [6, 6, 0, 12, 3, 3, 9, 9]
        attack_index = [4, 12, 8, 0, 8, 12, 4, 0]
        flip_h = [False, True, False, False, False, True, False, True]
        for i in range(NB_DIRECTIONS):
            # Add walking animations for each facing_direction
            self.character.add_animation(
                                     animation_name="walk",
                                     filepath=":resources:images/spritesheets/character.png",
                                     nb_frames_x=3,
                                     nb_frames_y=5,
                                     frame_width=64,
                                     frame_height=64,
                                     frame_start_index=normal_index[i],
                                     frame_end_index=normal_index[i]+2,
                                     frame_duration=1/10,
                                     flipped_horizontally=flip_h[i],
                                     flipped_vertically=False,
                                     loop_counter=0,
                                     back_and_forth=True,
                                     animation_state=i)
            # Add idle animations for each facing_direction
            self.character.add_animation(
                                     animation_name="idle",
                                     filepath=":resources:images/spritesheets/character.png",
                                     nb_frames_x=3,
                                     nb_frames_y=5,
                                     frame_width=64,
                                     frame_height=64,
                                     frame_start_index=normal_index[i]+1,
                                     frame_end_index=normal_index[i]+1,
                                     frame_duration=1/10,
                                     flipped_horizontally=flip_h[i],
                                     flipped_vertically=False,
                                     loop_counter=0,
                                     back_and_forth=False,
                                     animation_state=i)
            # Add attack animations for each facing_direction
            self.character.add_animation(
                                     animation_name="attack",
                                     filepath=":resources:images/spritesheets/character_attack.png",
                                     nb_frames_x=4,
                                     nb_frames_y=4,
                                     frame_width=192,
                                     frame_height=192,
                                     frame_start_index=attack_index[i],
                                     frame_end_index=attack_index[i]+3,
                                     frame_duration=1/12,
                                     flipped_horizontally=False,
                                     flipped_vertically=False,
                                     loop_counter=1,
                                     back_and_forth=False,
                                     animation_state=i)

        # Set position for counter
        self.numbers1.center_x = 100
        self.numbers1.center_y = 500
        self.numbers2.center_x = 400
        self.numbers2.center_y = 500
        self.numbers3.center_x = 700
        self.numbers3.center_y = 500

        # Set positions ofr yoyo
        self.yoyo1.center_x = 650
        self.yoyo1.center_y = 200
        self.yoyo2.center_x = 100
        self.yoyo2.center_y = 200
        self.yoyo3.center_x = 375
        self.yoyo3.center_y = 50

        # By default the character is idle and facing down
        self.character.center_x = 400
        self.character.center_y = 360
        self.character.select_animation("idle")
        self.character.select_state(FACE_DOWN)
        self.character.scale = 2
        self.speed = 3
        self.char_attack = False

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("[yoyo2] Press ENTER to run only once", 10, 230, (0, 255, 0))
        arcade.draw_text("[yoyo1] Infinite and back-and-forth animation", 500, 230, (255, 255, 255))
        arcade.draw_text("[yoyo3] Infinite and back-and-forth animation", 230, 100, (0, 0, 255))
        arcade.draw_text("[numbers1] Infinite forward animation", 10, 550, (255, 255, 0))
        arcade.draw_text("[numbers2] Infinite backward animation", 275, 550, (255, 255, 0))
        arcade.draw_text("[numbers3] Press +/- to update counter", 550, 550, (255, 255, 0))
        arcade.draw_text("[character] use arrows & space bar", 275, 275, (255, 255, 255))
        self.numbers1.draw()
        self.numbers2.draw()
        self.numbers3.draw()
        self.yoyo1.draw()
        self.yoyo2.draw()
        self.yoyo3.draw()
        self.character.draw()

    def update(self, delta_time):
        # update animations for counter
        self.numbers1.update_animation(delta_time)
        self.numbers2.update_animation(delta_time)
        self.numbers3.select_frame(self.counter)
        self.numbers3.update_animation(delta_time)
        # update animations for the 3 yoyos
        self.yoyo1.update_animation(delta_time)
        self.yoyo2.update_animation(delta_time)
        self.yoyo3.update_animation(delta_time)
        # move and turn the yoyo2 according to animation progression
        # 1 turn and a half when yoyo is fully extended
        percent1 = self.yoyo1.get_percent()
        k1 = 2*abs(0.5-percent1)
        k2 = 2 * (0.5 - abs(0.5 - percent1))
        self.yoyo1.center_y =50 + (k1 * 150)
        self.yoyo1.angle = (1.5 * 360) * k2
       # update Y position and angle for yoyo2 (only if the animation is requested : press SPACE bar to run)
        if self.yoyo2.get_current_animation() == "yoyo":
            # Select the "idle" animation when the "yoyo" one is finished
            if self.yoyo2.is_finished():
                self.yoyo2.select_animation("idle")
            # move and turn the yoyo2 according to animation progression
            # 1 turn and a half when yoyo is fully extended
            percent = self.yoyo2.get_percent()
            k1 = 2 * abs(0.5 - percent)
            k2 = 2 * (0.5 - abs(0.5 - percent))
            self.yoyo2.center_y = 50 + (k1 * 150)
            self.yoyo2.angle = (1.5 * 360) * k2
        # update character animation and position
        self.update_character(delta_time)

    def on_key_press(self, key, modifiers):
        # Launch 1 time yoyo
        if key == arcade.key.ENTER:
            if self.yoyo2.get_current_animation() == "idle":
                self.yoyo2.select_animation("yoyo",rewind=True, running=True)
        # update counter
        if key == arcade.key.NUM_ADD:
            self.counter = (self.counter+1)%10
        if key == arcade.key.NUM_SUBTRACT:
            self.counter = (self.counter+9)%10
        #Store the flags to tell the character is moving in one of 4 directions
        if key == arcade.key.UP:
            self.char_moves[FACE_UP] = True
        if key == arcade.key.DOWN:
            self.char_moves[FACE_DOWN] = True
        if key == arcade.key.LEFT:
            self.char_moves[FACE_LEFT] = True
        if key == arcade.key.RIGHT:
            self.char_moves[FACE_RIGHT] = True
        if key == arcade.key.SPACE:
            self.char_attack = True

    def on_key_release(self, key, modifiers):
        # Store the flags to tell the character is moving in one of 4 directions
        if key == arcade.key.UP:
            self.char_moves[FACE_UP] = False
        if key == arcade.key.DOWN:
            self.char_moves[FACE_DOWN] = False
        if key == arcade.key.LEFT:
            self.char_moves[FACE_LEFT] = False
        if key == arcade.key.RIGHT:
            self.char_moves[FACE_RIGHT] = False

def main():
    game = TestArcade(800, 600, "Test arcade.AnimatedSprite class", False)
    game.set_vsync(True)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()


