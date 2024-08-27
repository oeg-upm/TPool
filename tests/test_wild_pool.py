import logging
import unittest
from unittest.mock import MagicMock
import threading
import queue
from TPool import WildPool


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


if __name__ == '__main__':
    unittest.main()
