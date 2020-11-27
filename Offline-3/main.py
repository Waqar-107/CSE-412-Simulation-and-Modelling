# from dust i have come, dust i will be

from scipy import stats

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
            chi_squared += pow(cnt[i] - n / k, 2)

        chi_squared *= (k / n)

        # check if rejected or not
        if chi_squared > stats.chi2.ppf(q=1 - _alpha, df=k - 1):
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
