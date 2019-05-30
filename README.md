# TPool
[![Build Status](https://semaphoreci.com/api/v1/ahmad88me/tpool/branches/master/badge.svg)](https://semaphoreci.com/ahmad88me/tpool)
[![codecov](https://codecov.io/gh/oeg-upm/TPool/branch/master/graph/badge.svg)](https://codecov.io/gh/oeg-upm/TPool)

Thread Pool for python 2 with multiple parameters. 
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
```
from TPool import Pool
from threading import Lock

pairs = []


def foo_merge(name, num, lock):
    global pairs
    lock.acquire()
    pairs.append((name, num))
    lock.release()

def example(self):
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
   
example()
```
