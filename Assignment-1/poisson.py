# from dust i have come, dust i will be

import numpy as np
import bisect
import matplotlib.pyplot as plt

lamb = 1
N = 1000
M = 1

# -------------------------------------
# find the theoretical values
Fx = []
X = []

numerator = 1
denominator = 1
Fx.append(numerator / denominator)
X.append(0)

# from 1 to 20
x = 1
while True:
    numerator *= lamb
    denominator *= x

    tmp = Fx[x - 1] + (numerator / denominator)

    if tmp == Fx[x - 1]:
        break

    Fx.append(tmp)
    X.append(x)

    x += 1
    M += 1

for i in range(M):
    Fx[i] *= np.exp(-lamb)

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
