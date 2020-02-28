# from dust i have come, dust i will be

import simpy


def clock(e, name, tick):
    while True:
        print(name, e.now)
        yield e.timeout(tick)


env = simpy.Environment()

env.process(clock(env, 'fast', 0.5))
env.process(clock(env, 'slow', 1))

env.run(until=2)

