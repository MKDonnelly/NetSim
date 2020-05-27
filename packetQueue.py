import math
import random
import time

def negExp(rate):
   return (-1. / rate) * math.log(1 - random.uniform(0, 1))

def packetSize(lambdaValue):
   # The assignment did not specify the lambda term to 
   # use for the packet size since it is negatively
   # exponentially distributed. I have just set
   # it to .5 here
   v = int(negExp(lambdaValue) * 1544)
   while v > 1544:
      v = int(negExp(lambdaValue) * 1544)
   return v


class Packet:
   def __init__(self, startTime, lambdaValue):
      self.size = packetSize(lambdaValue)
      self.startTime = startTime

   def getSize(self):
      # Return size in bits
      return self.size * 8

   def getStartTime(self):
      return self.startTime

# For the purposes of project 2, the queue does not have 
# a fixed capacity.
class PacketQueue:
   def __init__(self):
      self.packets = []

   # Add a packet to the end of the queue
   def append(self, packet):
      self.packets.append(packet)

   # Add a packet to the start of the queue
   def push(self, packet):
      self.packets.insert(0, packet)

   # Remove packet from queue
   def pop(self):
      if len(self.packets) == 0:
         return -1
      else:
         return self.packets.pop(0)

   #Returns total number of packets in queue
   def size(self):
      return len(self.packets)
