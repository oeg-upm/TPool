import threading
import logging
import queue


class WildPool:
    """
    A flexible thread pool for managing concurrent tasks.

    The `WildPool` class provides a thread pool that efficiently manages the execution of multiple threads
    concurrently. Unlike a sequential thread pool, `WildPool` does not guarantee the order of execution
    of tasks, making it particularly suited for scenarios where tasks are independent and can be processed
    in parallel without needing to adhere to a specific sequence.

    This thread pool is designed for high-concurrency environments such as messaging queues
    and daemons, where managing multiple background tasks simultaneously is crucial. By limiting
    the number of concurrent threads to a specified maximum (`pool_size`), `WildPool` ensures that
    system resources are used efficiently, preventing issues like resource exhaustion or system slowdown.

    Key features of `WildPool` include:

    - **Concurrency Management:** Manages a fixed number of threads, ensuring no more than the specified
      number of tasks run concurrently, which helps in maintaining optimal system performance.

    - **Non-Sequential Execution:** Tasks are executed as soon as resources are available, without
      guaranteeing any particular order, which is ideal for tasks that do not depend on each other.

    - **Automatic Cleanup:** Completed threads are automatically removed from the pool, freeing up resources
      for new tasks.

    - **Daemon-Friendly:** The pool is well-suited for daemon processes and long-running services where tasks
      need to be processed continuously in the background.

    :param pool_size: The maximum number of threads in the pool.
    :type pool_size: int
    :param logger: Optional custom logger. If not provided, a default logger will be used.
    :type logger: logging.Logger, optional
    """
    def __init__(self, pool_size=5, logger=None):
        """
        Initialize the WildPool with a specified pool size and an optional logger.

        The pool size determines the maximum number of threads that can run concurrently. If a custom logger
        is not provided, a default logger with a critical level of logging will be used. This pool is designed
        for environments where tasks need to be processed in parallel without the constraints of sequential
        execution order.

        :param pool_size: The maximum number of threads in the pool.
        :type pool_size: int, optional
        :param logger: An optional custom logger. If not provided, a default logger is used.
        :type logger: logging.Logger, optional
        """
        self.semaphore = threading.Semaphore(pool_size)
        self.pool_size = pool_size
        self.pool = dict()
        self.bench = queue.SimpleQueue()
        self.queue_lock = threading.Lock()
        self.worker_lock = threading.Lock()
        self.join_lock = threading.Lock()
        self.worker = None
        self.keep_going = True
        self._join_is_called = False
        if not logger:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.CRITICAL)
            ch = logging.NullHandler()
            logger.addHandler(ch)
        self.logger = logger

    def _should_keep_going(self):
        """
        Check whether the worker thread should continue running.

        :return: True if the worker should keep running, False otherwise.
        :rtype: bool
        """
        with self.worker_lock:
            keep_going = self.keep_going
        with self.join_lock:
            if keep_going and self._join_is_called and self.bench.empty():
                keep_going = False
        return keep_going

    def add_thread(self, thread: threading.Thread):
        """
        Add a thread to the pool to be managed and executed.

        :param thread: The thread to be added to the pool.
        :type thread: threading.Thread
        """
        self.bench.put(thread)

    def _run_in_capsule(self, thread):
        """
        Start and manage the lifecycle of a thread within the pool.

        This method starts the thread, adds it to the pool, waits for it to complete,
        and then releases the semaphore.

        :param thread: The thread to be managed.
        :type thread: threading.Thread
        """
        thread.start()
        tid = thread.ident
        with self.queue_lock:
            self.pool[tid] = thread
        thread.join()
        self.semaphore.release()

    def _start_capsule(self, thread):
        """
        Start a new thread capsule to run the provided thread.

        This method encapsulates the thread running logic in a separate thread,
        allowing it to be managed by the pool.

        :param thread: The thread to run in the capsule.
        :type thread: threading.Thread
        """
        th = threading.Thread(target=self._run_in_capsule, args=(thread,))
        th.start()

    def _kick_dead_threads(self):
        """
        Remove completed threads from the pool.

        This method checks all threads in the pool and removes any that have completed
        their execution, freeing up space for new threads.
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
        Start a worker thread if none is currently running.

        This method ensures that only one worker thread is running to manage
        the threads in the pool. If a worker thread is already running, it will not
        start a new one.
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
        """
        Start a thread capsule.

        This method starts a new thread capsule to execute the provided thread.
        If None is passed, nothing would happen. This is used to permit the stopping of the worker
         as None is sent instead of a thread to unblock the bench get method.

        :param thread: The thread to start in the capsule, or None.
        :type thread: threading.Thread or None
        """
        if thread:
            self._start_capsule(thread)
        else:
            self.logger.debug(f"TPool: None is passed to jump.")
            self.semaphore.release()  # otherwise, we will have a semaphore acquired without a release

    def _worker_func(self):
        """
        The main function for the worker thread.

        This function manages the execution of threads in the pool, ensuring that
        no more than the allowed number of threads are running simultaneously.
        It runs until the pool is instructed to stop.
        """
        while self._should_keep_going():
            self.semaphore.acquire()
            th = self.bench.get()
            self._jump_into_the_pool(thread=th)
            self._kick_dead_threads()
        self.logger.debug("TPool: The worker is terminated")

    def join(self):
        """
        Block until all queued tasks have been processed and the worker thread exits.

        This method initiates a graceful shutdown of the thread pool. It waits for all tasks
        currently in the queue (`bench`) to be consumed and processed. Once the queue is empty,
        the worker thread will terminate, and this method will return.

        If `join()` has already been called, subsequent calls will be ignored to prevent
        unintended side effects or redundant shutdown attempts.

        Internally, a `None` sentinel is enqueued to unblock the worker if it is waiting
        for tasks, allowing it to check for shutdown conditions and exit cleanly.

        Note:
            - `join()` and `stop()` are mutually exclusive; calling both may lead to undefined behavior.
            - After calling `join()`, no new tasks should be added to the pool.

        Usage Example:
            pool = WildPool(pool_size=4)
            for task in tasks:
                pool.add_thread(threading.Thread(target=task))
            pool.start_worker()
            pool.join()  # Waits until all tasks are done
        """
        with self.join_lock:
            if self._join_is_called:  # prevent duplicate calls to join
                return
            self._join_is_called = True
        self.add_thread(None)  # to release the blocked bench.get in the _worker_func
        if self.worker:
            if self.worker.is_alive():
                self.worker.join()
        for _ in range(self.pool_size):
            self.semaphore.acquire()
        for _ in range(self.pool_size):
            self.semaphore.release()

    def stop(self):
        """
        Stop the worker thread and release resources.

        This method gracefully shuts down the worker thread, ensuring that
        all running threads are completed and resources are cleaned up.
        """
        with self.join_lock:
            if self._join_is_called:  # prevent calling both stop and join
                return

        self.logger.debug("TPool: releasing resources ...")
        with self.worker_lock:
            if self.worker and self.worker.is_alive():
                self.keep_going = False
                worker_alive = True
            else:
                worker_alive = False
        self.bench.put(None)  # to release the block in the main loop in case the bench get is blocking
        self.logger.debug("TPool: waiting for the worker to join")
        if worker_alive:
            self.worker.join()
            self.logger.debug("TPool: the worker is joined")
        else:
            self.logger.debug("TPool: the worker is not running so join would be skipped")

    def __del__(self):
        """
        Destructor to ensure proper cleanup.

        This method ensures that the worker thread is stopped and all resources
        are released when the WildPool object is deleted.
        """
        self.stop()
