# from dust i have come, dust i will be

import heapq
from collections import defaultdict
import numpy as np
import random

# -------------------------------------
# variables
number_of_stations = 0
number_of_machines = []
inter_arrival_mean = 0.0
job_types = 0
job_probabilities = []
stations_in_each_task = []
station_routing = defaultdict(list)
mean_service_time = defaultdict(list)

# -------------------------------------
# constants
simulation_length = 1
simulation_hours = 8
precision = 3
simulation_itr = 30


def expon(mean):
    return random.expovariate(1 / mean)


def erlang(mean):
    y1 = expon(mean / 2)
    y2 = expon(mean / 2)

    return y1 + y2


def random_integer(probability_distribution):
    arr = [i for i in range(1, job_types + 1, 1)]
    return np.random.choice(arr, p=probability_distribution)


# States and statistical counters
class States:
    def __init__(self):
        self.queue = [[] for _ in range(number_of_stations + 1)]
        self.servers_busy = [0] * (number_of_stations + 1)

        # avg delay in each station
        self.served = [0] * (number_of_stations + 1)
        self.avg_q_delay = [0] * (number_of_stations + 1)

        # delay for each job type and overall job delay
        # for each type of job if delay found add in the  corresponding arrays
        # when the job finishes all the task, increase the cnt and add the total delay in the array
        self.job_delay = [0] * (job_types + 1)
        self.job_cnt = [0] * (job_types + 1)
        self.current_jobs_in_system = 0

        # to determine avg q length
        self.area_number_in_q = [0] * (number_of_stations + 1)

        # avg number of jobs in the system
        # area = time_since_last_event * (sum of q lengths + sum of servers busy)
        # finally area / sim.now()
        self.area_number_job = 0
        self.time_last_event = 0.0

        # results
        self.avg_delay_in_job = [0] * (job_types + 1)
        self.avg_number_in_q = [0] * (number_of_stations + 1)
        self.overall_avg_delay = 0.0
        self.avg_number_of_jobs = 0
        self.avg_delay_in_q = [0] * (number_of_stations + 1)

    def update(self, sim, event):
        time_since_last_event = event.event_time - self.time_last_event
        self.time_last_event = event.event_time

        # for avg q length
        for i in range(1, number_of_stations + 1, 1):
            self.area_number_in_q[i] += len(self.queue[i]) * time_since_last_event

        self.avg_number_of_jobs += self.current_jobs_in_system * time_since_last_event
        # delay and counts are being handled in the departure event

    def finish(self, sim):
        # calculate avg delay in queue for each of the jobs
        for i in range(1, job_types + 1, 1):
            if self.job_cnt[i]:
                self.avg_delay_in_job[i] = self.job_delay[i] / self.job_cnt[i]

        # overall delay for jobs
        self.overall_avg_delay = 0
        for i in range(1, job_types + 1, 1):
            self.overall_avg_delay += job_probabilities[i] * self.avg_delay_in_job[i]

        # average number of jobs the system
        self.avg_number_of_jobs /= sim.now()

        # avg delay in each q
        for i in range(1, number_of_stations + 1, 1):
            if self.served[i]:
                self.avg_delay_in_q[i] = self.avg_q_delay[i] / self.served[i]

        for i in range(1, number_of_stations + 1, 1):
            self.avg_number_in_q[i] = self.area_number_in_q[i] / sim.now()

        return self.avg_delay_in_job, self.overall_avg_delay, self.avg_number_of_jobs, self.avg_number_in_q, \
               self.avg_delay_in_q


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
        arrival_time = self.event_time + expon(inter_arrival_mean)
        job_type = random_integer(job_probabilities[1:])
        self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim, job_type, 1))

        # schedule the exit
        self.sim.schedule_event(ExitEvent(simulation_hours * simulation_length, self.sim))


class ExitEvent(Event):
    def __init__(self, event_time, sim):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        print("simulation is going to end now. current time:", self.event_time)


class ArrivalEvent(Event):
    def __init__(self, event_time, sim, job_type, current_station):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.job_type = job_type
        self.current_station = current_station

    def process(self, sim):
        # schedule the next arrival
        if self.current_station == 1:
            self.sim.states.job_cnt[self.job_type] += 1
            self.sim.states.current_jobs_in_system += 1

            arrival_time = self.sim.now() + expon(inter_arrival_mean)
            job_type = random_integer(job_probabilities[1:])
            self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim, job_type, 1))

        # now lets process the current arrival
        station = station_routing["job" + str(self.job_type)][self.current_station]
        if sim.states.servers_busy[station] == number_of_machines[station]:
            sim.states.queue[station].append(self)
        else:
            sim.states.servers_busy[station] += 1
            assert (0 <= sim.states.servers_busy[station] <= number_of_machines[station])

            # schedule a departure
            e = erlang(mean_service_time["job" + str(self.job_type)][self.current_station])
            depart_time = self.sim.now() + e
            sim.schedule_event(DepartureEvent(depart_time, self.sim, self.job_type, self.current_station))


class DepartureEvent(Event):
    def __init__(self, event_time, sim, job_type, current_station):
        super().__init__(sim)
        self.event_time = event_time
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.job_type = job_type
        self.current_station = current_station

    def process(self, sim):
        # find the station where this event was taking service
        station = station_routing["job" + str(self.job_type)][self.current_station]

        # this station served a job!
        self.sim.states.served[station] += 1

        # check if the job is done
        # if not done then schedule an arrival in the next station
        if self.current_station < stations_in_each_task[self.job_type]:
            arrival_time = self.sim.now()
            self.sim.schedule_event(ArrivalEvent(arrival_time, self.sim, self.job_type, self.current_station + 1))
        else:
            self.sim.states.current_jobs_in_system -= 1

        # now check the queue of the station where this event was
        # if someone is in the queue then schedule departure for that job
        if len(self.sim.states.queue[station]) == 0:
            self.sim.states.servers_busy[station] -= 1
            assert (0 <= sim.states.servers_busy[station] <= number_of_machines[station])

        else:
            ev = self.sim.states.queue[station].pop(0)
            delay = self.sim.now() - ev.event_time

            # add the delay of corresponding station and job
            self.sim.states.avg_q_delay[station] += delay
            self.sim.states.job_delay[ev.job_type] += delay

            # schedule a departure
            e = erlang(mean_service_time["job" + str(ev.job_type)][ev.current_station])
            depart_time = self.sim.now() + e
            sim.schedule_event(DepartureEvent(depart_time, self.sim, ev.job_type, ev.current_station))


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
                self.states.update(self, event)

            self.simulator_clock = event.event_time
            event.process(self)

        return self.states.finish(self)


def read_input():
    global number_of_stations, number_of_machines, inter_arrival_mean, job_types, job_probabilities, \
        stations_in_each_task, station_routing, mean_service_time

    f = open("job_shop_input.txt", "r")
    lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].endswith("\n"):
            lines[i] = lines[i][: -1]

    number_of_stations = int(lines[0])

    number_of_machines = list(map(int, lines[1].split()))
    number_of_machines = [0] + number_of_machines

    inter_arrival_mean = float(lines[2])
    job_types = int(lines[3])

    job_probabilities = list(map(float, lines[4].split()))
    job_probabilities = [0] + job_probabilities

    stations_in_each_task = list(map(int, lines[5].split()))
    stations_in_each_task = [0] + stations_in_each_task

    idx = 6
    for i in range(job_types):
        station_routing["job" + str(i + 1)] = list(map(int, lines[idx].split()))
        station_routing["job" + str(i + 1)] = [0] + station_routing["job" + str(i + 1)]

        mean_service_time["job" + str(i + 1)] = list(map(float, lines[idx + 1].split()))
        mean_service_time["job" + str(i + 1)] = [0] + mean_service_time["job" + str(i + 1)]

        idx += 2


def job_shop_model():
    read_input()

    seed = 107
    random.seed(seed)
    np.random.seed(seed)

    # -----------------------------------------------------
    # variables to hold the metric
    avg_delay_in_job = [0] * (job_types + 1)
    avg_number_in_q = [0] * (number_of_stations + 1)
    overall_avg_delay = 0.0
    avg_number_of_jobs = 0
    avg_delay_in_q = [0] * (number_of_stations + 1)

    # -----------------------------------------------------
    # run simulation for 30 times
    for i in range(simulation_itr):
        sim = Simulator()
        delay_in_job, overall_delay, number_of_jobs, number_in_q, delay_in_q = sim.run()

        for j in range(1, job_types + 1, 1):
            avg_delay_in_job[j] += delay_in_job[j]

        overall_avg_delay += overall_delay
        avg_number_of_jobs += number_of_jobs

        for j in range(1, number_of_stations + 1, 1):
            avg_number_in_q[j] += number_in_q[j]
            avg_delay_in_q[j] += delay_in_q[j]

    # -----------------------------------------------------
    # determine average
    for j in range(1, job_types + 1, 1):
        avg_delay_in_job[j] /= simulation_itr

    overall_avg_delay /= simulation_itr
    avg_number_of_jobs /= simulation_itr

    for j in range(1, number_of_stations + 1, 1):
        avg_number_in_q[j] /= simulation_itr
        avg_delay_in_q[j] /= simulation_itr

    # -----------------------------------------------------
    # generate report
    sp = " " * 10
    result = open("job_shop_output.txt", "w")

    result.write("Average total delay in queue for each jobs\n")
    result.write("job" + sp + "Average total delay in queue\n")
    for i in range(1, job_types + 1, 1):
        result.write(str(i) + sp + "  " + str(round(avg_delay_in_job[i], precision)) + "\n")

    result.write("\nOverall average delay: " + str(round(overall_avg_delay, precision)) + "\n")
    result.write("Average number of jobs: " + str(round(avg_number_of_jobs, precision)) + "\n\n")

    result.write("Work Station" + sp + "Average queue length" + sp + "Average delay in queue\n")
    for i in range(1, number_of_stations + 1, 1):
        result.write(str(i) + sp * 2 + str(round(avg_number_in_q[i], precision)) + sp * 2 + str(
            round(avg_delay_in_q[i], precision)) + "\n")


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
