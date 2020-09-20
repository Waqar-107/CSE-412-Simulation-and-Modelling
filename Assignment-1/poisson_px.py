# from dust i have come, dust i will be

import numpy as np
import bisect
import matplotlib.pyplot as plt

lamb = 1
N = 1000
M = 10

# -------------------------------------
# find the theoretical values
X = []
Px = []

numerator = 1
denominator = 1

for i in range(M):
    numerator *= lamb
    denominator *= i
    if i == 0:
        denominator = 1  # 0!

    tmp = np.round(np.exp(-lamb) * (numerator / denominator), 3)

    Px.append(tmp)
    X.append(i)

# plt.figure(1)
# plt.plot(X, Px)
# -------------------------------------

# -------------------------------------
# experimental value
np.random.seed(107)

hash_map = {}
for i in range(N + 1):
    random_num = np.random.rand()
    idx = bisect.bisect_right(Px, random_num, lo=0, hi=len(Px))

    if idx in hash_map:
        hash_map[idx] += 1
    else:
        hash_map[idx] = 1

cumulative_sum = [0] * M
for i in range(M):
    if i in hash_map:
        cumulative_sum[i] = hash_map[i] / 1000

plt.plot(X, cumulative_sum)
# plt.legend(["X vs P(x)", "X vs cumulative sum"])

plt.xlabel('x')
plt.ylabel('Px')
plt.show()
# -------------------------------------
