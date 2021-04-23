# TPool
[![Build Status](https://semaphoreci.com/api/v1/ahmad88me/tpool/branches/master/badge.svg)](https://semaphoreci.com/ahmad88me/tpool)
[![codecov](https://codecov.io/gh/oeg-upm/TPool/branch/master/graph/badge.svg)](https://codecov.io/gh/oeg-upm/TPool)

It supports py2 and py3

Thread Pool for python 2 (and 3) with multiple parameters. 
Python2 include an undocumented thread pool which 
only accept functions with single arguments. TPool 
implements a pool for threads supporting multiple arguments 


# Install
`pip install TPool`

### Why not PPool
If you want to have access to shared variables. But also
note that in Python (at least the cPython version)
include a global lock that it does not run multiple 
threads at the same time, but it is good enough if the 
bottle neck is disk IO or network. 

## Example
### Example 1 - functions
```
from TPool.TPool import Pool
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
