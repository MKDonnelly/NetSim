import math
import random
import time
from packetQueue import *
from wlanclient import *

# Seed random number generator
random.seed(time.time())

###########################################################
##############     PARAMETERS USED IN SIMULATION   ########
###########################################################
# User will enter these values

# Rate of packet arrival
lambdaValue = float(input("Enter value for lambda: "))

# Number of hosts
nHosts = int(input("Enter number of hosts: "))

# Total frames to send
totalPackets = int(input("Enter number of frames: "))
#############################################################

wClients = []

for i in range(0, nHosts):
   wClients.append(wClient(lambdaValue, i, wClients))

# According to clarifications on piazza, 
# lambda is the rate of arrival of a packet
# in the network as a whole. Below, I implement  
# this by inserting a packet arrival event into
# the array of clients. The process of generating
# the packet length is handled by the client
# when this event is processed
packetArrivalTime = 0
for i in range(0, totalPackets):
   # The mean arrival time is negExp(lambda)
   packetArrivalTime += negExp(lambdaValue)

   # Choose a random client
   randClient = random.randint(0, nHosts-1)

   # Set a packet to arrive using the negExp distribution
   wClients[randClient].addEvent(Event(packetArrivalTime, EVENT_PKT_ARRIVAL))


# Now start at time 0 and get the first event
# for each wireless client.  This loop will 
# basically look at each of the wireless clients,
# pick the one with the event that comes first
# in time, update all of the other wireless clients,
# and then continue
eventTime = 0
while clientWantsToSend(wClients):
   # Find nearest time to perform an action
   for client in wClients:
      client.updateClient(eventTime)

   # Each client will sense the channel every .01ms
   # and update it's state
   eventTime += .01

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
# the throughput. Divide by 1000 since the delays are in ms
totalDelay = sumOfDelay(wClients) / 1000
print("Average delay (in seconds): " + str(totalDelay / totalPackets))
