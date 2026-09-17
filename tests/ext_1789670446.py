# suite extendida para: Implement a Python function `sum_range_reduce(n)` that uses `functools.reduce` a
# requiere función solve()
assert sum_range_reduce(1_000_000) == 1_000_000 * 1_000_001 // 2, "Error con n=1_000_000"
assert sum_range_reduce(0) == 0, "Error con n=0 (debe devolver 0)"
print('SUITE OK')