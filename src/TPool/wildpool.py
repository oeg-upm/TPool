import threading
import logging
import time


class WildPool:
    """
    A pool for managing threads.

    :param pool_size: The maximum number of threads in the pool.
    :type pool_size: int
    :param timeout: The default timeout for threads if not specified.
    :type timeout: int
    :param worker_timeout: The idle timeout for the worker.
    :type worker_timeout: int
    :param logger: Optional custom logger. If not provided, a default logger will be used.
    :type logger: logging.Logger
    """
    def __init__(self, pool_size=5, timeout=0, worker_timeout=3, logger=None):
        """
        pool_size: int
        timeout: int in seconds
        worker_timeout: int in seconds
        logger: The logger.
        """
        self.pool_size = pool_size
        self.pool = dict()
        self.bench = []
        self.lock = threading.Lock()
        self.worker = None
        self.timeout = timeout
        self.worker_timeout = worker_timeout
        self.last_kill = None
        if not logger:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.CRITICAL)
            # create console handler and set level to debug
            ch = logging.NullHandler()
            logger.addHandler(ch)
        self.logger = logger

    def add_thread(self, thread: threading.Thread, timeout=0):
        """
        Add a thread to the pool.

        :param thread: The thread to be added to the pool.
        :type thread: threading.Thread
        :param timeout: The timeout for the thread. If not specified, the default pool timeout will be used.
        :type timeout: int
        """
        d = {
            "thread": thread
        }
        if timeout > 0:
            d["timeout"] = timeout
        elif self.timeout > 0:
            d["timeout"] = self.timeout

        with self.lock:
            self.bench.append(d)
        self.start()

    def start(self):
        """
        Start the worker if there are threads in the bench and no worker is currently running.
        """
        with self.lock:
            wake_up = False
            if self.bench:
                self.logger.debug("Bench is not empty")
                if not self.worker or not self.worker.is_alive:
                    wake_up = True
                else:
                    wake_up = False
            else:
                self.logger.debug("Bench is empty")
        if wake_up:
            self._create_worker()

    def _kick_dead_threads(self):
        """
        Remove threads which are already completed from the Pool so more threads can be added
        """
        tids = list(self.pool.keys())
        for tid in tids:
            t = self.pool[tid]
            if not t["thread"].is_alive():
                self.logger.debug(f"Removing thread {t} from the pool")
                del self.pool[tid]
                self.last_kill = time.time()

    def _kick_slow_threads(self):
        """
        Remove threads which exceeded the specified timeout from the Pool so more threads can be added
        """
        tids =list(self.pool.keys())
        for tid in tids:
            t = self.pool[tid]
            if "timeout" in t:
                elapsed = time.time() - t["start_time"]
                if elapsed > t["timeout"]:
                    self.logger.debug(f"Killing thread {t} and removing it from the pool")
                    t["thread"].kill()
                    self.last_kill = time.time()
                    del self.pool[tid]

    def _create_worker(self):
        """
        Spawn a new worker if there is no working running already
        """
        self.logger.debug("create worker")
        with self.lock:
            if self.worker and self.worker.is_alive:
                self.logger.debug("The worker is already running")
            else:
                self.logger.debug("Spawning a new worker")
                self.worker = threading.Thread(target=self._worker_func)
                self.worker.start()
                self.logger.debug("worker is ran")

    def _clean_pool(self):
        self._kick_dead_threads()
        self._kick_slow_threads()

    def _should_break(self):
        b = False
        if self.worker_timeout > 0 and self.last_kill:
            with self.lock:
                elapsed = time.time() - self.last_kill
                if elapsed > self.worker_timeout:
                    b = True
        return b

    def _fill_the_pool(self):
        tids = self.pool.keys()
        num_vacancies = max(self.pool_size - len(tids), 0)
        num_mov = min(num_vacancies, len(self.bench))
        for _ in range(num_mov):
            tj = self.bench.pop(0)
            tid = tj["thread"].start()
            if "timeout" in tj:
                tj["start_time"] = time.time()
            self.pool[tid] = tj

    def _worker_func(self):
        while True:
            self.lock.acquire()
            self._clean_pool()
            self._fill_the_pool()
            self.lock.release()
            if self._should_break():
                break

    def join(self, relax=0.1):
        """
        Wait for all threads in the pool and bench to complete.

        :param relax: Sleep time in seconds between checks. 0 means no waiting.
        :type relax: float
        """
        done = False
        while not done:
            with self.lock:
                if len(self.pool) == len(self.bench) == 0:
                    done = True
            if relax > 0:
                time.sleep(relax)