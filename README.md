# TPool

![tests](../../actions/workflows/python-package.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/TPool.svg?kill-cache=1)](https://badge.fury.io/py/TPool)

Thread Pool for python 3 with multiple parameters. TPool implements a pool for threads supporting multiple arguments 

The documentation is available [here](https://oeg-upm.github.io/TPool/)

# Install
```
pip install TPool
```

# Run Tests
```
python -m unittest discover
```




# Thread Pools
This package offer two different thread pools: `SeqPool` and `WildPool`.

## SeqPool
This pool is meant for a predefined set of input of the same function (called `target`).
It expects the function that you would like to run in parallel and the list of arguments.
So, it would create multiple threads of the same function but with a different output. 
The pool make sure to only run `pool_size` number of threads at max. 

## WildPool
This is a more flexible pool which supports different threads with different
functions and it also supports a timeout. It has a worker thread which spawn the
the different threads until the `pool_size` is met. One a thread is finished
or reached the timeout time, it would be killed and removed from the pool.
If the worker is idel for `work_idel`


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
