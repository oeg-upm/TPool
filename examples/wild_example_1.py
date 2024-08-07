from TPool import WildPool
from threading import Thread, Lock
import string
import logging


class Example:

    def __init__(self):
        self.data = dict()
        self.lock = Lock()

    def set_even_or_odd(self, n):
        print(f"processing: {n}")
        self.lock.acquire()
        val = ""
        if n%2 == 0:
            val = "even"
        else:
            val = "odd"
        self.data[n] = val
        self.lock.release()

    def test_threads(self):
        logger = logging.getLogger('WildPool')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        pool = WildPool(pool_size=5, logger=logger)
        for i in range(100):
            th = Thread(target=self.set_even_or_odd, args=(i,))
            pool.add_thread(th)
        pool.join()
        print(self.data)


a = Example()
a.test_threads()