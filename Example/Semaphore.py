from threading import Thread, BoundedSemaphore
from time import sleep, time

ticket_office = BoundedSemaphore(value=3)

def ticket_buyer(number):
   start_service = time()
   with ticket_office:
       sleep(1)
       print("client {0:d}, service time: {1:1.6f}".format(number,time() - start_service))

buyer = [Thread(target=ticket_buyer, args=(i,)) for i in range(5)]

for b in buyer:
   b.start()