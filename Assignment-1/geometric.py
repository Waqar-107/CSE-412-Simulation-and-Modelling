import numpy as np
import bisect
import matplotlib.pyplot as plt

p = 0.5
N = 1000
M = 1

# -------------------------------------
# theoretical value
Fx = []
X = []

Fx.append(1 - p)
X.append(0)

x = 1
while True:
    tmp = (1 - p) * Fx[x - 1]
    Fx.append(tmp)
    X.append(x)

    if 1 - tmp == 1.0:
        break

    x += 1

M = len(Fx)
for i in range(M):
    Fx[i] = 1 - Fx[i]

plt.figure(1)
plt.plot(X, Fx)
# -------------------------------------

# -------------------------------------
# experimental value
hash_map = {}
for i in range(N + 1):
    random_num = np.random.rand()
    idx = bisect.bisect_right(Fx, random_num, lo=0, hi=len(Fx))

    if idx in hash_map:
        hash_map[idx] += 1
    else:
        hash_map[idx] = 1

cumulative_sum = [0] * M
if 0 in hash_map:
    cumulative_sum[0] = hash_map[0]

for i in range(1, M, 1):
    cumulative_sum[i] = cumulative_sum[i - 1]
    if i in hash_map:
        cumulative_sum[i] += hash_map[i]

for i in range(M):
    cumulative_sum[i] /= 1000

plt.plot(X, cumulative_sum)
plt.legend(["X vs F(x)", "X vs cumulative sum"])
plt.xlabel('x')
plt.ylabel('Fx')
plt.show()
# -------------------------------------
