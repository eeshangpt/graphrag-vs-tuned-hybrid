import math

def phi(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def power(n, sd, margin):
    se = sd / math.sqrt(n)
    return max(0, 2 * phi(margin / se - 1.64485) - 1)

print("n=500")
print(f"sd=0.45, m=2: {power(500, 0.45, 0.02):.2f}")
print(f"sd=0.45, m=3: {power(500, 0.45, 0.03):.2f}")
print(f"sd=0.45, m=4: {power(500, 0.45, 0.04):.2f}")
print(f"sd=0.45, m=5: {power(500, 0.45, 0.05):.2f}")
print(f"sd=0.35, m=2: {power(500, 0.35, 0.02):.2f}")
print(f"sd=0.35, m=3: {power(500, 0.35, 0.03):.2f}")
print(f"sd=0.35, m=4: {power(500, 0.35, 0.04):.2f}")
print(f"sd=0.35, m=5: {power(500, 0.35, 0.05):.2f}")
print("n=1000")
print(f"sd=0.45, m=2: {power(1000, 0.45, 0.02):.2f}")
print(f"sd=0.45, m=3: {power(1000, 0.45, 0.03):.2f}")
print(f"sd=0.45, m=4: {power(1000, 0.45, 0.04):.2f}")
print(f"sd=0.45, m=5: {power(1000, 0.45, 0.05):.2f}")
print(f"sd=0.35, m=2: {power(1000, 0.35, 0.02):.2f}")
print(f"sd=0.35, m=3: {power(1000, 0.35, 0.03):.2f}")
print(f"sd=0.35, m=4: {power(1000, 0.35, 0.04):.2f}")
print(f"sd=0.35, m=5: {power(1000, 0.35, 0.05):.2f}")
