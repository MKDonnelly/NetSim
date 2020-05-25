import math
import random
import time
from packetQueue import *
from events import *

# Used to indicate that a client is sending
# Clients will poll this to check when it
# is ok to send
channelBusy = 0

def negExp(rate):
   return (-1. / rate) * math.log(1 - random.uniform(0, 1))

def randomBackoff(t):
   return random.randrange(0, pow(2,t))

# A client can be in any one of these states
# This helps when we are running the simulation
# to determine what the client needs to do
STATE_WAIT_DSFS = 0
STATE_WAIT_SIFS = 1
STATE_SENDING_PACKET = 2
STATE_WAIT_FOR_ACK = 3

# A wireless client
class wClient:
   # wClients is the array of clients we are using
   # in the simulation
   def __init__(self, lambdaValue, t, i, wClients):
      self.clientID = i
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

      # The client will keep track of these counters
      self.sifsCounter = self.sifs
      self.difsCounter = self.difs

      self.eventList = EList()

      # The client will sense the channel every senseDelay time
      # For simplicity, we do this every time, regardless of 
      # if we have packets left to send or not. We start of by
      # sensing senseDelay after we start the simulation
      self.eventList.insert(Event(self.senseDelay, EVENT_SENSE_CHANNEL))

      self.packetQueue = PacketQueue()


   # Called by the main loop to insert packet arrival times
   def addEvent(self, event):
      self.eventList.insert(event)

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

      # This is for handling packet arrival events
      if firstEvent != -1 and firstEvent.getTime() <= currentTime:
         # .remove() actually removes the head element
         # since we are actually processing it in here
         firstEvent = self.eventList.remove()

         # Check the event type, and perform the correct
         # action based on the type
         if firstEvent.getType() == EVENT_PKT_GENERATED:
            # Add the generated packet to the packet queue, and note at what
            # time it arrived so we can calculate the delay later. The
            # size of the packet is calculated in the __init__ of
            # the Packet class 
            self.packetQueue.append(Packet(currentTime))

         elif firstEvent.getType() == EVENT_SENSE_CHANNEL:
            global channelBusy
            if self.packetQueue.size() > 0 and not channelBusy:
               # Sense the channel. If it is unblocked and we have
               # a packet to send, then send it off
               # We always need to put in a channel sense since
               # that is what helps us keep track of the SIFS and DIFS time

               print("Client " + str(self.clientID) + " sending at " + str(currentTime))

               # Send a packet if the channel is not busy
               channelBusy = 1

               # Get a packet to send
               p = self.packetQueue.pop()
 
               # Calculate the delay for the packet
               transmitDelay = p.getSize() / self.wchanrate
               queuingDelay = currentTime - p.getStartTime()

               # Update counters 
               self.dataCounter += p.getSize()
               self.delayCounter += transmitDelay + queuingDelay

               # Unblock channel after done sending
               self.eventList.insert(Event(currentTime + transmitDelay, EVENT_UNBLOCK_CHANNEL))

               # This will let us sense the channel in the future
            self.eventList.insert(Event(currentTime + self.senseDelay, EVENT_SENSE_CHANNEL))
            # If the channel is busy, we do a random backoff
            # and don't sense the channel until then
#            elif channelBusy:
#               self.eventList.insert(Event(currentTime + randomBackoff(self.randomBackoff), EVENT_SENSE_CHANNEL))

         elif firstEvent.getType() == EVENT_UNBLOCK_CHANNEL:
            channelBusy = 0

         elif firstEvent.getType() == EVENT_SENSE_CHANNEL:
            self.eventList.insert(Event(currentTime + self.senseDelay, EVENT_SENSE_CHANNEL))


   # A client will want to send packets if there
   # are any events in the event list other than
   # the sense delays or if there are packets
   # in the packet queue. Since we can have a max of
   # 1 sense delay, a length of 2 or more indicates
   # there are still events to process
   def wantsToSend(self):
      return self.eventList.eventsLeft() > 1 or self.packetQueue.size() > 0

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

