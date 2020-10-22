# from dust i have come, dust i will be

import heapq
import numpy as np

# -----------------------------------------------
# constants
group_sizes = [1, 2, 3, 4]
group_size_probabilities = [0.5, 0.3, 0.1, 0.1]
counter_probabilities = [0.80, 0.15, 0.05]
inter_arrival_mean = 30  # seconds
simulation_duration = 90 * 60 * 60  # 90 minutes
counter_mapping = ["hot_food", "sandwich", "drinks"]
counter_routing = {
    "hot_food": ["hot_food", "drinks", "cash"],
    "sandwich": ["sandwich", "drinks", "cash"],
    "drinks": ["drinks", "cash"]
}

# -----------------------------------------------
# variables
counter_st = {"hot_food": (50, 120), "sandwich": (60, 180), "drinks": (5, 20)}
counter_act = {"hot_food": (20, 40), "sandwich": (5, 15), "drinks": (5, 10)}
q_quantity = {}


def expon(mean):
    return np.random.exponential(mean)


def random_integer(opts, probability_dist):
    return np.random.choice(opts, p=probability_dist)


# States and statistical counters
class States:
    def __init__(self):
        # queues
        self.queue = {"hot_food": [[]], "sandwich": [[]], "cash": [[] for _ in range(q_quantity["cash"])]}

        # servers available
        self.servers_available = {"hot_food": q_quantity["hot_food"], "sandwich": q_quantity["sandwich"],
                                  "cash": q_quantity["cash"]}

        # avg and max delays
        self.avg_q_delay = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}
        self.max_q_delay = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # avg and max delays for each type of customers
        self.avg_delay_customer = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}
        self.max_delay_customer = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # which counter served how much
        self.served = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # avg and max length of q
        # avg_q_length = sum of q area / simulation duration
        self.avg_q_length = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}
        self.max_q_length = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # avg and max number of customers in the system
        self.max_customer = 0
        self.current_customers = 0

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
        # first arrival
        grp_size_type = random_integer(group_sizes, group_size_probabilities)
        arrival_time = self.sim.now() + expon(inter_arrival_mean)
        for i in range(grp_size_type):
            grp_type = random_integer([0, 1, 2], counter_probabilities)
            self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim, counter_mapping[grp_type], 0))

        # exit event
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
    def __init__(self, event_time, sim, grp_type, current_counter):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.grp_type = grp_type
        self.current_counter = current_counter

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
    seed = 107
    np.random.seed(seed)

    sim = Simulator()
    sim.run()


def set_specs(idx):
    global q_quantity, counter_st, counter_act

    quantities = [[1, 1, 2], [1, 1, 3], [2, 1, 2], [1, 2, 2], [2, 2, 2], [2, 1, 3], [1, 2, 3], [2, 2, 3]]
    q_quantity = {"hot_food": quantities[idx][0], "sandwich": quantities[idx][1], "cash": quantities[idx][2]}

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

"""
in the events, keep some extra attribute,
1. current_counter - an index for counter routing where it is assumed that the routing is saved in an array
2. group_type - hot_food / sandwich / drinks

start-event
-------------
1. schedule the first arrival
   a. first generate group size
   b. then for each of the student, find their food type and create arrival event for them
2. schedule the exit

exit-event
-------------
1. keep this as it is

arrival-event
-------------
1. if this is an arrival at hot-food or sandwich section then create new arrivals here
2. now lets start processing this one
3. if the corresponding food section has idle employee start serving immediately. 
   otherwise select the smallest queue and insert the event there. 

departure-event
----------------
1. check if the corresponding queue has any customer in it, if there's someone then start serving that customer and
   schedule a departure-event for the customer
2. if the current departure-event is not in the cash counter then schedule an arrival-event in the next counter
"""
