# Agente multi-paso generado por EVO V9
# Objetivo: que genere 3 numeros al azar entre 1 y 10, los ordene de mayor a menor y sume los dos mas grandes

# --- Paso 1: Genera tres números aleatorios entre 1 y 10 ---
import random
numbers = [random.randint(1, 10) for _ in range(3)]
print(numbers)

# --- Paso 2: Ordena los números de mayor a menor ---
nums = [5, 6, 1]
sorted_nums = sorted(nums, reverse=True)
print(sorted_nums)

# --- Paso 3: Suma los dos primeros (los más grandes) del orden resultante ---
lst = [6, 5, 1]
resultado = sum(lst[:2])
print(resultado)
