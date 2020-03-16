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

5. update time average stats

6. then decide whether to arrive or depart depending on the next_event_type

7. in arrival, we first determine the time of arrival. then if the server is busy we add the customer in the q
else we consider the delay = 0, we make the server busy and schedule a departure time for this customer

8. in depart, if the queue is empty then make the server idle. if not then calculate the amount of time the customer
in front got delayed, add it to total sum of delays


# variable-nama

server_status: either busy or idle

number_of_customers_delayed: customers who had to wait in the queue. two operations done:
    
    `++ when the server was idle and the customer arrived, added delay = 0 with the total`
    
    `when the customer departed, added the delay`
    
in short this variable counted the number of customers got served

number_of_delays_req: no. of customers we need who had to wait

time_next_event[]: time when event will occur

simulation_time: as the name explains :v

time_last_event: when did the last event occurred

time_since_last_event: time passed since the occurrence of the last event

area_number_in_q: 

area_server_status: amount of time the server has worked

next_event_type: decides what will be the next event, 1 for arrival, 2 for departure

total_of_delays: sum of delays