# from dust i have come, dust i will be

import heapq
import random
import math
from lcgrand import *
import matplotlib.pyplot as plt


def exponential(mean):
    return -(1 / mean) * math.log(lcgrand(1))


lazy = -1
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

        self.time_last_event = 0
        self.server_status = []

    def update(self, sim, event):
        time_since_last_event = sim.now() - self.time_last_event
        self.time_last_event = sim.now()

        self.people_in_q = 0
        for i in range(sim.params.k):
            self.people_in_q += len(self.queue[i])

        self.area_number_in_q += (self.people_in_q / sim.params.k) * time_since_last_event

        cnt = 0
        for i in range(sim.params.k):
            if self.server_status[i] != lazy:
                cnt += 1

        self.total_time_served += time_since_last_event * (cnt / sim.params.k)

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

        # process this arrival event
        # find a lazy server
        for i in range(sim.params.k):
            if sim.states.server_status[i] == lazy:
                delay = 0
                sim.states.total_delay += delay

                # schedule a departure
                depart_time = sim.now() + exponential(sim.params.mu)
                sim.schedule_event(DepartureEvent(depart_time, sim))

                # make the server busy. here we assign the departure time so that we
                # can track which server got free and from which queue we will serve
                sim.states.server_status[i] = depart_time
                sim.states.served += 1

                return

        # no lazy server found :(
        # now find the shortest queue, if there are more than one then select the leftmost one
        idx = 0
        mn = len(sim.states.queue[0])

        for i in range(1, sim.params.k, 1):
            if len(sim.states.queue[i]) < mn:
                mn = len(sim.states.queue[i])
                idx = i

        sim.states.queue[idx].append(self.event_time)


class DepartureEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):

        # find the server that was giving service
        server_no = -1
        for i in range(sim.params.k):
            if self.event_time == sim.states.server_status[i]:
                sim.states.server_status[i] = lazy
                server_no = i

                # check if there is someone in the q
                if len(sim.states.queue[i]):
                    t = sim.states.queue[i].pop(0)
                    sim.states.total_delay += sim.now() - t

                    # schedule a departure
                    depart_time = sim.now() + exponential(sim.params.mu)
                    sim.schedule_event(DepartureEvent(depart_time, sim))

                    # make the server busy. here we assign the departure time so that we
                    # can track which server got free and from which queue we will serve
                    sim.states.server_status[i] = depart_time
                    sim.states.served += 1
                else:
                    # check if i-1 or i+1 has anyone in the q
                    if i - 1 >= 0 and len(sim.states.queue[i - 1]):
                        t = sim.states.queue[i - 1].pop()
                        sim.states.total_delay += sim.now() - t

                        # schedule a departure
                        depart_time = sim.now() + exponential(sim.params.mu)
                        sim.schedule_event(DepartureEvent(depart_time, sim))

                        # make the server busy. here we assign the departure time so that we
                        # can track which server got free and from which queue we will serve
                        sim.states.server_status[i] = depart_time
                        sim.states.served += 1
                    elif i + 1 > sim.params.k and len(sim.states.queue[i + 1]):
                        t = sim.states.queue[i + 1].pop()
                        sim.states.total_delay += sim.now() - t

                        # schedule a departure
                        depart_time = sim.now() + exponential(sim.params.mu)
                        sim.schedule_event(DepartureEvent(depart_time, sim))

                        # make the server busy. here we assign the departure time so that we
                        # can track which server got free and from which queue we will serve
                        sim.states.server_status[i] = depart_time
                        sim.states.served += 1

                break

        if server_no != -1:
            if server_no - 1 >= 0 and len(sim.states.queue[server_no - 1]):
                while len(sim.states.queue[server_no - 1]) - len(sim.states.queue[server_no]) >= 2:
                    x = sim.states.queue[server_no - 1].pop()
                    sim.states.queue[server_no].append(x)

            if server_no + 1 < sim.params.k and len(sim.states.queue[server_no + 1]):
                while len(sim.states.queue[server_no + 1]) - len(sim.states.queue[server_no]) >= 2:
                    x = sim.states.queue[server_no + 1].pop()
                    sim.states.queue[server_no].append(x)


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

        self.states.server_available = self.params.k
        self.states.server_quantity = self.params.k
        self.states.server_status = [lazy] * self.params.k
        self.states.queue = [[]] * self.params.k

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


def experiment4():
    seed = 101
    lambd = 5.0 / 60
    mu = 8.0 / 60
    server_quantity = 4

    avg_length = []
    avg_delay = []
    util = []

    servers = [i for i in range(1, server_quantity + 1, 1)]

    for i in range(1, server_quantity + 1, 1):
        # reset lcgrand
        reset()

        sim = Simulator(seed)
        sim.configure(Params(lambd, mu, i), States())

        sim.run()
        sim.print_results()

        length, delay, utl = sim.get_results()
        avg_length.append(length)
        avg_delay.append(delay)
        util.append(utl)

    # plot
    plt.figure(1)
    plt.subplot(311)
    plt.plot(servers, avg_length)
    plt.xlabel('Server (k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(servers, avg_delay)
    plt.xlabel('Server (k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(servers, util)
    plt.xlabel('Server (k)')
    plt.ylabel('Util')

    plt.show()


def main():
    experiment4()


if __name__ == "__main__":
    main()

'''
arrival: 
1. find a free server, if found get in
2. if all the servers are busy then find the leftmost shortest queue and get in it

depart:
1. if the corresponding queue is empty then free the server
2. take the first person standing in the queue and then - 
for all the queue, if (LF - L) or (LR - L) >= 2  
'''
