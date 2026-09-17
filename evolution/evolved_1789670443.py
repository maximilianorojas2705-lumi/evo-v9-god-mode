import functools

def sum_range_reduce(n):
    return functools.reduce(lambda acc, x: acc + x, range(1, n + 1), 0)

# Test
assert sum_range_reduce(100) == 5050, "La suma de 1 a 100 debería ser 5050"
print("Test passed: sum_range_reduce(100) == 5050")