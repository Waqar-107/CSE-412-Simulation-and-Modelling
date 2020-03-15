# algorithm

1. declare number of events = 2, there are two events, 
arrival and departure.

2. initialize the variables. time_next_event[1] is for arrival
and time_next_event[2] is for departure. so arrival time is set to
a random number added with simulation time and departure time set
to an arbitrary large number

3. while the delayed customer no. is not equal to the required number repeat from 4

4. call timing() to determine the next event. it will be either an arrival
or a departure. 

5 update time average stats


# variable-nama

server_status: either busy or idle

number_of_customers_delayed: customers who had to wait in the queue

number_of_delays_req: no. of customers we need who had to wait

time_next_event[]: time when event will occur

simulation_time: as the name explains :v