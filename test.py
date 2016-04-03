import arcade
arcade.open_window("Sprite Example", 800, 600)
player = arcade.PlatformerSpriteSheetSprite()
top_trim = 100
ltrim = 2
rtrim = 2
image_location_list = [
 [520 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
 [520 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
 [520 + ltrim, 0 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
 [390 + ltrim, 1548 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
 [390 + ltrim, 1290 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
 [390 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
 [390 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim]]
filename = "doc/source/examples/images/spritesheet_complete.png"
texture_info_list = arcade.load_textures(filename, image_location_list)
for texture_info in texture_info_list:
     texture = texture_info
     player.append_texture(texture)
texture_info_list = arcade.load_textures(\
filename, image_location_list, True)
for texture_info in texture_info_list:
     texture = texture_info
     player.append_texture(texture)
player.set_left_walk_textures([12, 13])
player.set_right_walk_textures([5, 6])
player.set_left_jump_textures([10])
player.set_right_jump_textures([3])
player.set_left_stand_textures([11])
player.set_right_stand_textures([4])
player.texture_change_distance = 5
player.speed = 10
player.set_position(5, 5)
player.jump()
player.change_x = 10 # Jump
player.change_y = 1
player.update()
player.go_left()
player.update()
player.stop_left()
player.update()
player.face_left()
player.update()
player.change_x = -10 #Left
player.change_y = 0.0
player.update()
player.go_left()
player.update()
player.update()
player.update()
player.stop_left()
player.update()
player.face_right()
player.change_x = 10 # Right
player.change_y = 0.0
print("Ping")
player.update()
player.go_right()
player.update()
player.update()
player.update()
player.stop_right()
player.update()
player.stop_right()
player.change_x = 0 # Stop
player.change_y = 0.0
player.update()
player.update()
player.kill()
arcade.quick_run(0.25)