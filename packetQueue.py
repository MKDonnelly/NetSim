import math
import random
import time

def negExp(rate):
   return (-1. / rate) * math.log(1 - random.uniform(0, 1))

def packetSize():
   # The assignment did not specify the lambda term to 
   # use for the packet size since it is negatively
   # exponentially distributed. I have just set
   # it to .5 here
   # TODO: This doesn't work. The packet is not within
   #       the range 0 to 1544
   return int(negExp(.5) * 1544)

class Packet:
   def __init__(self, startTime):
      self.size = packetSize()
      print("Packet size is " + str(self.size))
      self.startTime = startTime

   def getSize(self):
      return self.size

   def getStartTime(self):
      return self.startTime

# For the purposes of project 2, the queue does not have 
# a fixed capacity.
class PacketQueue:
   def __init__(self):
      self.packets = []

   # Add a packet to the queue
   def append(self, packet):
      self.packets.append(packet)

   # Remove packet from queue
   def pop(self):
      if len(self.packets) == 0:
         return -1
      else:
         return self.packets.pop(0)

   #Returns total number of packets in queue
   def size(self):
      return len(self.packets)
