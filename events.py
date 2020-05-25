# Used when a packet arrives at a client
EVENT_PKT_ARRIVAL = 0

# This is used to unblock the channel 
# after the transmission delay
EVENT_UNBLOCK_CHANNEL = 1

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

   # Gets the first element at the head of the event list
   # and returns it
   def getFirst(self):
      if len(self.events) > 0:
         return self.events.pop(0)
      else:
         return -1;

   def firstTime(self):
      if len(self.events) > 0:
         return self.events[0].getTime()
      else:
         return -1

   # Return number of events left
   def eventsLeft(self):
      return len(self.events)
