import math
import random
import numpy.random

def negExp(rate):
   return (-1. / rate) * math.log(1 - random.uniform(0, 1))

def pareto(rate):
   return numpy.random.pareto(rate)

#Based on the assignment, we actually do not need to store
#anything in the queue.  All we need is the number of packets
#in the queue and if we need to drop a packet
class PacketQueue:
   #If MAXBUFFER == -1, the queue
   # is "infinite" in the sense that
   # we do not check its size. Otherwise,
   # we limit the queue's size to this value
   def __init__(self, maxsize):
      self.MAXBUFFER = maxsize
      self.totalPackets = 0

   #Add a packet to the queue
   #Returns -1 if the packet was dropped, 0 otherwise
   def append(self):
      if self.MAXBUFFER == -1:
         self.totalPackets += 1
         return 0
      elif self.totalPackets + 1 <= self.MAXBUFFER:
         self.totalPackets += 1
         return 0
      else:
         return -1

   #Decrements number of packets. Returns -1 if queue is empty
   def pop(self):
      if self.totalPackets == 0:
         return -1
      else:
         self.totalPackets -= 1

   #Returns total number of packets in queue
   def size(self):
      return self.totalPackets

#mu is the rate in packets/second used for -exp dist
EVENT_ARRIVAL = 0
EVENT_DEPARTURE = 1
class Event:
   def __init__(self, etime, etype):
      self.event_time = etime
      self.event_type = etype

   def getTime(self):
      return self.event_time

   def getType(self):
      return self.event_type
   
class GEL:
   def __init__(self):
      self.events = []

   def insert(self, event):
      # I use a selection sort algorithm to
      # insert the element.  Append it to the end
      # and then slide it back based on the event
      # time field
      self.events.append(event)

      #Move the appended element back as needed
      elementIdx = len(self.events) - 1
      while self.events[elementIdx].getTime() < \
            self.events[elementIdx-1].getTime() and elementIdx >= 1:
         #Swap elements
         self.events[elementIdx], self.events[elementIdx-1] = \
                  self.events[elementIdx-1], self.events[elementIdx]
         elementIdx -= 1

   def remove(self):
      if len(self.events) > 0:
         return self.events.pop(0)
      else:
         return -1;

   def eventsLeft(self):
      return len(self.events) > 0


#First, create the global event list and populate it with the
#arriving packets
globalEvents = GEL()

#This holds the time as we are generating inter arrival times.
#We will start at 0, and will begin by incrementing it by a generated
#inter arrival time. For every packet we generate in the loop below,
#this will be incremented to be the next time that a packet arrives
eventTime = 0

#These two parameters are used in the test part of our report
###########################################################
#Rate of packet arrival
lambdaValue = .1

#Packets/second that are transmitted
muValue = 1

#Size of the queue
queueSize = 1
#############################################################

#I guess by default we will assume 1,000 packets...
for i in range(1, 1000):
   #Generate the arrival time of the next packet using
   #the pareto distribution
   eventTime += pareto(lambdaValue)

   #Now create and insert the new event into the GEL 
   globalEvents.insert(Event(eventTime, EVENT_ARRIVAL))


####################################################
#Statistics

#Utilization. A running total of the time the server 
#was active
utilizationTime = 0

#One parameter we need to track is the average queue length
#The average is the sum of all queue lengths we observe 
#divided by the number of observations (i.e. if we see
#queue lengths of 1, 2, and 3, the average length is
#(1 + 2 + 3) / 3)
sumQueueLengths = 0
numLengths = 0

#sumQueueLengths / numLengths is the average queue size

#Number of packets dropped
droppedPackets = 0

####################################################
#Current time
ctime = 0

# Determines if the server is sending a packet
sendingPacket = 0

#Queue used to hold packets as they come in
queue = PacketQueue(queueSize)

#Now process the GEL to simulate packet arrival
while globalEvents.eventsLeft():
   event = globalEvents.remove()
   #Update queue stats
   sumQueueLengths += queue.size()

   #Number of times we checked the queue length
   numLengths += 1

   if event.getType() == EVENT_ARRIVAL:
      ctime = event.getTime()

      #Server is not sending packet, so we can send right away
      if sendingPacket == 0:
         sendingPacket = 1
         sendTime = negExp(muValue)
         utilizationTime += sendTime
         globalEvents.insert(Event(ctime + sendTime, EVENT_DEPARTURE))

      else:
         #Server is busy, so put the packet into the queue
         #check if we get -1 (queue is full)
         if queue.append() == -1:
            #Queue is full, so recored dropped packet
            droppedPackets += 1

   elif event.getType() == EVENT_DEPARTURE:
      #Used when we are processing packet departure
      ctime = event.getTime()

      #Since a packet just departed (and we can process at most 1 packet
      #at a time with the server), we have 0 packets being processed by
      #the server
      sendingPacket = 0

      #Check if there is anything in the queue
      if queue.pop() != -1:
         #Queue was not empty, so create departure for next packet
         sendTime = negExp(muValue)
         globalEvents.insert(Event(ctime + sendTime, EVENT_DEPARTURE))

         #The server will be sending this packet, so update utilization time
         utilizationTime += sendTime

         sendingPacket = 1

# At this point, ctime will hold the time that the simulation terminates.
# We need this to calculate utilization rate (which is utilizationTime /
# ctime)

print("Utilization (%): ", utilizationTime / ctime)
print("Mean queue length (in packets): ", float(sumQueueLengths) / numLengths)
print("Dropped packets: ", droppedPackets)
