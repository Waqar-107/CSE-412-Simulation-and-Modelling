# from dust i have come, dust i will be

import simpy
import random

'''
Carwash example.

Covers:

- Waiting for other processes
- Resources: Resource

Scenario:
  A carwash has a limited number of washing machines and defines
  a washing processes that takes some (random) time.

  Car processes arrive at the carwash at a random time. If one washing
  machine is available, they start the washing process and wait for it
  to finish. If not, they wait until they an use one.
'''

RANDOM_SEED = 42
MACHINE_QUANTITY = 2
WASH_TIME = 5
T_INTER = 7  # Create a car every ~7 minutes
SIMULATION_TIME = 20  # Simulation time in minutes


class CarWash(object):
    def __init__(self, env, num_machines, wash_time):
        self.env = env
        self.machine = simpy.Resource(env, capacity=num_machines)
        self.wash_time = wash_time

    # takes a car process and washes it
    def wash(self, car):
        yield self.env.timeout(self.wash_time)
        print("Carwash removed %d%% of %s's dirt." % (random.randint(50, 99), car))


def car(env, name, cw):
    print('%s arrives at the carwash at %.2f' % (name, env.now))
    with cw.machine.request() as req:
        yield req

        print('%s enters the carwash at %.2f' % (name, env.now))
        yield env.process(cw.wash(name))

        print('%s leaves the carwash at %.2f' % (name, env.now))


def setup(env, machine, wash_time, t_inter):
    '''
    create a carwash, a number of initial cars
    and keep creating cars approx. every `t_inter` minutes
    '''

    # create a carwash
    carwash = CarWash(env, machine, wash_time)

    # create 4 initial cars
    for i in range(4):
        env.process(car(env, 'Car %d' % i, carwash))

    # create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i += 1

        env.process(car(env, 'Car %d' % i, carwash))


print("Carwash")
random.seed(RANDOM_SEED)

e = simpy.Environment()
e.process(setup(e, MACHINE_QUANTITY, WASH_TIME, T_INTER))

e.run(until=SIMULATION_TIME)
