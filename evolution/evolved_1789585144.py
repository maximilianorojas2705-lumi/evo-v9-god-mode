#!/usr/bin/env 3
# Suma creativa de 1 a 100 usando una función lambda y reduce

from functools import reduce

def suma_rango(inicio: int, fin: int) -> int:
    return reduce(lambda acc, x: acc + x, range(inicio, fin + 1), 0)

if __name__ == "__main__":
    total = suma_rango(1, 100)
    print(f"La suma de 1 a 100 es: {total}")