import math
import timeit
from pprint import pprint
from random import shuffle

import numpy
import numpy as np
from numpy import arange

DEG = 268.0

deg2rad = math.pi / 180.0
degrees = list(arange(-780, 720, 0.01))
shuffle(degrees)


def test_python():
    for i in degrees:
        r = deg2rad * i


def test_native():
    for i in degrees:
        math.radians(i)


def test_np_batch():
    np.deg2rad(numpy.asarray(degrees))


def test_np_single():
    for i in degrees:
        np.deg2rad(i)


def bench(snippet):
    print(snippet + ": " + str(timeit.timeit(snippet, number=1000, globals=globals()) / len(degrees)))


if __name__ == '__main__':
    pprint(degrees)

    bench("test_python()")
    bench("test_native()")
    bench("test_np_batch()")
    # bench("test_np_single()")
