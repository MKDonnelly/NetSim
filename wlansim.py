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
# Rate of packet arrival
lambdaValue = .1

# Number of hosts
nHosts = 10

# The random backoff upper bound
t = 1

# The number of packets each client will send
# I guess we assume 100 here, or some other large
# value...
clientPackets = 100
#############################################################

eventTime = 0
wClients = []

for i in range(0, nHosts):
   wClients.append(wClient(lambdaValue, t))

# Now start at time 0 and get the first event
# for each wireless client.  This loop will 
# basically look at each of the wireless clients,
# pick the one with the event that comes first
# in time, update all of the other wireless clients,
# and then continue. This will continue until each
# client has sent it's default of 100 packets
while clientWantsToSend(wClients):
   # Find nearest time to perform an action
   eventTime = nearestClientTime(wClients)
   updateClients(wClients, eventTime)

# At this point, eventTime will hold the time that the
# simulation ended

# Display statistics for the simulation

# Each wlan client will hold the number of data bytes
# it has received. We can sum them up using the
# sumOfData function provided
#bTransmitted = sumOfData(wClients)
#throughput = str(bTransmitted / eventTime)
#print("Throughput: " + throughput)

# According to the assignment, the average network delay
# is the total delay of all of the hosts divided by
# the throughput
#totalDelay = sumOfDelay(wClients)
#print("Average delay: " + str(totalDelay / throughput))
