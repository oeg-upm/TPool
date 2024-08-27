# TPool

[![docs](https://github.com/oeg-upm/TPool/actions/workflows/sphinx-docs.yml/badge.svg)](https://oeg-upm.github.io/TPool/)
[![PyPI version](https://badge.fury.io/py/TPool.svg)](https://badge.fury.io/py/TPool)

TPool is a Python 3 library that provides flexible and powerful thread pools designed for handling concurrent tasks with ease. It supports the execution of multiple threads with various configurations and allows for both sequential and non-sequential task management.


The documentation is available [here](https://oeg-upm.github.io/TPool/)


## Install
```
pip install TPool
```

## Run Tests
```
python -m unittest discover
```


## Thread Pools Overview 
TPool offers two distinct types of thread pools to cater to different use cases:

### SeqPool
`SeqPool` is designed for scenarios where you have a predefined set of inputs and wish to run the same function
(`target`) across multiple threads. It ensures that no more than a specified number (`pool_size`) of threads are
running concurrently. 
* **Use Case**: Ideal for batch processing tasks where each task can run in parallel, but the order of execution
matters. 
* **Execution**: The pool executes the provided function with different arguments, managing the concurrency to avoid 
overwhelming system resources. 

### WildPool 
`WildPool` is a flexible thread pool designed for managing concurrent tasks in non-sequential order.
It efficiently handles multiple threads, allowing different functions to run concurrently without guaranteeing the 
order of execution.
* **Use Case**: Perfect for handling diverse tasks in daemon processes (e.g., messaging
queues), where tasks need to be processed as soon as resources are available. 
* **Execution**: A worker thread manages the execution of threads, ensuring that the number of concurrent threads
does not exceed the specified `pool_size`. Threads are automatically removed from the pool upon completion.

#### Detailed Description of WildPool:
* **Concurrency Management**: `WildPool` manages a fixed number of threads, ensuring no more than the specified
number of tasks run concurrently, which helps in maintaining optimal system performance. 
* **Non-Sequential Execution**: Tasks are executed as soon as resources are available, without guaranteeing any 
particular order, making it ideal for tasks that do not depend on each other. 
* **Automatic Cleanup**: Completed threads are automatically removed from the pool, freeing up resources for new tasks. 
* **Daemon-Friendly**: The pool is well-suited for daemon processes and long-running services where tasks need to be
processed continuously in the background.



## Examples
### Example 1: Wild Pool 
```
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

```

### Example 2: Sequential Pool 
```
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

```

## Contributing 
Contributions are welcome! Please fork the repository and submit a pull request with your improvements or bug fixes. 

## License 
This project is licensed under the Apache License. See the LICENSE file for details.
