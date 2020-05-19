import math
import random
import time
from packetQueue import PacketQueue
from events import *

# Used to indicate that a client is sending
# Clients will poll this to check when it
# is ok to send
channelBusy = 0

def negExp(rate):
   return (-1. / rate) * math.log(1 - random.uniform(0, 1))

def randomBackoff(t):
   return random.randrange(0, t)


# A wireless client
class wClient:
   def __init__(self, lambdaValue, t):
      self.lambdaValue = lambdaValue
      self.randomBackoff = t

      # As the simulation runs, we will keep
      # track of the amount of data sent on
      # this client in dataCounter and the sum
      # of the delays the packet encountered
      # before reaching its destination
      self.dataCounter = 0
      self.delayCounter = 0

      # NOTE: For the parameters below, we are assuming
      #       these values as per the assignment. There should
      #       be no need to adjust these when running the simulation
      # SIFS is .05ms and DIFS is .1ms, we are
      # just assuming this according to the assignment
      self.sifs = .05
      self.difs = .1

      # We can sense the channel every .01ms
      self.senseDelay = .01

      # ACK packets are 64 bytes in length
      self.ackLen = 64

      # Wireless channel rate is 11Mbps
      self.wchanrate = 11 * pow(10, 6)

      # Generate packet inter arrival times
      # We will default to 100 packets
      eventTime = 0
      self.eventList = EList()
      for i in range(0, 100):
         eventTime += negExp(lambdaValue)
         self.eventList.insert(Event(eventTime, EVENT_PKT_ARRIVE))

      self.packetQueue = PacketQueue()

   # Updates the client to currentTime
   # The client will look through its event list and
   # perform any events that need to happen
   # by currentTime
   def updateClient(self, currentTime):
      # We know that we can have at most one event in the
      # event list happen when updating the currentTime
      # this is because we select the nearest time
      # of all the clients
      # .getHead() does not remove the head element, it
      # just returns it so that we can check it
      firstEvent = self.eventList.getHead()
      if firstEvent != -1 and firstEvent.getTime() <= currentTime:
         # .remove() actually removes the head element
         # since we are actually processing it in here
         firstEvent = self.eventList.remove()

         # Check the event type, and perform the correct
         # action based on the type
      

   # A client will want to send packets if there
   # are any events in the event list
   def wantsToSend(self):
      return self.eventList.eventsLeft()

   # Return the nearest time of an event the client
   # needs to perform 
   def nearestTime(self):
      eventHead = self.eventList.getHead()
      if eventHead != -1:
         return eventHead.getTime()
      else:
         return -1

   # Returns the amount of data the client sent 
   def bytesSent(self):
      return self.dataCounter

   # Return the total amount of delay the packets
   # encountered before reaching this client
   def totalDelay(self):
      return self.delayCounter

# This takes an array of wClient's and 
# checks if any of them still have data to send.
# I use this in the main event loop to check when
# we can terminate the loop
def clientWantsToSend(wClientsList):
   wantsToSend = False
   for client in wClientsList:
      if client.wantsToSend():
         wantsToSend = True
   return wantsToSend

# Searches through a list of wireless clients
# to find the next time that one of them does 
# something
def nearestClientTime(wClientsList):
   nearestTime = math.inf
   for client in wClientsList:
      if client.nearestTime() < nearestTime and client.nearestTime() != -1:
         nearestTime = client.nearestTime()
   return nearestTime

# When the simulation is running, every iteration we move
# forward to the next time at which point a client has 
# something to do. This function updates each client
# to that next point in time.
def updateClients(wClientsList, nextTime):
   for client in wClientsList:
      client.updateClient(nextTime)

# Gets the sum of all the data the clients received
# during the simulation
def sumOfData(wClientsList):
   dataSum = 0
   for client in wClientsList:
      dataSum += client.bytesSent()
   return dataSum

# Gets the sum of all the delays the packets
# encountered during the simulation
def sumOfDelay(wClientsList):
   delaySum = 0
   for client in wClientsList:
      delaySum += client.totalDelay()
   return delaySum
