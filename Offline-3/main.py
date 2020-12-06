# from dust i have come, dust i will be

from scipy import stats
from collections import defaultdict
import math

multiplication_const = 65539
mod = pow(2, 31)
alpha = 0.1


class Solution:
    def __init__(self, seed, number_of_rands):
        self.seed = seed
        self.number_of_rands = number_of_rands
        self.random_numbers = []

    def generate_randoms(self):
        self.random_numbers = [self.seed]

        for i in range(1, self.number_of_rands):
            z = (multiplication_const * self.random_numbers[i - 1]) % mod
            self.random_numbers.append(z)

        for i in range(self.number_of_rands):
            self.random_numbers[i] /= mod

        assert (self.number_of_rands == len(self.random_numbers))

    def uniformity_test(self, k, _alpha):
        self.generate_randoms()
        interval = 1.0 / k

        cnt = [0] * k
        for r in self.random_numbers:
            lo = 0
            hi = k - 1

            while lo <= hi:
                mid = (lo + hi) // 2

                st = interval * mid
                en = st + interval

                if st <= r <= en:
                    cnt[mid] += 1
                    break
                elif r < st:
                    hi = mid - 1
                else:
                    lo = mid + 1

        # chi square test
        chi_squared = 0.0
        for i in range(k):
            chi_squared += pow(cnt[i] - self.number_of_rands / k, 2)

        chi_squared *= (k / self.number_of_rands)

        # check if rejected or not
        if chi_squared > stats.chi2.ppf(q=1 - _alpha, df=k - 1):
            print("rejected")
        else:
            print("not rejected")

    def serial_test_util(self, curr_d, max_d, k, string, cnt, constant):
        if curr_d == max_d:
            return pow(cnt[string] - constant, 2)

        summation = 0
        for i in range(1, k + 1):
            summation += self.serial_test_util(curr_d + 1, max_d, k, string + "_" + str(i), cnt, constant)

        return summation

    def serial_test(self, d, k, _alpha):
        self.generate_randoms()

        cnt = defaultdict(int)
        length = (self.number_of_rands // d) * d
        interval = 1.0 / k

        d_arr = []
        for i in range(length):
            d_arr.append(self.random_numbers[i])
            if len(d_arr) == d:
                # determine each of the elements interval and concatenate in a string
                pattern = []
                for num in d_arr:
                    lo = 0
                    hi = k - 1

                    while lo <= hi:
                        mid = (lo + hi) // 2

                        st = interval * mid
                        en = st + interval

                        # interval found
                        if st <= num <= en:
                            pattern.append(str(mid + 1))
                            break
                        elif num < st:
                            hi = mid - 1
                        else:
                            lo = mid + 1

                cnt["_".join(pattern)] += 1
                d_arr = []

        chi_squared = 0
        for i in range(1, k + 1):
            chi_squared += self.serial_test_util(1, d, k, str(i), cnt, self.number_of_rands / pow(k, d))

        chi_squared *= (pow(k, d) / self.number_of_rands)

        # check if rejected or not
        if chi_squared > stats.chi2.ppf(q=1 - _alpha, df=pow(k, d) - 1):
            print("rejected")
        else:
            print("not rejected")

    def runs_test(self, _alpha):
        self.generate_randoms()

        a = [[4529.4, 9044.9, 13568, 18091, 22615, 27892],
             [9044.9, 18097, 27139, 36187, 45234, 55789],
             [13568, 27139, 40721, 54281, 67852, 83685],
             [18091, 36187, 54281, 72414, 90470, 111580],
             [22615, 45234, 67852, 90470, 113262, 139476],
             [27892, 55789, 83685, 111580, 139476, 172860]
             ]
        b = [1 / 6, 5 / 24, 11 / 120, 19 / 720, 29 / 5040, 1 / 840]

        increasing_seq = defaultdict(int)
        cnt = 1

        # corner case for determining increasing run-up length. though this will never be executed
        if self.number_of_rands == 1:
            increasing_seq[1] = 1

        for i in range(1, self.number_of_rands):
            if self.random_numbers[i] > self.random_numbers[i - 1]:
                cnt += 1
            else:
                cnt = min(cnt, 6)
                increasing_seq[cnt] += 1
                cnt = 1

            if i == self.number_of_rands - 1:
                cnt = min(cnt, 6)
                increasing_seq[cnt] += 1

        R = 0
        for i in range(6):
            for j in range(6):
                R += a[i][j] * (increasing_seq[i + 1] - self.number_of_rands * b[i]) * (
                        increasing_seq[j + 1] - self.number_of_rands * b[j])

        R /= self.number_of_rands
        if R > stats.chi2.ppf(q=1 - _alpha, df=6):
            print("rejected")
        else:
            print("not rejected")

    def correlation_test(self, j, _alpha):
        self.generate_randoms()

        h = int((self.number_of_rands - 1) / j - 1)
        rho = 0

        for k in range(h + 1):
            rho += self.random_numbers[k * j] * self.random_numbers[(k + 1) * j]

        rho = (12 * rho) / (h + 1)
        rho -= 3

        variance_rho = (13 * h + 7) / pow(h + 1, 2)
        Aj = rho / math.sqrt(variance_rho)

        if abs(Aj) > stats.norm.ppf(q=1 - _alpha / 2):
            print("rejected")
        else:
            print("not rejected")


if __name__ == "__main__":
    nums = [20, 500, 4000, 10000]

    for n in nums:
        solve = Solution(1505107, n)
        print("n =", n)

        # uniformity test
        print("-------------------------------------------")
        print("uniformity test")

        print("k = 10", end=". ")
        solve.uniformity_test(k=10, _alpha=alpha)

        print("k = 20", end=". ")
        solve.uniformity_test(k=20, _alpha=alpha)

        print()

        # serial test
        print("-------------------------------------------")
        print("serial test")

        print("d = 2, k = 4")
        solve.serial_test(d=2, k=4, _alpha=alpha)

        print("d = 3, k = 4")
        solve.serial_test(d=3, k=4, _alpha=alpha)

        print("d = 2, k = 8")
        solve.serial_test(d=2, k=8, _alpha=alpha)

        print("d = 3, k = 8")
        solve.serial_test(d=3, k=8, _alpha=alpha)

        print()

        # runs test
        print("-------------------------------------------")
        print("runs test")
        solve.runs_test(_alpha=alpha)
        print()

        # correlation test
        print("-------------------------------------------")
        print("correlation test")

        print("j = 1")
        solve.correlation_test(j=1, _alpha=alpha)

        print("j = 3")
        solve.correlation_test(j=3, _alpha=alpha)

        print("j = 5")
        solve.correlation_test(j=5, _alpha=alpha)

        print()
