"""
Method:
--------
1. for values of x, generate pdf and cdf and store them in Px[] and Fx[]
2. keep generating values until the value of cdf changes. they will stop changing at one moment
3. keep the values of x in X[]
4. for N trials (N=1000, here),
    4.1. generate a random number
    4.2. find its upper_bound in cdf(Fx[])
    4.3. find the corresponding x for the upper_bound value
    4.4. update the frequency of x (frequency[x]++)
5. divide each frequency by N
6. plot X[] vs Px[]
7. plot X[] vs frequency[]
"""

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
Px = []

numerator = 1
denominator = 1

Px.append(np.round(np.exp(-lamb), 5))
Fx.append(numerator / denominator)
X.append(0)

# calculate pdf and cdf
x = 1
while True:
    numerator *= lamb
    denominator *= x

    tmp = Fx[x - 1] + (numerator / denominator)

    if tmp == Fx[x - 1]:
        break

    Fx.append(tmp)
    Px.append(np.round(Px[x - 1] * (1 / x), 5))
    X.append(x)

    x += 1
    M += 1

for i in range(M):
    Fx[i] = np.round(np.exp(-lamb) * Fx[i], 5)

# plot pdf
plt.figure(1)
plt.plot(X, Px)
# -------------------------------------

# -------------------------------------
# experimental value
frequency = [0] * M
for i in range(N + 1):
    random_num = np.random.rand()

    # find the upper_bound of random_num
    idx = bisect.bisect_right(Fx, random_num, lo=0, hi=len(Fx))
    frequency[idx] += 1

for i in range(M):
    frequency[i] /= 1000

# plot X vs frequency/N
plt.plot(X, frequency)
plt.legend(["X vs P(x)", "X vs Frequency/N"])

plt.xlabel('X')
plt.ylabel('Frequency/N')
plt.show()
# -------------------------------------
