import setuptools

with open("README.md", "r") as fh:
    long_description = """
    Thread Pool for python 2 with multiple parameters. 
Python2 include an undocumented thread pool which 
only accept functions with single arguments. TPool 
implements a pool for threads supporting multiple arguments 

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

    """

setuptools.setup(
    name="TPool",
    version="1.0",
    author="Ahmad Alobaid",
    author_email="aalobaid@fi.upm.es",
    description="Thread Pool for Python 2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oeg-upm/PPool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: System :: Operating System"
    ],
)