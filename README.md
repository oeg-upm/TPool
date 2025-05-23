# TPool

![tests](../../actions/workflows/python-package.yml/badge.svg)
[![docs](../../actions/workflows/sphinx-docs.yml/badge.svg)](https://oeg-upm.github.io/TPool/)
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
`WildPool` is the core component of TPool — a robust thread pool implementation that efficiently manages concurrent execution of independent tasks.

### WildPool 
`WildPool` is a flexible thread pool designed for managing concurrent tasks in non-sequential order.
It efficiently handles multiple threads, allowing different functions to run concurrently without guaranteeing the 
order of execution.
* **Use Case**: Perfect for handling diverse tasks in daemon processes (e.g., messaging
queues), where tasks need to be processed as soon as resources are available. 
* **Execution**: A worker thread manages the execution of threads, ensuring that the number of concurrent threads
does not exceed the specified `pool_size`. Threads are automatically removed from the pool upon completion.

###  Key Features
- **Concurrency Management**: Ensures that no more than a specified number of threads run concurrently (`pool_size`).
- **Non-Sequential Execution**: Tasks are executed as soon as resources are available — task order is not guaranteed.
- **Automatic Cleanup**: Threads are automatically removed from the pool after completion.
- **Daemon-Friendly**: Well-suited for background services and long-running daemons.
- **Graceful Shutdown**: Use `.join()` to wait for all tasks or `.stop()` to shut down manually.


## Example: Using WildPool 
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
        pool.start_worker()
        pool.join()
        print(self.data)


a = Example()
a.test_threads()

```


## Contributing 
Contributions are welcome! Please fork the repository and submit a pull request with your improvements or bug fixes. 

## License 
This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for details.
