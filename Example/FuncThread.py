from threading import Thread
from time import sleep
def func(dict):
    for i in range(5):
        print("from {0:s} thread: value:{1:d}, new value {3:d}\n".
              format(dict['name'],
                     dict['value'],
                     i+dict['value']))
        sleep(0.5)
th1 = Thread(target=func, args={'value':120,'name':'th1'})
th2 = Thread(target=func, args={'value':220,'name':'th2'})
th1.start()
th2.start()
th1.join()
th2.join()
print("--> stop")