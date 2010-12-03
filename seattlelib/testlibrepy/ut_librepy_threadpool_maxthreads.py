#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks that the maximum threads are started
when there are enough tasks queued for the thread pool.
"""

# Construct a thread pool
tpool = ThreadPool() # Default, 1-4 threads, scaling_thres = 5

def noop():
  sleep(1)

# Get the idle thread count
idle_threads = libthread.active_threads()

# Schedule 4*10 tasks, this should force max, threads.
# Also, we can check that no extra threads are started.
for x in xrange(40):
  tpool.add_task(noop)

# Wait for the thread pool to start up
sleep(0.2)

# Check the threads
started_threads = libthread.active_threads()

# Check the thread counts
if idle_threads + 4 != started_threads:
  print "We should have started 4 threads!"

# Check what the pool reports
if tpool.threads() != 4:
  print "Pool does not report 4 threads!"

# Done
exitall()

