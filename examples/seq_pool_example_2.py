from multiprocessing import Process, Lock, Pipe
from TPool import SeqPool
import string


class Example:

    def __init__(self):
        self.data = dict()

    def set_even_or_odd(self, n, lock):
        lock.acquire()
        val = ""
        if n%2 == 0:
            val = "even"
        else:
            val = "odd"
        self.data[n] = val
        lock.release()

    def test_threads(self):
        params_list = []
        lock = Lock()
        for i in range(100):
            params_list.append((i, lock))
        pool = SeqPool(pool_size=10, target=self.set_even_or_odd, params_list=params_list)
        pool.run()
        print(self.data)


a = Example()
a.test_threads()