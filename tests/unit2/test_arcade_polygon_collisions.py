import unittest
import arcade.geometry

p1 = [[400, 100],[600, 30],[800, 100],[800,0],[400,0]]
p2 = [[500,100],[600,150],[600,90]]
p3 = [[600,60],[700,50],[600,40]]
p4 = [[650,20],[750,40],[700,20]]

class test_geometry_collitions(unittest.TestCase):

    def test_that_p1_p2_do_not_collide(self):
        self.assertFalse(arcade.geometry.are_polygons_intersecting(p1,p2),"p1, and p2 should not collide")

    def test_that_p1_p3_do_collide(self):
        self.assertTrue(arcade.geometry.are_polygons_intersecting(p1, p3), "p3, and p2 should collide")

    def test_that_p1_p4_do_collide(self):
        self.assertTrue(arcade.geometry.are_polygons_intersecting(p1, p4), "p3, and p2 should collide")

    def test_that_p2_p4_do_not_collide(self):
        self.assertFalse(arcade.geometry.are_polygons_intersecting(p2, p4), "p3, and p2 should collide")

    def draw_all_polygons(self):
        import matplotlib.pyplot as plt
        import numpy as np
        h = np.array(p1)
        plt.scatter(h[:, 0], h[:, 1],c="b",label="p1")
        plt.plot(h[:, 0], h[:, 1],"b")
        plt.plot([h[-1, 0],h[0, 0]], [h[-1, 1],h[0, 1]],"b--")
        h = np.array(p2)
        plt.scatter(h[:, 0], h[:, 1],c="r",label="p2")
        plt.plot(h[:, 0], h[:, 1],"r")
        plt.plot([h[-1, 0], h[0, 0]], [h[-1, 1], h[0, 1]], "r--")
        h = np.array(p3)
        plt.scatter(h[:, 0], h[:, 1],c="g",label="p3")
        plt.plot(h[:, 0], h[:, 1],"g")
        plt.plot([h[-1, 0], h[0, 0]], [h[-1, 1], h[0, 1]], "g--")
        h = np.array(p4)
        plt.scatter(h[:, 0], h[:, 1],c="k",label="p4")
        plt.plot(h[:, 0], h[:, 1],"k")
        plt.plot([h[-1, 0], h[0, 0]], [h[-1, 1], h[0, 1]], "k--")
        plt.legend(loc='upper right')
        plt.show()

if __name__ == "__main__":
    test_geometry_collitions().draw_all_polygons()
