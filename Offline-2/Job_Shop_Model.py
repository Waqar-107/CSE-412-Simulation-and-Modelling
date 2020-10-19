# from dust i have come, dust i will be

import heapq
import random
import math
from lcgrand import *
from collections import defaultdict

# -------------------------------------
# variables
number_of_stations = 0
number_of_machines = []
inter_arrival_rate = 0.0
job_types = 0
job_probabilities = []
stations_in_each_task = []
station_routing = defaultdict(list)
mean_service_time = defaultdict(list)

# -------------------------------------
# constants
simulation_duration = 10000
simulation_hours = 8
STREAM_INTER_ARRIVAL = 1  # Random-number stream for inter arrivals
STREAM_JOB_TYPE = 2  # Random-number stream for job types
STREAM_SERVICE = 3  # Random-number stream for service times


def expon(mean, stream):
    return -mean * math.log(lcgrand(stream))


def erlang(m, mean, stream):
    mean_exponential = mean / m
    summation = 0

    i = 1
    while i <= m:
        summation += expon(mean_exponential, stream)
        i += 1

    return summation


def random_integer(probability_distribution, stream):
    u = lcgrand(stream)

    i = 0
    for i in range(len(probability_distribution)):
        if u < probability_distribution[i]:
            return i + 1

    return len(probability_distribution)


# States and statistical counters
class States:
    def __init__(self):
        self.queue = [[] for _ in range(number_of_stations + 1)]
        self.servers_busy = [0] * (number_of_stations + 1)

        # avg delay in each station
        self.served = [0] * (number_of_stations + 1)
        self.avg_q_delay = [0] * (number_of_stations + 1)

        # delay for each job type and overall job delay
        # for each type of job save the delays in the event object. keep adding at each station
        # when the job finishes all the task, increase the cnt and add the total delay in the array
        self.job_delay = [0] * (job_types + 1)
        self.job_cnt = [0] * (job_types + 1)

        # to determine avg q length
        self.area_number_in_q = [0] * (number_of_stations + 1)

        # avg number of jobs in the system
        # area = time_since_last_event * (sum of q lengths + sum of servers busy)
        # finally area / sim.now()
        self.area_number_job = 0

    def update(self, sim, event):
        None

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
        # schedule the first arrival
        arrival_time = self.event_time + expon(inter_arrival_rate, STREAM_INTER_ARRIVAL)
        job_type = random_integer(job_probabilities, STREAM_JOB_TYPE)
        self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim, job_type))

        # schedule the exit
        self.sim.schedule_event(ExitEvent(simulation_hours * simulation_duration, self.sim))


class ExitEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        print("simulation is going to end now. current time:", self.event_time)


class ArrivalEvent(Event):
    def __init__(self, event_time, sim, job_type):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.job_type = job_type
        self.current_station = 1
        self.delay = 0.0

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
        self.eventQ = []
        self.simulator_clock = 0
        self.seed = seed
        self.states = States()

    def initialize(self):
        self.simulator_clock = 0
        self.schedule_event(StartEvent(0, self))

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


def job_shop_model():
    read_input()

    seed = 101
    sim = Simulator(seed)
    sim.run()


if __name__ == "__main__":
    job_shop_model()

"""
start-event
-------------
1. schedule the first arrival
2. schedule the exit

exit-event
-------------
1. keep this as it is

arrival-event
-------------
1. if the job has arrived in the first station then schedule the arrival of the next event
2. if all the machines of the station are busy then insert the event in the queue of that station
3. if an idle machine found in that station then schedule a departure for the event, delay will be 0

departure-event
----------------
1. if the job is in it's final station then done
2. otherwise schedule an arrival event for the next station.
3. if the queue of the station where the event was empty then make an machine in that station free. 
otherwise take the event that is in the top of the queue and schedule departure for it. also calculate the delay
 
"""
