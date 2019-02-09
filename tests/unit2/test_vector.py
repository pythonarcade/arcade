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

    def test_mult_by_single_value(self):
        v1 = arcade.Vector(1, 3)
        v2 = v1 * 5
        self.assertIsNot(v1, v2)
        self.assertEqual((5, 15), v2, "Should return new vector, each property multiplied.")

    def test_mult_by_iterable(self):
        v1 = arcade.Vector(1, 3)
        v2 = (2, 3)
        v3 = v1 * v2
        self.assertIsNot(v1, v3)
        self.assertIsNot(v2, v3)
        self.assertEqual((2, 9), v3)

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

    # TODO: test div and idiv

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

    # TODO: test set magnitude?

    def test_normalize_static(self):
        v1 = arcade.Vector(5, 5)
        v2 = arcade.Vector.normalize(v1)
        self.assertEqual((1, 1), v2)
        self.assertIsNot(v1, v2)
        self.assertEqual((1, 0.5), arcade.Vector.normalize((2, 1)))
        self.assertEqual((0.5, 1), arcade.Vector.normalize((1, 2)))
        self.assertEqual((-1, 0), arcade.Vector.normalize((-4, 0)))
        self.assertEqual((0, 0), arcade.Vector.normalize((0, 0)))
        self.assertEqual((1, 0), arcade.Vector.normalize((0.5, 0)))
        self.assertEqual((1, -1), arcade.Vector.normalize((0.5, -0.5)))

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
