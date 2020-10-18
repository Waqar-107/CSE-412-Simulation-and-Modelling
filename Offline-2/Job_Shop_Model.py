# from dust i have come, dust i will be

import heapq
import random
import math
from lcgrand import *
from collections import defaultdict

# -------------------------------------
# variables
number_of_stations = None
number_of_machines = []
inter_arrival_rate = None
job_types = None
job_probabilities = []
stations_in_each_task = []
station_routing = defaultdict(list)
mean_service_time = defaultdict(list)


def exponential(rate):
    # return random.expovariate(rate)
    return -(1 / rate) * math.log(lcgrand(1))


simulation_duration = 10000


# States and statistical counters
class States:
    def __init__(self):
        None

    def update(self, sim, event):
        None

    # called when there's no event left
    # do the calculations here
    def finish(self, sim):
        None


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.event_time = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        None


class ExitEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        print("simulation is going to end now. current time:", self.event_time)


class ArrivalEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'ARRIVAL'
        self.sim = sim

    def process(self, sim):
        None


class DepartureEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):
        None


class Simulator:
    def __init__(self, seed):
        # eventQ is a min heap, we are pushing events in it, when retrieved, it will give the next earliest event
        self.eventQ = []
        self.simulator_clock = 0
        self.seed = seed
        self.states = None

    def initialize(self):
        self.simulator_clock = 0
        self.schedule_event(StartEvent(0, self))

    # adds the parameters like mu and lambda, a states object is initiated
    def configure(self, states):
        self.states = states  # state()

    # returns the current time
    def now(self):
        return self.simulator_clock

    def schedule_event(self, event):
        heapq.heappush(self.eventQ, (event.event_time, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)

            if event.eventType == 'EXIT':
                break

            if self.states is not None:
                self.states.update(self, event)

            self.simulator_clock = event.event_time
            event.process(self)

        self.states.finish(self)
        print()


def read_input():
    global number_of_stations, number_of_machines, inter_arrival_rate, job_types, job_probabilities, \
        stations_in_each_task, station_routing, mean_service_time

    f = open("job_shop.txt", "r")
    lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].endswith("\n"):
            lines[i] = lines[i][: -1]

    number_of_stations = int(lines[0])
    number_of_machines = list(map(int, lines[1].split()))
    inter_arrival_rate = float(lines[2])
    job_types = int(lines[3])
    job_probabilities = list(map(float, lines[4].split()))
    stations_in_each_task = list(map(int, lines[5].split()))

    idx = 6
    for i in range(job_types):
        station_routing["job" + str(i + 1)] = list(map(int, lines[idx].split()))
        mean_service_time["job" + str(i + 1)] = list(map(float, lines[idx + 1].split()))

        idx += 2


def experiment1():
    # seed = 101
    # sim = Simulator(seed)
    # sim.run()
    read_input()


def main():
    experiment1()


if __name__ == "__main__":
    main()
