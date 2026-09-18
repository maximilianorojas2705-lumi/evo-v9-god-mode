# PROBLEMA
sumar los dígitos de un número

# MODELOS COMPETIDORES
deepseek-r1-distill-llama-70b, meta-llama/llama-4-scout-17b-16e-instruct, openai/gpt-oss-120b, qwen/qwen3-32b

# GANADOR
deepseek-r1-distill-llama-70b

# SOLUCIÓN
def solve(n):
    return sum(int(d) for d in str(abs(n)))

if __name__ == '__main__':
    print(solve(0))


# TESTS DEL VERIFICADOR
assert solve(0) == 0
assert solve(5) == 5
assert solve(999) == 27
assert solve(-12345) == 15

# RESULTADO
TESTS OK

