# from dust i have come, dust i will be

import heapq
import numpy as np
import time

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

# arrival controller
arrival_controller = {}
group_no = 0


def expon(mean):
    return np.random.exponential(mean)


def uniform_rand(lo, hi):
    return np.random.uniform(lo, hi)


def random_integer(opts, probability_dist):
    return np.random.choice(opts, p=probability_dist)


# States and statistical counters
class States:
    def __init__(self):
        # queues - though there is no q required for drinks, i have kept it to avoid a few if-else checks in departure
        self.queue = {"hot_food": [[]], "sandwich": [[]], "drinks": [[]],
                      "cash": [[] for _ in range(q_quantity["cash"])]}

        # servers available
        self.servers_available = {"hot_food": q_quantity["hot_food"], "sandwich": q_quantity["sandwich"],
                                  "drinks": np.inf, "cash": q_quantity["cash"]}

        # need to track which q should be popped
        # food counters will have a single q so it's easy to pop from their q
        self.cash_server = [0] * q_quantity["cash"]

        # avg and max delays
        self.avg_q_delay = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}
        self.max_q_delay = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # avg and max delays for each type of customers
        self.avg_delay_customer = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}
        self.max_delay_customer = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # which counter served how much
        self.served = {"hot_food": 0.0, "sandwich": 0.0, "drinks": 0.0, "cash": 0.0}
        self.customer_type_cnt = {"hot_food": 0.0, "sandwich": 0.0, "drinks": 0.0}

        # avg and max length of q
        # avg_q_length = sum of q area / simulation duration
        self.avg_q_length = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}
        self.max_q_length = {"hot_food": 0.0, "sandwich": 0.0, "cash": 0.0}

        # avg and max number of customers in the system
        self.max_customer = 0
        self.current_customers = 0

        self.time_last_event = 0

    def update(self, event):
        time_since_last_event = event.event_time - self.time_last_event
        self.time_last_event = event.event_time

        self.max_customer = max(self.max_customer, self.current_customers)

        # avg q lengths
        for key in self.avg_q_length:
            cnt = 0
            for i in range(len(self.queue[key])):
                cnt += len(self.queue[key][i])
                self.max_q_length[key] = max(self.max_q_length[key], len(self.queue[key][i]))

            self.avg_q_length[key] += (cnt / len(self.queue[key])) * time_since_last_event

    def finish(self, sim):
        for key in self.avg_q_length:
            self.avg_q_length[key] /= sim.now()


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.event_time = None

    def process(self):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType

    # when there are two or more events with same time, the heap will depend on the 2nd element of the tuple to compare
    # so we have to implement lt and le so that events can be compared in the heap
    # for <
    def __lt__(self, other):
        return True

    # for <=
    def __le__(self, other):
        return True


class StartEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'START'
        self.sim = sim

    def process(self):
        global group_no

        # first arrival
        grp_size_type = random_integer(group_sizes, group_size_probabilities)
        arrival_time = self.sim.now() + expon(inter_arrival_mean)
        group_no += 1

        for i in range(grp_size_type):
            grp_type = random_integer([0, 1, 2], counter_probabilities)
            self.sim.states.customer_type_cnt[counter_mapping[grp_type]] += 1
            self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim, group_no, counter_mapping[grp_type], 0, 0))

        # exit event
        self.sim.schedule_event(ExitEvent(simulation_duration, self.sim))


class ExitEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self):
        print("simulation is going to end now. current time:", self.event_time)


class ArrivalEvent(Event):
    def __init__(self, event_time, sim, grp_no, grp_type, current_counter, q_no):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.group_no = grp_no
        self.grp_type = grp_type
        self.current_counter = current_counter
        self.q_no = q_no

    def process(self):
        global group_no

        # schedule next arrival
        if self.current_counter == 0 and self.group_no not in arrival_controller:
            self.sim.states.current_customers += 1

            grp_size_type = random_integer(group_sizes, group_size_probabilities)
            arrival_time = self.event_time + expon(inter_arrival_mean)
            group_no += 1

            # mark it to avoid excessive event creations
            arrival_controller[self.group_no] = True

            for i in range(grp_size_type):
                grp_type = random_integer([0, 1, 2], counter_probabilities)
                self.sim.states.customer_type_cnt[counter_mapping[grp_type]] += 1
                self.sim.schedule_event(
                    ArrivalEvent(arrival_time, self.sim, group_no, counter_mapping[grp_type], 0, 0))

        # process the current arrival
        if self.sim.states.servers_available[self.grp_type] > 0:
            self.sim.states.servers_available[self.grp_type] -= 1

            # counter is the current counter name - hot_food / sandwich / drinks / cash
            counter = counter_routing[self.grp_type][self.current_counter]

            # if cash then use act
            service_time = 0
            if counter == "cash":
                for key in counter_act:
                    x = uniform_rand(counter_act[key][0], counter_act[key][1])
                    service_time += x
            else:
                service_time = uniform_rand(counter_st[counter][0], counter_st[counter][1])

            # if cash then find which counter it is
            q_no = 0
            if counter == "cash":
                for i in range(len(self.sim.states.cash_server)):
                    if self.sim.states.cash_server[i] == 0:
                        self.sim.states.cash_server[i] = 1
                        q_no = i
                        break

            self.sim.schedule_event(
                DepartureEvent(self.event_time + service_time, self.sim, self.group_no, self.grp_type,
                               self.current_counter, q_no))

        else:
            # append to the shortest queue. for food counters idx will always be 0
            # for drinks counter, it will never reach this far as inf - 1 is inf
            idx = 0
            mn = np.inf
            for i in range(len(self.sim.states.queue[self.grp_type])):
                if len(self.sim.states.queue[self.grp_type][i]) < mn:
                    mn = self.sim.states.queue[self.grp_type][i]
                    idx = 0

            self.q_no = idx
            self.sim.states.queue[self.grp_type][idx].append(self)


class DepartureEvent(Event):
    def __init__(self, event_time, sim, grp_no, grp_type, current_counter, q_no):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.group_no = grp_no
        self.grp_type = grp_type
        self.current_counter = current_counter
        self.q_no = q_no

    def process(self):
        # check if the queue of the counter has more people
        counter = counter_routing[self.grp_type][self.current_counter]
        self.sim.states.served[counter] += 1

        if len(self.sim.states.queue[counter][self.q_no]) > 0:
            u = self.sim.states.queue[counter][self.q_no].pop(0)

            # check delay
            delay = self.sim.now() - u.event_time

            # delay update
            if counter != "drinks":
                self.sim.states.avg_q_delay[counter] += delay
                self.sim.states.max_q_delay[counter] = max(self.sim.states.max_q_delay[counter], delay)

            self.sim.states.avg_delay_customer[u.grp_type] += delay
            self.sim.states.max_delay_customer[u.grp_type] = max(self.sim.states.max_delay_customer[u.grp_type], delay)

            # schedule the departure
            # if cash then use act
            service_time = 0
            if counter == "cash":
                for key in counter_act:
                    x = uniform_rand(counter_act[key][0], counter_act[key][1])
                    service_time += x
            else:
                service_time = uniform_rand(counter_st[counter][0], counter_st[counter][1])

            self.sim.schedule_event(
                DepartureEvent(self.event_time + service_time, self.sim, self.group_no, self.grp_type,
                               self.current_counter, self.q_no))

        else:
            # free resources
            self.sim.states.servers_available[counter_routing[self.grp_type][self.current_counter]] += 1
            if self.grp_type == "cash":
                self.sim.states.cash_server[self.q_no] = 0

        # send to next.
        if self.current_counter < len(counter_routing[self.grp_type]) - 1:
            # create new arrival
            # q_no does not matter here
            self.sim.schedule_event(
                ArrivalEvent(self.event_time, self.sim, self.group_no, self.grp_type, self.current_counter + 1, 0))
        else:
            self.sim.states.current_customers -= 1


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

        start = time.time()
        while len(self.eventQ) > 0:
            current_time, event = heapq.heappop(self.eventQ)
            if event.eventType == 'EXIT':
                break

            if self.states is not None:
                self.states.update(event)

            self.simulator_clock = event.event_time
            event.process()

        end = time.time()
        print("time taken:", end - start)

        return self.states.finish(self)


def cafeteria_model():
    seed = 1
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
   a. first generate group size. group_no will be 1
   b. then for each of the student, find their food type and create arrival event for them
   c. set q_no as 0
2. schedule the exit

exit-event
-------------
1. keep this as it is

arrival-event
-------------
1. if this is the customers first food counter and the group that has not been used to create new arrival, then create
   another arrival-event with group_no + 1 label. mark this group as used. 
2. now lets start processing this one
3. if the corresponding food section has idle employee start serving immediately. otherwise select the smallest 
   queue and insert the event there. if there are idle employee in cash then determine the index and save it as
   q_no. 
   
departure-event
----------------
1. check if the corresponding queue has any customer in it, if there's someone then start serving that customer and
   schedule a departure-event for the customer
2. if the current departure-event is not in the cash counter then schedule an arrival-event in the next counter
"""
