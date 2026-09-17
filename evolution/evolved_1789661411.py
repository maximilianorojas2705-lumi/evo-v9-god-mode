# utils_math.py
def sum_to_n(n: int) -> int:
    """Return the sum of all integers from 1 to n inclusive."""
    if n < 0:
        raise ValueError("n must be non‑negative")
    return n * (n + 1) // 2

def factorial(n: int) -> int:
    """Return the factorial of n using recursion."""
    if n < 0:
        raise ValueError("n must be non‑negative")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


# test_utils_math.py
def test_sum_to_n():
    assert sum_to_n(100) == 5050

def test_factorial():
    assert factorial(5) == 120

# Ensure the module can be run directly for quick sanity check
if __name__ == "__main__":
    test_sum_to_n()
    test_factorial()
    print("All tests passed.")