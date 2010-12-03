#pragma repy restrictions.default dylink.repy librepy.repy
"""
This method tries to destroy a thread pool.
It checks that we can do this.
"""

# Create a thread pool.
tpool = ThreadPool(min_threads=4,max_threads=4)

# Start the thread pool
tpool.start()
sleep(0.4)

# Check the threads are started
if tpool.threads() != 4:
  print "Should have started 4 threads!"

# Destroy the pool
tpool.destroy()
sleep(0.4)

# Check the threads
if tpool.threads() > 0:
  print "Should have destroyed all the threads!"

exitall()


