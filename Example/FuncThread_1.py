from threading import Thread
from time import sleep
def func(value,name):
    for i in range(5):
        print("from {0:s} thread: value:{1:d}, new value {2:d}\n".
              format(name,value,i+value))
        sleep(0.5)
th1 = Thread(target=func, args=(120,'th1'))
print("thread1 status: {0}".format(th1.is_alive()))
th2 = Thread(target=func, args=(220,'th2'))
print("thread2 status: {0}".format(th2.is_alive()))
th1.start()
print("thread1 status: {0}".format(th1.is_alive()))
th2.start()
print("thread2 status: {0}".format(th2.is_alive()))
th1.join()
print("thread1 status: {0}".format(th1.is_alive()))
th2.join()
print("thread2 status: {0}".format(th2.is_alive()))
print("--> stop")