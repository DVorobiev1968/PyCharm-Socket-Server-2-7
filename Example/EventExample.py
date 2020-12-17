from threading import Thread, Event
from time import sleep, time


event = Event()


def worker(name):
   event.wait()
   print("Worker: {0}\n".format(name))


# Clear event
event.clear()

# Create and start workers
workers = [Thread(target=worker, args=("wrk {0}".format(i),)) for i in range(5)]
for w in workers:
   w.start()

print("Main thread")

event.set()