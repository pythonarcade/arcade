import random
import timeit
import math

floats = [random.random() * 1000 for _ in range(100_000)]
i1 = [int(v) for v in floats]
i2 = [math.trunc(v) for v in floats]
print(i1 == i2)


def trunc_int():
    for v in floats:
        int(v)


def trunc_math():
    for v in floats:
        math.trunc(v)


def trunc_round():
    for v in floats:
        round(v, 0)


res_1 = timeit.timeit(trunc_int, number=100, globals=globals())
print("int(v)", res_1)
res_2 = timeit.timeit(trunc_math, number=100, globals=globals())
print("math.trunc(v)", res_2)
res_3 = timeit.timeit(trunc_round, number=100, globals=globals())
print("round(v)", res_3)
