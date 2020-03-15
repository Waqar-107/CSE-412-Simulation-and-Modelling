# from dust i have come, dust i will be

import random
import math

# ================================================================
MODLUS = 2147483647
MULT1 = 24112
MULT2 = 26143

zrng = [1,
        1973272912, 281629770, 20006270, 1280689831, 2096730329, 1933576050,
        913566091, 246780520, 1363774876, 604901985, 1511192140, 1259851944,
        824064364, 150493284, 242708531, 75253171, 1964472944, 1202299975,
        233217322, 1911216000, 726370533, 403498145, 993232223, 1103205531,
        762430696, 1922803170, 1385516923, 76271663, 413682397, 726466604,
        336157058, 1432650381, 1120463904, 595778810, 877722890, 1046574445,
        68911991, 2088367019, 748545416, 622401386, 2122378830, 640690903,
        1774806513, 2132545692, 2079249579, 78130110, 852776735, 1187867272,
        1351423507, 1645973084, 1997049139, 922510944, 2045512870, 898585771,
        243649545, 1004818771, 773686062, 403188473, 372279877, 1901633463,
        498067494, 2087759558, 493157915, 597104727, 1530940798, 1814496276,
        536444882, 1663153658, 855503735, 67784357, 1432404475, 619691088,
        119025595, 880802310, 176192644, 1116780070, 277854671, 1366580350,
        1142483975, 2026948561, 1053920743, 786262391, 1792203830, 1494667770,
        1923011392, 1433700034, 1244184613, 1147297105, 539712780, 1545929719,
        190641742, 1645390429, 264907697, 620389253, 1502074852, 927711160,
        364849192, 2049576050, 638580085, 547070247]


def lcgrand(stream):
    stream = int(stream)

    zi = zrng[stream]
    lowprd = (zi & 65535) * MULT1
    hi31 = (zi >> 16) * MULT1 + (lowprd >> 16)
    zi = ((lowprd & 65535) - MODLUS) + \
         ((hi31 & 32767) << 16) + (hi31 >> 15)

    if zi < 0:
        zi += MODLUS

    lowprd = (zi & 65535) * MULT2
    hi31 = (zi >> 16) * MULT2 + (lowprd >> 16)
    zi = ((lowprd & 65535) - MODLUS) + \
         ((hi31 & 32767) << 16) + (hi31 >> 15)

    if zi < 0:
        zi += MODLUS
    zrng[stream] = zi

    return (zi >> 7 | 1) / 16777216.0


# ================================================================

queue_limit = 100
busy = 1
idle = 0

mean_inter_arrival, mean_service, number_of_delays_req = 0.0, 0.0, 0
outfile = open("out.txt", "w")

next_event_type, number_of_customers_delayed, number_of_events, number_in_q, server_status = 0, 0, 0, 0, 0
area_number_in_q, area_server_status, simulation_time, time_last_event, total_of_delays = 0.0, 0.0, 0.0, 0.0, 0.0
time_arrival = [0.0] * (queue_limit + 1)
time_next_event = [0.0] * 3


def expon(mean):
    # return random.expovariate(1.0 / mean)
    return -mean * math.log(lcgrand(1))


def initialize():
    global server_status, time_next_event, mean_inter_arrival, number_of_events, total_of_delays

    server_status = idle
    total_of_delays = 0.0

    # initialize the event list
    time_next_event[1] = simulation_time + expon(mean_inter_arrival)
    time_next_event[2] = 1.0e30


def timing():
    global next_event_type, number_of_events, time_next_event, simulation_time

    min_time_next_event = 1.0e29

    next_event_type = 0

    # determine the next event type
    for i in range(1, number_of_events + 1, 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i

    if next_event_type == 0:
        outfile.write("event list is empty at time " + str(simulation_time))
        exit(1)

    simulation_time = min_time_next_event


def update_time_avg_stats():
    global simulation_time, time_last_event, area_number_in_q, number_in_q, area_server_status

    time_since_last_event = simulation_time - time_last_event
    time_last_event = simulation_time

    # update area under number-in-queue function
    area_number_in_q += number_in_q * time_since_last_event

    # update area under server-busy indicator function
    area_server_status += server_status * time_since_last_event


def arrive():
    global number_in_q, time_next_event, simulation_time, total_of_delays,\
        number_of_customers_delayed, server_status, mean_service

    # schedule next arrival
    time_next_event[1] = simulation_time + expon(mean_inter_arrival)

    # check to see whether server is busy
    if server_status == busy:
        # server is busy so add a customer in the q
        number_in_q += 1

        if number_in_q > queue_limit:
            outfile.write("overflow in the q at " + str(simulation_time) + "\n")
            exit(2)

        # there's still room in the q
        time_arrival[number_in_q] = simulation_time

    else:
        # server is idle, so arriving customer has a delay of 0
        delay = 0.0
        total_of_delays += delay  # does this even make any difference?

        # make the server busy
        number_of_customers_delayed += 1
        server_status = busy

        # schedule a departure (service completion)
        time_next_event[2] = simulation_time + expon(mean_service)


def depart():
    global number_in_q, server_status, time_next_event, total_of_delays, \
        number_of_customers_delayed, mean_service, time_arrival

    # if the q is empty
    if number_in_q == 0:
        server_status = idle
        time_next_event[2] = 1.0e30

    else:
        number_in_q -= 1

        # compute the delay of the customer who is beginning service
        # and update the total delay of accumulator
        delay = simulation_time - time_arrival[1]
        total_of_delays += delay

        # inc the number of customers delayed and schedule departure
        number_of_customers_delayed += 1
        time_next_event[2] = simulation_time + expon(mean_service)

        for i in range(1, number_in_q + 1, 1):
            time_arrival[i] = time_arrival[i + 1]


def report():
    outfile.write("\navg delay in queue " + str(round(total_of_delays / number_of_customers_delayed, 3)) + "\n")
    outfile.write("\navg number in queue " + str(round(area_number_in_q / simulation_time, 3)) + "\n")
    outfile.write("\nserver utilization " + str(round(area_server_status / simulation_time, 3)) + "\n")
    outfile.write("\ntime simulation ended " + str(round(simulation_time, 3)) + "\n")

    outfile.close()


if __name__ == "__main__":
    infile = open("in.txt", "r")
    line = infile.readline()
    infile.close()

    mean_inter_arrival, mean_service, number_of_delays_req = map(float, line.split())
    number_of_delays_req = int(number_of_delays_req)

    outfile.write("single server queuing system")
    outfile.write("\nmean inter arrival time " + str(mean_inter_arrival))
    outfile.write("\nmean service time " + str(mean_service))
    outfile.write("\nnumber of customers " + str(number_of_delays_req) + "\n")

    # is this arbitrary?
    number_of_events = 2

    # initialize the simulation
    initialize()

    # run the simulation while more delays are still required
    while number_of_customers_delayed < number_of_delays_req:
        # determine the next event
        timing()

        update_time_avg_stats()

        if next_event_type == 1:
            arrive()
        else:
            depart()

    report()
