# from dust i have come, dust i will be

import heapq
import random
import math
from lcgrand import *


def exponential(rate):
    # return random.expovariate(rate)
    return -(1 / rate) * math.log(lcgrand(1))


busy = 1
idle = 0
simulation_duration = 10000


# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # inter arrival rate
        self.mu = mu  # service rate
        self.k = k
        # Note lambd and mu are not mean value, they are rates i.e. (1/mean)


# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queue = []

        # Statistics
        self.util = 0.0
        self.avg_Q_delay = 0.0
        self.avg_Q_length = 0.0
        self.served = 0

        # others
        self.total_delay = 0.0
        self.total_time_served = 0.0
        self.area_number_in_q = 0.0
        self.people_in_q = 0
        self.server_status = idle
        self.time_last_event = 0

    def update(self, sim, event):
        time_since_last_event = sim.now() - self.time_last_event
        self.time_last_event = sim.now()

        self.area_number_in_q += self.people_in_q * time_since_last_event
        self.total_time_served += self.server_status * time_since_last_event

    # called when there's no event left
    # do the calculations here
    def finish(self, sim):
        try:
            self.avg_Q_delay = self.total_delay / self.served
        except ZeroDivisionError:
            print("error while determining avg q delay, served 0")

        # sim.now() will have the EXIT time
        self.util = self.total_time_served / sim.now()

        # average q length
        self.avg_Q_length = self.area_number_in_q / sim.now()

    def print_results(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % self.served)
        print('MMk Average queue length: %lf' % self.avg_Q_length)
        print('MMk Average customer delay in queue: %lf' % self.avg_Q_delay)
        print('MMk Time-average server utility: %lf' % self.util)
        print("total time served", self.total_time_served)

    def get_results(self, sim):
        return self.avg_Q_length, self.avg_Q_delay, self.util


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
        # the server has started, next there will be an arrival, so we schedule the first arrival here
        arrival_time = self.event_time + exponential(self.sim.params.lambd)
        self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim))

        # set the exit event here
        self.sim.schedule_event(ExitEvent(simulation_duration, self.sim))


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
        # schedule next arrival
        next_arrival_time = sim.now() + exponential(sim.params.lambd)
        sim.schedule_event(ArrivalEvent(next_arrival_time, sim))

        if sim.states.server_status == busy:
            sim.states.people_in_q += 1
            sim.states.queue.append(sim.now())
        else:
            delay = 0
            sim.states.total_delay += delay

            sim.states.server_status = busy
            sim.states.served += 1

            # schedule a departure
            depart_time = sim.now() + exponential(sim.params.mu)
            sim.schedule_event(DepartureEvent(depart_time, sim))


class DepartureEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):
        if len(sim.states.queue) == 0:
            sim.states.server_status = idle

        else:
            sim.states.people_in_q -= 1

            delay = sim.now() - sim.states.queue[0]
            sim.states.total_delay += delay

            sim.states.served += 1
            depart_time = sim.now() + exponential(sim.params.mu)
            sim.schedule_event(DepartureEvent(depart_time, sim))

            sim.states.queue.pop(0)


class Simulator:
    def __init__(self, seed):
        # eventQ is a min heap, we are pushing events in it, when retrieved, it will give the next earliest event
        self.eventQ = []
        self.simulator_clock = 0
        self.seed = seed
        self.params = None
        self.states = None

    def initialize(self):
        self.simulator_clock = 0
        self.schedule_event(StartEvent(0, self))

    # adds the parameters like mu and lambda, a states object is initiated
    def configure(self, params, states):
        self.params = params
        self.states = states

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

            # print('Time:', round(event.event_time, 5), '| Event:', event)

            self.simulator_clock = event.event_time
            event.process(self)

        self.states.finish(self)
        print()

    def print_results(self):
        self.states.print_results(self)

    def get_results(self):
        return self.states.get_results(self)

    def print_analytical_results(self):
        # avg queue len = (lambda * lambda) / (mu * (mu - lambda))
        avg_q_len = (self.params.lambd * self.params.lambd) / (self.params.mu * (self.params.mu - self.params.lambd))

        # avg delay in queue = lambda / (mu * (mu - lambda))
        avg_delay_in_q = self.params.lambd / (self.params.mu * (self.params.mu - self.params.lambd))

        # server utilization factor = lambda / mu
        server_util_factor = self.params.lambd / self.params.mu

        print("\nAnalytical Results :")
        print("lambda = %lf, mu = %lf" % (self.params.lambd, self.params.mu))
        print("Average queue length", round(avg_q_len, 3))
        print("Average delay in queue", round(avg_delay_in_q, 3))
        print("Server utilization factor", round(server_util_factor, 3))


def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1), States())

    sim.run()
    sim.print_results()
    sim.print_analytical_results()


def main():
    experiment1()


if __name__ == "__main__":
    main()

'''
start-event will schedule the 1st arrival-event
arrival-events process will schedule a departure-event for itself

the events have process of their own
the states has update

an event is extracted from the heap
then states update is called using that event
then process of that event is called

what i need now: 
1. find a place to schedule arrival-departure
2. find a place to update the params
'''
