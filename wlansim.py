import math
import random
import time
from packetQueue import PacketQueue
from wlanclient import *

# Seed random number generator
random.seed(time.time())

###########################################################
##############     PARAMETERS USED IN SIMULATION   ########
###########################################################
# 		ALL TIME VALUES ARE IN MS!!!!!!
# Rate of packet arrival
lambdaValue = 1

# Number of hosts
nHosts = 10

# The random backoff upper bound
t = 1
#############################################################

eventTime = 0
wClients = []

for i in range(0, nHosts):
   wClients.append(wClient(lambdaValue, t, i))

# According to clarifications on piazza, 
# lambda is the rate of arrival of a packet
# in the network as a whole. Below, I implement  
# this by inserting a packet arrival event into
# the array of clients. The process of generating
# the packet length is handled by the client
# when this event is processed
packetArrivalTime = 0
# I guess we will iterate for 10,000 packets...
for i in range(0, 10000):
   # The mean arrival time is negExp(lambda)
   packetArrivalTime += negExp(lambdaValue)

   # Choose a random client
   randClient = random.randint(0, nHosts-1)

   # Set a packet to arrive using the negExp distribution
   wClients[randClient].addEvent(Event(packetArrivalTime, EVENT_PKT_GENERATED))


# Now start at time 0 and get the first event
# for each wireless client.  This loop will 
# basically look at each of the wireless clients,
# pick the one with the event that comes first
# in time, update all of the other wireless clients,
# and then continue
while clientWantsToSend(wClients):
   # Find nearest time to perform an action
   eventTime = nearestClientTime(wClients)
#   print("Time: " + str(eventTime))
   updateClients(wClients, eventTime)

# At this point, eventTime will hold the time that the
# simulation ended

# Display statistics for the simulation

# Each wlan client will hold the number of data bytes
# it has received. We can sum them up using the
# sumOfData function provided
bTransmitted = sumOfData(wClients)
# Event time is in ms, convert to seconds
timeInSeconds = eventTime / 1000
throughput = bTransmitted / timeInSeconds
print("Throughput (in bits/second): " + str(round(throughput)))

# According to the assignment, the average network delay
# is the total delay of all of the hosts divided by
# the throughput
totalDelay = sumOfDelay(wClients)
print("Average delay (in seconds): " + str(totalDelay / throughput))
