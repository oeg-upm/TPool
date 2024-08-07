# TPool

![tests](../../actions/workflows/python-package.yml/badge.svg)

Thread Pool for python 3 with multiple parameters. TPool implements a pool for threads supporting multiple arguments 


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



## Example
### Example 1 - functions
```
from TPool
from threading import Lock

pairs = []


def foo_merge(name, num, lock):
    global pairs
    lock.acquire()
    pairs.append((name, num))
    lock.release()


def example():
    global pairs
    pairs = []
    lock = Lock()
    local_pairs = [('A', 2), ('B', 3), ('C', 4), ('D', 5)]
    params = []
    for p in local_pairs:
        param = p + (lock,)
        params.append(param)
    pool = Pool(max_num_of_threads=3, func=foo_merge, params_list=params)
    pool.run()
    print pairs


if __name__ == "__main__":
    example()
```

### Example 2 - Classes
*This is a python3 example*
```
from multiprocessing import Process, Lock, Pipe
from TPool.TPool import Pool
import string


class Annotator:

    def __init__(self):
        self.gvar = "abc: "
        self.data = {
            "abc": 123,
        }

    def f(self, te, lock):
        print("te: "+te)
        lock.acquire()
        self.gvar += te+" --"
        self.data[te] = "Ok"
        lock.release()

    def test_threads(self):
        params_list = []
        lock = Lock()
        for i in range(100):
            s = str(i)+" "
            s += string.ascii_lowercase[i%26]
            s += string.ascii_lowercase[(i+1)%26]
            params_list.append((s, lock))
        pool = Pool(max_num_of_threads=10, func=self.f, params_list=params_list)
        pool.run()
        print("final: "+self.gvar)
        print(self.data)

a = Annotator()
a.test_threads()
```
