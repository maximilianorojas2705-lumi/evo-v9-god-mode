# suite extendida para: sumar los dígitos de un número
# requiere función solve()
assert solve(10**100 - 1) == 9 * 100
assert solve(-int('987654321' * 10)) == sum(int(d) for d in '987654321' * 10)
print('SUITE OK')