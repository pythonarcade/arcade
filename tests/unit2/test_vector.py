import unittest
from math import pi

import arcade


class TestVector(unittest.TestCase):
    def setUp(self):
        self.v1 = arcade.Vector()
        self.v2 = arcade.Vector()

    def test_string_representation(self):
        self.assertEqual("Vector(x=0, y=0)", str(self.v1))

    def test_can_access_and_modify_properties(self):
        self.v1.x = 10
        self.v1.y = 2
        self.assertEqual(arcade.Vector(10, 2), self.v1)

    def test_equality_with_iterable(self):
        self.assertEqual((0, 0), self.v1, "Should be equal to tuple.")
        self.assertEqual([1, 2], arcade.Vector(1, 2), "Should be equal to list.")

    def test_can_access_fields_with_index(self):
        v = arcade.Vector(5, 11)
        self.assertEqual(5, v[0], "Should access x with index 0.")
        self.assertEqual(11, v[1], "Should access y with index 1.")

    def test_can_modify_fields_with_index(self):
        self.v1[0] = 17
        self.v1[1] = 18
        self.assertEqual(arcade.Vector(17, 18), self.v1)

    def test_cannot_dynamically_add_fields(self):
        with self.assertRaises(AttributeError, msg="Should not be allowed to dynamically add fields."):
            self.v1.something = "Not allowed"

    def test_add_returns_new_vector(self):
        v1 = arcade.Vector(3, 5)
        v2 = arcade.Vector(7, 11)
        v3 = v1 + v2
        self.assertEqual(arcade.Vector(10, 16), v3, "Should add two vectors.")
        self.assertTrue(v3 is not v1, "Should not be the same object.")
        self.assertTrue(v3 is not v2, "Should not be the same object.")

    def test_add_with_tuple(self):
        v1 = arcade.Vector(3, 5)
        v2 = (7, 11)
        v3 = v1 + v2
        self.assertIsInstance(v3, arcade.Vector, "Should create new Vector.")
        self.assertEqual(arcade.Vector(10, 16), v3, "Should add tuple to Vector.")

    def test_iadd(self):
        v1 = arcade.Vector(1, 3)
        old_v1 = v1
        v1 += arcade.Vector(5, 7)
        self.assertEqual((6, 10), v1)
        self.assertIs(old_v1, v1, "iadd should not return a new object.")
        # TODO: Consider effect of inplace add on arcade recalculaing position hash
        # Maybe just return new object with iadd.

    def test_iadd_with_iterable(self):
        v = arcade.Vector(1, 3)
        v += [4, 5]
        self.assertEqual((5, 8), v, "Should be able to iadd a list.")
        v += (5, 7)
        self.assertEqual((10, 15), v, "Should be able to iadd a tuple.")

    def test_sub_returns_new_vector(self):
        v1 = arcade.Vector(3, 5)
        v2 = arcade.Vector(7, 11)
        v3 = v1 - v2
        self.assertEqual(arcade.Vector(-4, -6), v3, "Should subtract two vectors.")
        self.assertTrue(v3 is not v1, "Should not be the same object.")
        self.assertTrue(v3 is not v2, "Should not be the same object.")

    def test_isub(self):
        v1 = arcade.Vector(1, 5)
        old_v1 = v1
        v1 -= arcade.Vector(5, 7)
        self.assertEqual((-4, -2), v1)
        self.assertIs(old_v1, v1, "isub should not return a new object.")
        # TODO: Consider effect of inplace sub on arcade recalculaing position hash
        # Maybe just return new object with isub.
        v1 -= (3, 7)
        self.assertEqual((-7, -9), v1, "Should isub tuples.")
        v1 -= (3, 7)
        self.assertEqual([-10, -16], v1, "Should isub lists.")

    def test_mult_by_scalar(self):
        v1 = arcade.Vector(1, 3)
        v2 = v1 * 5
        self.assertIsNot(v1, v2)
        self.assertEqual((5, 15), v2, "Should return new vector, each property multiplied.")

    def test_mult_by_vector(self):
        v1 = arcade.Vector(1, 3)
        v2 = (2, 3)
        v3 = v1 * v2
        self.assertIsNot(v1, v3)
        self.assertIsNot(v2, v3)
        self.assertEqual((2, 9), v3)

    def test_rmul(self):
        v1 = arcade.Vector(3, 5)
        v2 = 5 * v1
        self.assertEqual(arcade.Vector(15, 25), v2, "Should right-multiply by a number.")

    def test_imul(self):
        v = arcade.Vector(5, 7)
        old_v = v
        v *= arcade.Vector(2, 3)
        self.assertIs(old_v, v, "Should not return new vector for imul.")
        # todo: consider inplace consequences with arcade spatial hash reset
        self.assertEqual((10, 21), v)
        v *= (2, 3)
        self.assertEqual((20, 63), v)
        v *= 2
        self.assertEqual((40, 126), v)

    def test_div_with_scalar(self):
        v1 = arcade.Vector(10, 10)
        v2 = v1 / 2
        self.assertEqual((5, 5), v2, "Should divide by a single number.")

    def test_div_with_vector(self):
        v1 = arcade.Vector(10, 10)
        v2 = arcade.Vector(2, 5)
        v3 = v1 / v2
        self.assertEqual((5, 2), v3, "Should divide by another vector.")

    def test_rdiv(self):
        v1 = arcade.Vector(2, 3)
        v2 = 18 / v1
        self.assertEqual(arcade.Vector(9, 6), v2, "Should right-divide a number.")

    def test_idiv(self):
        v1 = arcade.Vector(25, 15)
        old_v1 = v1
        v1 /= 5
        self.assertEqual((5, 3), v1, "Should divide in-place with scalar.")
        self.assertIs(old_v1, v1, "Should not return a new Vector object for idiv.")
        # TODO: consider inplace consequences with arcade spatial hash reset

        v1 = arcade.Vector(50, 50)
        v2 = arcade.Vector(5, 10)
        v1 /= v2
        self.assertEqual((10, 5), v1, "Should divide in-place with other vector.")

    def test_vector_is_splattable(self):
        self.v2.x = 5
        self.v2.y = 11
        x, y = self.v1
        x2, y2 = self.v2
        self.assertEqual((0, 0), (x, y))
        self.assertEqual((5, 11), (x2, y2))

    def test_magnitude_sq(self):
        self.assertEqual(0, arcade.Vector().magnitude_sq)
        self.assertEqual(5**2, arcade.Vector(3, 4).magnitude_sq)

    def test_magnitude(self):
        self.assertEqual(0, arcade.Vector().magnitude)
        self.assertEqual(5, arcade.Vector(3, 4).magnitude)

    def test_normalize(self):
        v1 = arcade.Vector(-8, 6)
        v1.normalize()
        self.assertEqual((-0.8, 0.6), v1, "Should normalize in-place.")

        v1 = arcade.Vector(0, 0)
        v1.normalize()
        self.assertEqual((0, 0), v1, "Should handle division by zero error.")

    def test_shoot_lazer_toward_player(self):
        """Useful for directing lazer bolts toward a point."""
        enemy_pos = arcade.Vector(50, 50)
        player_pos = arcade.Vector(100, 100)

        lazer_speed = 5  # px/frame
        lazer_velocity = (player_pos - enemy_pos).normalize() * lazer_speed
        self.assertEqual(5, lazer_velocity.magnitude, "Should set speed to 5.")
        self.assertEqual(45, lazer_velocity.heading, "Should be traveling toward player.")

    # def test_shoot_lazer_from_player_at_same_heading(self):
    #     player = arcade.Sprite()
    #     player.angle = 20
    #
    #     lazer_speed = 5  # px/frame
    #     lazer_velocity = arcade.Vector.from_angle(player.angle) * lazer_speed

    def test_heading_radians(self):
        self.assertEqual(pi / 2, arcade.Vector(0, 1).heading_radians)
        self.assertEqual(pi, arcade.Vector(-1, 0).heading_radians)
        self.assertEqual(-pi / 2, arcade.Vector(0, -1).heading_radians)

    def test_heading_returns_degrees(self):
        self.assertEqual(0, arcade.Vector(0, 0).heading)
        self.assertEqual(0, arcade.Vector(1, 0).heading)
        self.assertEqual(45, arcade.Vector(1, 1).heading)
        self.assertEqual(90, arcade.Vector(0, 1).heading)
        self.assertEqual(135, arcade.Vector(-1, 1).heading)
        self.assertEqual(180, arcade.Vector(-1, 0).heading)
        self.assertEqual(-135, arcade.Vector(-1, -1).heading)

    # test limit








if __name__ == '__main__':
    unittest.main()


# TODO: Test arcade.Sprite position setter to allow tuple assignment e.g., s.position = (1, 1)
