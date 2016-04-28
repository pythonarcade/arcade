# import arcade to use the library
import arcade


# this function is called repeatedly in order to draw the shapes and update
# their position
def on_draw(delta_time):
    """ Use this function to draw everything to the screen. """

    # start the render. This must happen before any drawing
    # commands. We do NOT need an stop render command.
    arcade.start_render()

    # draw shapes
    on_draw.ball.draw()
    on_draw.center_line.draw()
    on_draw.right_arc.draw()
    on_draw.left_arc.draw()
    on_draw.floor.draw()
    on_draw.left_leg.draw()
    on_draw.right_leg.draw()
    on_draw.body.draw()
    on_draw.neck.draw()
    on_draw.head.draw()
    on_draw.left_arm.draw()
    on_draw.right_arm_1.draw()
    on_draw.right_arm_2.draw()
    on_draw.hoop.draw()
    on_draw.backboard.draw()
    on_draw.shot_display.draw()

    # update shape positions for objects that will move
    on_draw.ball.update()
    on_draw.center_line.update()
    on_draw.right_arc.update()
    on_draw.left_arc.update()
    on_draw.right_arm_2.update()

    # code to direct movement here
    on_draw.ball.change_x = on_draw.ball_move_x
    on_draw.ball.change_y = on_draw.ball_move_y
    on_draw.center_line.change_x = on_draw.ball_move_x
    on_draw.center_line.change_y = on_draw.ball_move_y
    on_draw.right_arc.change_x = on_draw.ball_move_x
    on_draw.right_arc.change_y = on_draw.ball_move_y
    on_draw.left_arc.change_x = on_draw.ball_move_x
    on_draw.left_arc.change_y = on_draw.ball_move_y

    # shoot ball
    if on_draw.ball.center_x < 710:
        on_draw.ball_move_y -= 0.006
    elif on_draw.ball.center_x >= 710:
        on_draw.ball_move_x = 0
        on_draw.ball_move_y -= 0.25

    # flick arm
    if on_draw.right_arm_2.tilt_angle > 45:
        on_draw.right_arm_2.change_tilt_angle = on_draw.arm_flick
    else:
        on_draw.right_arm_2.change_tilt_angle = 0

    # reset the ball and arm when it goes off the screen
    if on_draw.ball.center_y < -30:
        on_draw.ball.center_x = 236
        on_draw.ball.center_y = 105

        on_draw.center_line.start_x = 236
        on_draw.center_line.end_x = 236
        on_draw.center_line.start_y = 85
        on_draw.center_line.end_y = 125

        on_draw.left_arc.center_x = 236
        on_draw.left_arc.center_y = 105

        on_draw.right_arc.center_x = 236
        on_draw.right_arc.center_y = 105

        on_draw.right_arm_2.tilt_angle = 130

        on_draw.ball_move_x = 2
        on_draw.ball_move_y = 2


# open new window and set the background
arcade.open_window("Basketball Example", 800, 600)
arcade.set_background_color(arcade.color.WHITE)

# all shapes created will require the prefix 'on_draw' in order to be
# accessible to the on_draw function

# this is the ball
on_draw.ball = arcade.Circle(236, 105, 20, arcade.color.ORANGE)
on_draw.center_line = arcade.Line(236, 85, 236, 125, arcade.color.BLACK, 1)
on_draw.right_arc = arcade.Arc(236, 105, 20, 15,
                               arcade.color.BLACK, 0, 180, 1, 270)
on_draw.left_arc = arcade.Arc(236, 105, 20, 15,
                              arcade.color.BLACK, 0, 180, 1, 90)

# this is the floor
on_draw.floor = arcade.Line(0, 5, 800, 5, arcade.color.BLACK, 5)

# this is the shooter
on_draw.left_leg = arcade.Rectangle(100, 10, 30, 7, arcade.color.RED, 0, 80)
on_draw.right_leg = arcade.Rectangle(110, 10, 30, 7, arcade.color.RED, 0, 100)
on_draw.body = arcade.Rectangle(105, 25, 30, 20, arcade.color.YELLOW, 0, 90)
on_draw.neck = arcade.Rectangle(207, 60, 7, 4, arcade.color.BLACK, 1, 90)
on_draw.head = arcade.Circle(210, 82, 10, arcade.color.BLACK, 3)
on_draw.left_arm = arcade.Rectangle(170, 20, 30, 5, arcade.color.BLACK, 2, 70)
on_draw.right_arm_1 = arcade.Rectangle(210, 50, 15, 5,
                                       arcade.color.BLACK, 2, 50)
on_draw.right_arm_2 = arcade.Rectangle(220, 60, 15, 5,
                                       arcade.color.BLACK, 2, 130)

# this draws the hoop
on_draw.backboard = arcade.Line(730, 370, 730, 470, arcade.color.BLACK, 4)
on_draw.hoop = arcade.Circle(700, 400, 30, arcade.color.DARK_GREEN, 2)

# this is the text on the screen
on_draw.shot_display = arcade.Text("Basketball", 50, 550, 50,
                                   arcade.color.PURPLE)

# declare any variables that will move an object
on_draw.ball_move_x = 2
on_draw.ball_move_y = 2

on_draw.arm_flick = -5

arcade.schedule(on_draw, 1 / 80)

arcade.run()
