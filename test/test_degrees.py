import math
import unittest
from unittest import TestCase

deg2rad = math.pi / 180


class Deg2Radians(TestCase):
    def setUp(self):
        try:
            import numpy
        except:
            raise unittest.SkipTest("NumPy not installed. TestCase will skip.")

    def testDeg2radians(self):
        self.assertInterdependence(0.0)
        self.assertInterdependence(23.0)
        self.assertInterdependence(45.0)
        self.assertInterdependence(360.0)
        self.assertInterdependence(720.0)
        self.assertInterdependence(-720.4)
        self.assertInterdependence(-90.0)
        self.assertInterdependence(-10.0)
        self.assertInterdependence(-90)
        self.assertInterdependence(-10)

    def assertInterdependence(self, degrees):
        import numpy as np

        np_rad = np.deg2rad(degrees)
        math_rad = math.radians(degrees)

        self.assertFloat(np_rad)
        self.assertFloat(math_rad)
        self.assertAlmostEqual(math_rad, np_rad)

    def assertFloat(self, value):
        try:
            float(value)
        except ValueError:
            self.fail(f"Value {value} cannot be convert to float")
