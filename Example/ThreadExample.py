# coding: UTF-8
from threading import Thread


def prescript(thefile, num):
    with open(thefile, 'w') as f:
        for i in range(num):
            if num > 500:
                f.write('МногоБукв\n')
            else:
                f.write('МалоБукв\n')


thread1 = Thread(target=prescript, args=('f1.txt', 200,))
thread2 = Thread(target=prescript, args=('f2.txt', 1000,))

thread1.start()
thread2.start()
thread1.join()
thread2.join()
