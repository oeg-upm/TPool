
Seq Pool Example 1
==================

.. code-block:: python

	from TPool import SeqPool
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
	    pool = SeqPool(pool_size=3, target=foo_merge, params_list=params)
	    pool.run()
	    print(pairs)
	
	
	if __name__ == "__main__":
	    example()


