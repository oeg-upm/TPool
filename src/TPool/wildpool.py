import threading
import logging
import time
import queue


class WildPool:
    """
    A pool for managing threads.

    :param pool_size: The maximum number of threads in the pool.
    :type pool_size: int
    :param timeout: The default timeout for threads if not specified.
    :type timeout: int
    :param logger: Optional custom logger. If not provided, a default logger will be used.
    :type logger: logging.Logger
    """
    def __init__(self, pool_size=5, logger=None):
        """
        pool_size: int
        timeout: int in seconds
        logger: The logger.
        """
        self.semaphore = threading.Semaphore(pool_size)
        self.pool_size = pool_size
        self.pool = dict()
        self.bench = queue.SimpleQueue()
        self.queue_lock = threading.Lock()
        self.worker_lock = threading.Lock()
        self.worker = None
        self.keep_going = True
        if not logger:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.CRITICAL)
            ch = logging.NullHandler()
            logger.addHandler(ch)
        self.logger = logger

    def _should_keep_going(self):
        with self.worker_lock:
            keep_going = self.keep_going
        return keep_going

    def add_thread(self, thread: threading.Thread):
        """
        Add a thread to the pool.

        :param thread: The thread to be added to the pool.
        :type thread: threading.Thread
        """
        self.bench.put(thread)

    def _run_in_capsule(self, thread):
        thread.start()
        tid = thread.ident
        with self.queue_lock:
            self.pool[tid] = thread
        thread.join()
        self.semaphore.release()

    def _start_capsule(self, thread):
        th = threading.Thread(target=self._run_in_capsule, args=(thread,))
        th.start()

    def _kick_dead_threads(self):
        """
        Remove threads which are already completed from the Pool so more threads can be added
        """
        with self.queue_lock:
            tids = list(self.pool.keys())
            for tid in tids:
                t = self.pool[tid]
                if not t.is_alive():
                    self.logger.debug(f"TPool: Removing thread {t} from the pool")
                    del self.pool[tid]

    def start_worker(self):
        """
        Spawn a new worker if there is no running one already
        """
        self.logger.debug("TPool: create worker")
        with self.worker_lock:
            if self.worker and self.worker.is_alive():
                self.logger.debug("TPool: The worker is already running")
            else:
                self.logger.debug("TPool: Spawning a new worker")
                self.worker = threading.Thread(target=self._worker_func)
                self.worker.start()
                self.logger.debug("TPool: worker is running")

    def _jump_into_the_pool(self, thread):
        if thread:
            self._start_capsule(thread)
        else:
            self.logger.debug(f"TPool: None is passed to jump.")

    def _worker_func(self):
        self.semaphore.acquire()  # This is not a typo. Because otherwise, n+1 will be running instead of n threads
        while self._should_keep_going():
            th = self.bench.get()
            self._jump_into_the_pool(thread=th)
            self._kick_dead_threads()
            self.semaphore.acquire()
        self.logger.debug("TPool: The worker is terminated")

    def stop(self):
        self.logger.debug("TPool: releasing resources ...")
        with self.worker_lock:
            if self.worker and self.worker.is_alive():
                self.keep_going = False
                worker_alive = True
            else:
                worker_alive = False
        self.bench.put(None)  # to release the block in the main loop in case the bench get is blocking
        try:
            # to release the semaphore block in case it was blocking. Extra releasing will cause the exception
            self.semaphore.release()
        except Exception as e:
            pass
        self.logger.debug("TPool: waiting for the worker to join")
        if worker_alive:
            self.worker.join()
            self.logger.debug("TPool: the worker is joined")
        else:
            self.logger.debug("TPool: the worker is not running so join would be skipped")

    def __del__(self):
        self.stop()
