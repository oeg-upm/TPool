import unittest
from unittest.mock import patch, MagicMock
import threading
import time
import logging

from TPool import WildPool

class TestWildPool(unittest.TestCase):

    def setUp(self):
        self.pool_size = 5
        self.timeout = 2
        self.worker_timeout = 3

        logger = None
        # logger = logging.getLogger('WildPool')
        # logger.setLevel(logging.DEBUG)
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.DEBUG)
        # logger.addHandler(ch)

        self.wp = WildPool(pool_size=self.pool_size, timeout=self.timeout, worker_timeout=self.worker_timeout,
                           logger=logger)
        # # self.wp.logger.setLevel(logging.CRITICAL)  # Suppress logging for the tests
        # self.wp.logger.setLevel(logging.DEBUG)  # Suppress logging for the tests


    @patch('threading.Thread')
    def test_add_thread(self, MockThread):
        thread = MockThread()
        self.wp.add_thread(thread, timeout=5)
        self.assertEqual(len(self.wp.bench), 1)
        self.assertEqual(self.wp.bench[0]['thread'], thread)
        self.assertEqual(self.wp.bench[0]['timeout'], 5)

    @patch('time.time', side_effect=[10, 10, 10])
    def test_kick_dead_threads(self, mock_time):
        thread = MagicMock()
        thread.is_alive.return_value = False
        self.wp.pool['thread_id2'] = {'thread': thread}
        self.wp._kick_dead_threads()
        self.assertEqual(len(self.wp.pool), 0)
        self.assertEqual(self.wp.last_kill, 10)

    @patch('time.time', side_effect=[19, 19, 19])
    def test_kick_slow_threads(self, mock_time):
        thread = MagicMock()
        thread.is_alive.return_value = True
        self.wp.pool['thread_id1'] = {'thread': thread, 'timeout': 5, 'start_time': 0}
        self.wp._kick_slow_threads()
        self.assertEqual(len(self.wp.pool), 0)
        self.assertEqual(self.wp.last_kill, 19)
        thread.kill.assert_called_once()

    @patch('threading.Thread')
    def test_create_worker(self, MockThread):
        mock_thread = MockThread()
        self.wp.worker = None
        self.wp.bench = [mock_thread]
        self.wp._create_worker()
        mock_thread.start.assert_called_once()

    @patch('time.time', side_effect=[0, 1])
    def test_fill_the_pool(self, mock_time):
        thread = MagicMock()
        thread.start.return_value = 'thread_id'
        self.wp.bench = [{'thread': thread, 'timeout': 5}]
        self.wp._fill_the_pool()
        self.assertEqual(len(self.wp.pool), 1)
        self.assertIn('thread_id', self.wp.pool)
        self.assertEqual(self.wp.pool['thread_id']['thread'], thread)
        self.assertEqual(self.wp.pool['thread_id']['timeout'], 5)
        self.assertEqual(self.wp.pool['thread_id']['start_time'], 0)
        self.assertEqual(len(self.wp.bench), 0)

if __name__ == '__main__':
    unittest.main()
