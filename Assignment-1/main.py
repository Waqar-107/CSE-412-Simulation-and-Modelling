# from dust i have come, dust i will be

import numpy as np
import bisect
import matplotlib.pyplot as plt

lamb = 1

# -------------------------------------
# find the theoretical values
Fx = []
X = list(range(21))

numerator = 1
denominator = 1
Fx.append(numerator / denominator)

# from 1 to 20
for x in range(1, 21, 1):
    numerator *= lamb
    denominator *= x

    tmp = Fx[x - 1] + (numerator / denominator)
    Fx.append(tmp)

for i in range(21):
    Fx[i] *= np.exp(-lamb)

plt.figure(1)
plt.plot(X, Fx)
# -------------------------------------

# -------------------------------------
# experimental value
hash_map = {}
for i in range(1001):
    random_num = np.random.rand()
    idx = bisect.bisect_right(Fx, random_num, lo=0, hi=len(Fx))

    if idx in hash_map:
        hash_map[idx] += 1
    else:
        hash_map[idx] = 1

cumulative_sum = [0] * 21
if 0 in hash_map:
    cumulative_sum[0] = hash_map[0]

for i in range(1, 21, 1):
    cumulative_sum[i] = cumulative_sum[i - 1]
    if i in hash_map:
        cumulative_sum[i] += hash_map[i]

for i in range(21):
    cumulative_sum[i] /= 1000

plt.plot(X, cumulative_sum)
plt.legend(["X vs F(x)", "X vs cumulative sum"])

plt.xlabel('x')
plt.ylabel('Fx')
plt.show()
# -------------------------------------
