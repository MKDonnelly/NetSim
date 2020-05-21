import math
import random
import time

# This code handles the event list, which
# is used by wireless clients to determine
# what needs to happen next

# This event indicates a packet was generated
# for transmission by the client. These arrive
# in the network as a whole using the negExp distribution
EVENT_PKT_GENERATED = 0

# This event is for when the client begins
# sending the packet 
EVENT_SEND_PKT = 0

# Have the client begin sending the ACK
EVENT_SEND_ACK = 1

# We use this to unblock the channel that we
# previously blocked
EVENT_UNBLOCK_CHANNEL = 4

# We use this to sense the channel
EVENT_SENSE_CHANNEL = 5

# We use this every time we generate
# a new packet to send
EVENT_PKT_ARRIVE = 6

class Event:
   def __init__(self, etime, etype):
      self.event_time = etime
      self.event_type = etype

   def getTime(self):
      return self.event_time

   def getType(self):
      return self.event_type


class EList:
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

   # Remove event at head of list
   def remove(self):
      if len(self.events) > 0:
         return self.events.pop(0)
      else:
         return -1;

   def getHead(self):
      if len(self.events) > 0:
         return self.events[0]
      else:
         return -1

   # Return number of events left
   def eventsLeft(self):
      return len(self.events)
