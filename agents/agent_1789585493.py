# Agente multi-paso generado por EVO V9
# Objetivo: que genere 5 numeros al azar, calcule su promedio y diga si es mayor a 50

# --- Paso 1: Generar 5 números aleatorios ---
import random

# Generar 5 números aleatorios entre 0 y 100
random_numbers = [random.randint(0, 100) for _ in range(5)]

print(random_numbers)

# --- Paso 2: Calcular el promedio de esos 5 números ---
```python
numbers = [53, 32, 70, 40, 3]
print(sum(numbers) / len(numbers))
```

# --- Paso 3: Comparar el promedio con 50 y anunciar si es mayor ---
```python
# Supongamos que la lista de valores se llama `valores`
valores = [45, 55, 60, 30, 80]  # Puedes reemplazarla por los datos reales

promedio = sum(valores) / len(valores)

if promedio > 50:
    print(f"El promedio ({promedio:.2f}) es mayor que 50.")
else:
    print(f"El promedio ({promedio:.2f}) no es mayor que 50.")
```
