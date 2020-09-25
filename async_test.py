import multiprocessing as mp
from random import random
from time import sleep

class A(object):
    def __init__(self):

        self.d = dict()
        pass

    def do_something(self, i):
        sleep(random()/10.0)
        self.d[i] = True
        print(i)

    def run(self):
        manager = mp.Manager()
        self.d = manager.dict()
        processes = []
        for i in range(100):
            p = mp.Process(target=self.do_something, args=(i,))
            processes.append(p)
        [x.start() for x in processes]
        [x.join() for x in processes]

        print(f"Key count: {len(self.d.keys())}")


if __name__ == '__main__':
    a = A()
    a.run()