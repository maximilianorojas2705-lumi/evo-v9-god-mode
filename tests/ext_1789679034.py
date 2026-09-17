# suite extendida para: sumar los dígitos de un número
# requiere función solve()
import builtins
_original_input = builtins.input

builtins.input = lambda: "9876543210123456789"
assert solve() == 90

builtins.input = lambda: "-123456789012345678901234567890"
assert solve() == 135

builtins.input = _original_input
print('SUITE OK')