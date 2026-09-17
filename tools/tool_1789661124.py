def safe_divide(a, b):
    """Divide a by b, returning None if division by zero occurs."""
    try:
        return a / b
    except ZeroDivisionError:
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python divide_tool.py <numerador> <denominador>")
        sys.exit(1)
    try:
        num = float(sys.argv[1])
        den = float(sys.argv[2])
    except ValueError:
        print("Los argumentos deben ser números.")
        sys.exit(1)
    resultado = safe_divide(num, den)
    if resultado is None:
        print("Error: división por cero.")
    else:
        print(f"Resultado: {resultado}")