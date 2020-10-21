# from dust i have come, dust i will be

import heapq
import numpy as np
from collections import defaultdict

# -----------------------------------------------
# constants
group_sizes = [1, 2, 3, 4]
group_size_probabilities = [0.5, 0.3, 0.1, 0.1]
counter_probabilities = [0.80, 0.15, 0.05]
inter_arrival_mean = 30  # seconds
simulation_duration = 90 * 60 * 60  # 90 minutes

# -----------------------------------------------
# variables
counter_st = {"hot_food": (50, 120), "sandwich": (60, 180), "drinks": (5, 20)}
counter_act = {"hot_food": (20, 40), "sandwich": (5, 15), "drinks": (5, 10)}
q_quantity = {}


# States and statistical counters
class States:
    def __init__(self):
        None

    def update(self, event):
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
    def __init__(self):
        self.eventQ = []
        self.simulator_clock = 0
        self.states = States()

    def initialize(self):
        self.simulator_clock = 0
        self.schedule_event(StartEvent(0, self))

    def now(self):
        return self.simulator_clock

    def schedule_event(self, event):
        heapq.heappush(self.eventQ, (event.event_time, event))

    def run(self):
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)
            if event.eventType == 'EXIT':
                break

            if self.states is not None:
                self.states.update(event)

            self.simulator_clock = event.event_time
            event.process(self)

        return self.states.finish(self)


def cafeteria_model():
    None


def set_specs(idx):
    global q_quantity, counter_st, counter_act

    quantities = [[1, 1, 2], [1, 1, 3], [2, 1, 2], [1, 2, 2], [2, 2, 2], [2, 1, 3], [1, 2, 3], [2, 2, 3]]
    q_quantity = {"hot_food": quantities[idx][0], "sandwich": quantities[idx][1], "drinks": quantities[idx][2]}

    # scale down
    counter_st["hot_food"] = (
        counter_st["hot_food"][0] / quantities[idx][0], counter_st["hot_food"][1] / quantities[idx][0])
    counter_st["sandwich"] = (
        counter_st["sandwich"][0] / quantities[idx][1], counter_st["sandwich"][1] / quantities[idx][1])

    counter_act["hot_food"] = (
        counter_act["hot_food"][0] / quantities[idx][0], counter_act["hot_food"][1] / quantities[idx][0])
    counter_act["sandwich"] = (
        counter_act["sandwich"][0] / quantities[idx][1], counter_act["sandwich"][1] / quantities[idx][1])


if __name__ == "__main__":
    set_specs(0)
    cafeteria_model()
