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

# Some constants that are useful to keep track of

# ACK length in bits
ACK_LENGTH = 64 * 8

# Wireless channel rate in bits
WCHAN_RATE = 11 * pow(10, 6)

# We can sense every .01ms
SENSE_RATE = .01

# Value of SIFS is .05ms
SIFS = .05
# Value of DIFS is .1ms
DIFS = .1

# A client can be in different states depending on
# what it has sent or is expecting to receive

# The client will be in the state whenever it is
# ready or attempting to send a packet
STATE_READY = 0

# The client will be waiting for DIFS
# to go to 0 in this state
STATE_DIFS_WAIT = 1

# The client will be counting down from
# a backoff in this state
STATE_BACKOFF = 2

# The client will be transmitting a packet
# in this state
STATE_TRANSMIT = 3

# The client will be waiting for an ACK
# after sending a packet in this state
STATE_WAIT_ACK = 4

# The client will be waiting SIFS before sending 
# and ACK in this state
STATE_SIFS_WAIT = 5

# The client will be sending an ACK in this state
STATE_SEND_ACK = 6

# The client will be done with all operations in
# this state
STATE_DONE = 7

# A wireless client
class wClient:
   # wClients is the array of clients we are using
   # in the simulation.
   # In wlansim.py, we have a list of wireless clients
   # clientIndex is the index of this client in that list
   # and clientsList is the actual list. We use this below
   # when sending data to a random client
   def __init__(self, lambdaValue, clientIndex, clientsList):
      self.lambdaValue = lambdaValue
      self.clientIndex = clientIndex
      self.clientsList = clientsList
      self.state = STATE_READY

      # This will hold events the client need to
      # process, like packet arrival and sending packets
      self.eventList = EList()

      # This is used to hold packets as they arrive at the client
      self.packetQueue = PacketQueue()

      # Keep track of how much data we have sent and 
      # the total delay of all the packets sent
      self.dataCounter = 0
      self.delayCounter = 0

      # Keep track of the SIFS and DIFS values. These
      # are updated every time the client updates
      self.sifs = SIFS
      self.difs = DIFS


   # This is used by the main event loop to add a new 
   # packet arrival
   def addEvent(self, event):
      self.eventList.insert(event)

   # Updates the client to currentTime
   # The client will look through its event list and
   # perform any events that need to happen
   # by currentTime
   def updateClient(self, currentTime):
#      print("Client " + str(self.clientIndex) + " state is " + str(self.state))
      global channelBusy

      # Handle any events from the event list
      while self.eventList.eventsLeft() > 0 and \
            self.eventList.firstTime() <= currentTime:
         event = self.eventList.getFirst()
         if event.getType() == EVENT_PKT_ARRIVAL:
            # Generate a new packet and add it to the packet queue
            self.packetQueue.append(Packet(event.getTime()))


      if self.state == STATE_READY:
         if not channelBusy and self.packetQueue.size() > 0:
            self.state = STATE_DIFS_WAIT
         elif channelBusy:
            self.state = STATE_BACKOFF
            # TODO need to fix this; we need the backoff to
            #      increase as more colissions happen
            self.backoffValue = randomBackoff(1)

      elif self.state == STATE_DIFS_WAIT:
         if not channelBusy:
            self.difs -= .01
            if self.difs <= 0:
               self.state = STATE_TRANSMIT

      elif self.state == STATE_BACKOFF:
         if not channelBusy:
            self.backoffValue -= .01
            if self.backoffValue <= 0:
               self.state = STATE_READY

      elif self.state == STATE_TRANSMIT:
         # Transmit packet to a random client
         # First block channel
         channelBusy = 1

         # Get packet from queue
         p = self.packetQueue.pop()

         # Calculate delays for the packet
         queuingDelay = currentTime - p.getStartTime() 
         transmissionDelay = p.getSize() / WCHAN_RATE

         # Pick a random peer to send to
         randomClient = random.randint(0, len(self.clientsList)-1)
         # The only thing we give to the other client is our index.
         # This will let us unblock when it sends an ACK to us
         self.clientsList[0].givePacket(1)

         # Unblock after transmission
         self.eventList.insert(Event(currentTime + transmissionDelay, \
                                     EVENT_UNBLOCK_CHANNEL))

         # Now initialize how long we should wait and then go
         # into the ack waiting state
         self.ackReceived = 0
         self.waitTime = transmissionDelay + SIFS
         self.state = STATE_WAIT_ACK

      elif self.state == STATE_WAIT_ACK:
         # Wait to receive an ACK.
         # If we do, our state will automatically be
         # changed to STATE_READY, so this only handles
         # the case when we timeout
         if self.ackReceived:
            print("Got ACK!")
            self.state = STATE_DONE

         self.waitTime -= .01
         if self.waitTime <= 0:
            # Timeout, for now just print that this happened
            print("Client " + str(self.clientIndex) + " in state " + str(self.state))
            print("Timeout!!!")
            self.state = STATE_DONE

      elif self.state == STATE_SIFS_WAIT:
         self.state = STATE_SEND_ACK

      elif self.state == STATE_SEND_ACK:
         pass
 

      if self.packetQueue.size() == 0 and \
           self.eventList.eventsLeft() == 0 and \
           self.state != STATE_WAIT_ACK and \
           self.state != STATE_SIFS_WAIT:
         self.state = STATE_DONE
 
  
   # Let's call this client A and the one we just sent a packet to B.
   # Once B has received the packet, it will send an ACK back to A.
   # To do that, B calls this method on A
   def acceptACK(self):
      print("Client " + str(self.clientIndex) + " accepted ack")
      self.ackReceived = 1

   # This is called when we send a packet from one client to another
   # We provide the other client the index of the sending client in
   # the array so that this client can send back an ACK
   def givePacket(self, i):
      print("Client " + str(self.clientIndex) + " accepted packet from " + str(i))
      self.clientsList[1].acceptACK()

   # A client will want to send packets if there
   # are any events in the event list other than
   # the sense delays or if there are packets
   # in the packet queue. Since we can have a max of
   # 1 sense delay, a length of 2 or more indicates
   # there are still events to process
   def wantsToSend(self):
      return self.state != STATE_DONE

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
