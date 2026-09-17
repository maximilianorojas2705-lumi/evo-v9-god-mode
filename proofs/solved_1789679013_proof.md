# PROBLEMA
sumar los dígitos de un número

# MODELOS COMPETIDORES
deepseek-r1-distill-llama-70b, meta-llama/llama-4-scout-17b-16e-instruct, openai/gpt-oss-120b, qwen/qwen3-32b

# GANADOR
deepseek-r1-distill-llama-70b

# SOLUCIÓN
def solve():
    n = int(input())
    return sum(int(d) for d in str(abs(n)))

# TESTS DEL VERIFICADOR
assert solve(0) == 0
assert solve(5) == 5
assert solve(12345) == 15
assert solve(1000000000) == 1

# RESULTADO
Traceback (most recent call last):
  File "<string>", line 5, in <module>
TypeError: solve() takes 0 positional arguments but 1 was given

