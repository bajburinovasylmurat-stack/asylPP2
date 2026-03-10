n = [1, 2, 3, 4, 5]
s = list(map(lambda x: x**2, n))
e = list(filter(lambda x: x % 2 == 0, n))
print(s)
print(e)

from functools import reduce
t = reduce(lambda a, b: a + b, n)
print(t)