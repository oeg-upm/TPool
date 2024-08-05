import unittest

from TPool import Pool
from threading import Lock

pairs = []



def foo_merge(name, num, lock):
    global pairs
    lock.acquire()
    pairs.append((name, num))
    lock.release()


class TestTPool(unittest.TestCase):

    def test_merge_example(self):
        global pairs
        pairs = []
        lock = Lock()
        local_pairs = [('A', 2), ('B', 3), ('C', 4), ('D', 5)]
        params = []
        for p in local_pairs:
            param = p + (lock,)
            params.append(param)
        pool = Pool(max_num_of_threads=3, func=foo_merge, params_list=params)
        pool.run()
        self.assertListEqual(sorted(local_pairs), sorted(pairs))

    def test_alot_of_threads(self):
        global pairs
        pairs = []
        lock = Lock()
        local_pairs = []
        params = []
        for i in range(1000):
            p = (chr(ord('a') + i%26), i)
            local_pairs.append(p)
            param = p + (lock,)
            params.append(param)

        pool = Pool(max_num_of_threads=100, func=foo_merge, params_list=params)
        pool.run()
        self.assertListEqual(sorted(local_pairs), sorted(pairs))

    def test_few_threads(self):
        global pairs
        pairs = []
        lock = Lock()
        local_pairs = []
        params = []
        for i in range(1000):
            p = (chr(ord('a') + i%26), i)
            local_pairs.append(p)
            param = p + (lock,)
            params.append(param)

        pool = Pool(max_num_of_threads=3, func=foo_merge, params_list=params)
        pool.run()
        self.assertListEqual(sorted(local_pairs), sorted(pairs))


if __name__ == '__main__':
    unittest.main()