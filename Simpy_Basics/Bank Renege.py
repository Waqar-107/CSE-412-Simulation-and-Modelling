# from dust i have come, dust i will be

import simpy
import random

'''
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege
'''

RANDOM_SEED = 42
NEW_CUSTOMERS = 5               # total no. of customers
INTERVAL_CUSTOMERS = 10.0       # generate new customers roughly every x seconds
MIN_PATIENCE = 1                # min patience of a customer
MAX_PATIENCE = 3                # max patience of a customer


def source(e, n, interval, cnt):
    # this generates customers randomly
    for i in range(n):
        c = customer(e, 'customer' + str(i), cnt, time_in_bank=12)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def customer(e, name, cnt, time_in_bank):
    global MIN_PATIENCE, MAX_PATIENCE

    # customer arrives, is served and then leaves
    arrive = round(e.now, 3)
    print("current time :", arrive, "|", name, "is here")

    with cnt.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)

        # wait for the counter or abort at the end of our tether
        results = yield req | e.timeout(patience)
        wait = round(e.now - arrive, 3)

        if req in results:
            # we got the counter
            print("current time :", round(e.now, 3), "|", name, "waited for", wait)

            tib = random.expovariate(1.0 / time_in_bank)
            yield e.timeout(tib)
            print("current time :", round(e.now, 3), "| done with", name)

        else:
            # we reneged
            print("current-time :", round(e.now, 3), "|", name, "reneged after waiting for", wait)


# setup
print('Bank Renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# start processes and run
counter = simpy.Resource(env, capacity=1)
env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counter))
env.run()
