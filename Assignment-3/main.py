import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import variation, skew

# ---------------------------------
# read the data from a file
f = open("input.txt", "r")
lines = f.readlines()
f.close()

data = []
for line in lines:
    data.append(float(line.rstrip("\n")))

plt.hist(data, bins=10, rwidth=0.5)
plt.show()

data = np.array(data)
precision = 3
print("min", round(np.min(data), precision))
print("max", round(np.max(data), precision))
print("mean", round(np.mean(data), precision))
print("median", round(np.median(data), precision))
print("variance", round(np.var(data), precision))
print("coefficient of variation", round(variation(data), precision))
print("skewness", round(skew(data), precision))
