import logging
import unittest
from unittest.mock import MagicMock
import threading
import queue
from TPool import WildPool
import time


class TestWildPool(unittest.TestCase):

    def setUp(self):
        self.pool_size = 5
        logger = None
        # logger = logging.getLogger('WildPool')
        # logger.setLevel(logging.DEBUG)
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.DEBUG)
        # logger.addHandler(ch)
        self.wp = WildPool(pool_size=self.pool_size, logger=logger)

    def test_add_thread(self):
        thread = MagicMock(spec=threading.Thread)
        self.wp.add_thread(thread)
        self.assertFalse(self.wp.bench.empty())
        self.assertEqual(self.wp.bench.get(), thread)

    def test_kick_dead_threads(self):
        thread = MagicMock(spec=threading.Thread)
        thread.is_alive.return_value = False
        self.wp.pool['thread_id2'] = thread
        self.wp._kick_dead_threads()
        self.assertEqual(len(self.wp.pool), 0)

    def test_start_worker(self):
        thread = MagicMock(spec=threading.Thread)
        self.wp.add_thread(thread)
        self.wp.start_worker()
        self.assertTrue(self.wp.worker.is_alive())
        self.wp.stop()

    def test_all_threads_complete_before_join_returns(self):
        completed = []
        lock = threading.Lock()

        def task(n):
            time.sleep(0.1)  # simulate work
            with lock:
                completed.append(n)

        pool = WildPool(pool_size=3)
        for i in range(5):
            pool.add_thread(threading.Thread(target=task, args=(i,)))

        pool.start_worker()
        pool.join()

        # Check that all tasks finished
        self.assertEqual(len(completed), 5)
        self.assertCountEqual(completed, list(range(5)))

    def test_join_waits_for_running_threads(self):
        state = {"started": 0, "finished": 0}
        lock = threading.Lock()

        def task():
            with lock:
                state["started"] += 1
            time.sleep(0.2)
            with lock:
                state["finished"] += 1

        pool = WildPool(pool_size=2)
        for _ in range(4):
            pool.add_thread(threading.Thread(target=task))

        pool.start_worker()

        # Call join before all threads are done
        t0 = time.time()
        pool.join()
        t1 = time.time()

        duration = t1 - t0

        # All 4 threads should have run
        self.assertEqual(state["finished"], 4)
        self.assertGreaterEqual(duration, 0.4)  # Two waves of 2 threads

    def test_join_is_idempotent(self):
        result = []

        def task():
            time.sleep(0.05)
            result.append("done")

        pool = WildPool(pool_size=2)
        for _ in range(2):
            pool.add_thread(threading.Thread(target=task))

        pool.start_worker()
        pool.join()
        pool.join()  # second call should be safe
        self.assertEqual(result.count("done"), 2)


if __name__ == '__main__':
    unittest.main()
