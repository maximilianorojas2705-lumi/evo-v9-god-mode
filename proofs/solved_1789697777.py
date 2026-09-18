def solve(n):
    return sum(int(d) for d in str(abs(n)))

if __name__ == '__main__':
    print(solve(0))
