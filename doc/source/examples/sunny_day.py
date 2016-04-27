import arcade

def on_draw(delta_time):
    """ Use this function to draw everything to the screen. """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need an stop render command.
    arcade.start_render()

    # Draw shapes
    arcade.draw_all(shapes)


arcade.open_window("Drawing Example", 800, 600)

#sets the background color
arcade.set_background_color(arcade.color.SKY_BLUE)

shapes = []

#Green Hills in background
on_draw.hills = arcade.Ellipse(10,100,250,200,arcade.color.GREEN)
shapes.append(on_draw.hills)
on_draw.hills = arcade.Ellipse(400,10,250,200,arcade.color.GREEN)
shapes.append(on_draw.hills)
on_draw.hills = arcade.Ellipse(800,70,250,200,arcade.color.GREEN)
shapes.append(on_draw.hills)

#The cool sun
on_draw.sun = arcade.Circle(500,500,70,arcade.color.YELLOW)
shapes.append(on_draw.sun)

#the few coulds
on_draw.clouds = arcade.Circle(200,500,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(220,500,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(200,520,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)

on_draw.clouds = arcade.Circle(750,500,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(720,500,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(700,520,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(700,480,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(677,500,23,arcade.color.WHITE)
shapes.append(on_draw.clouds)
on_draw.clouds = arcade.Circle(660,510,20,arcade.color.WHITE)
shapes.append(on_draw.clouds)

#the road
on_draw.road = arcade.Rectangle(200,2,800,15,arcade.color.GRAY)
shapes.append(on_draw.road)

####START OF RED AND WHITE SEMI

#white rectangle that make the trailer to the semi
on_draw.trailer = arcade.Rectangle(200,48,300,100,arcade.color.WHITE)
shapes.append(on_draw.trailer)

#red rectangle that makes up the cabin of the semi
on_draw.semi = arcade.Rectangle(293,43,70,80,arcade.color.RED_ORANGE)
shapes.append(on_draw.semi)

#both black circles for the tires of the semi
on_draw.tires = arcade.Circle(275,30,20,arcade.color.BLACK)
shapes.append(on_draw.tires)
on_draw.tires = arcade.Circle(520,30,20,arcade.color.BLACK)
shapes.append(on_draw.tires)
on_draw.tires = arcade.Circle(595,30,20,arcade.color.BLACK)
shapes.append(on_draw.tires)

####END OF SEMI

####START OF ORANGE CAR

#body of the car
on_draw.car = arcade.Rectangle(30,28,60,60,arcade.color.ORANGE)
shapes.append(on_draw.car)
on_draw.car = arcade.Rectangle(10,21.5,35,35,arcade.color.ORANGE)
shapes.append(on_draw.car)
on_draw.car = arcade.Rectangle(50,21.5,35,35,arcade.color.ORANGE)
shapes.append(on_draw.car)

#tires of car
on_draw.tires = arcade.Circle(18,20,11,arcade.color.BLACK)
shapes.append(on_draw.tires)
on_draw.tires = arcade.Circle(100,20,11,arcade.color.BLACK)
shapes.append(on_draw.tires)

####END OF CAR


arcade.schedule(on_draw, 1 / 80)

arcade.run()

#unnecssary if drawing with on_draw
#arcade.finish_render()
