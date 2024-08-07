import threading
import logging
import time


class WildPool:

    def __init__(self, pool_size=5, timeout=0, worker_timeout=3, logger=None):
        """
        pool_size: int
        timeout: int in seconds
        worker_timeout: int in seconds
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
        Add thread to the pool.
        thread: The thread to be added to the pool
        timeout. This is optional. if it is None, then
        """
        d = {
            "thread": thread
        }
        if timeout > 0:
            d["timeout"] = timeout
        elif self.timeout > 0:
            d["timeout"] = self.timeout

        self.lock.acquire()
        self.bench.append(d)
        self.lock.release()
        self.start()

    def start(self):
        self.lock.acquire()
        wake_up = False
        if self.bench:
            self.logger.debug("Bench is not empty")
            if not self.worker or not self.worker.is_alive:
                wake_up = True
            else:
                wake_up = False
        else:
            self.logger.debug("Bench is empty")
        self.lock.release()
        if wake_up:
            self._create_worker()

    def _kick_dead_threads(self):
        """
        Remove threads which are already completed from the Pool so more threads can be added
        """
        # self.lock.acquire()
        tids = list(self.pool.keys())
        for tid in tids:
            t = self.pool[tid]
            if not t["thread"].is_alive():
                self.logger.debug(f"Removing thread {t} from the pool")
                del self.pool[tid]
                self.last_kill = time.time()
        # self.lock.release()

    def _kick_slow_threads(self):
        """
        Remove threads which exceeded the specified timeout from the Pool so more threads can be added
        """
        # self.lock.acquire()
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
        # self.lock.release()

    def _create_worker(self):
        """
        Spawn a new worker if there is no working running already
        """
        self.logger.debug("create worker")
        self.lock.acquire()
        if self.worker and self.worker.is_alive:
            self.logger.debug("The worker is already running")
        else:
            self.logger.debug("Spawning a new worker")
            self.worker = threading.Thread(target=self._worker_func)
            self.worker.start()
            self.logger.debug("worker is ran")
        self.lock.release()

    def _clean_pool(self):
        self._kick_dead_threads()
        self._kick_slow_threads()

    def _should_break(self):
        b = False
        if self.worker_timeout > 0 and self.last_kill:
            self.lock.acquire()
            elapsed = time.time() - self.last_kill
            if elapsed > self.worker_timeout:
                b = True
            self.lock.release()
        return b

    def _fill_the_pool(self):
        # self.lock.acquire()
        tids = self.pool.keys()
        num_vacancies = max(self.pool_size - len(tids), 0)
        num_mov = min(num_vacancies, len(self.bench))
        # self.logger.debug(f"num_vacancies: {num_vacancies}")
        # self.logger.debug(f"num_mov: {num_mov}")
        for _ in range(num_mov):
            tj = self.bench.pop(0)
            tid = tj["thread"].start()
            if "timeout" in tj:
                tj["start_time"] = time.time()
            self.pool[tid] = tj
        # self.lock.release()

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
        relax: float. Sleep number of seconds after each iteration. 0 means not waiting.
        """
        done = False
        while not done:
            self.lock.acquire()
            if len(self.pool) == len(self.bench) == 0:
                done = True
            self.lock.release()
            if relax > 0:
                time.sleep(relax)