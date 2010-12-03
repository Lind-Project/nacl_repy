#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks that the thread pool is properly
scaling when new tasks are added. This checks the 
up-scaling behavior.
"""

# Create a thread pool
tpool = ThreadPool() # Default, 1-4 threads, scaling_thres = 5

def noop():
  sleep(3)

# If we schedule 5, we should see 1 thread,
# If we schedule 10, we should see 2 threads,
# ..., up to 20, then we should see 4 threads
#
# Since the thread begins on a task once it starts,
# we actually need to schedule 6 tasks until the threads
# are exhausted.
for x in xrange(1,5):
  for t in xrange(6):
    tpool.add_task(noop)
  sleep(0.2)
  if tpool.threads() != x:
    print "We have added "+str(6*x)+" tasks, should have "+str(x)+" threads"
    print "Have: "+str(tpool.threads())
    print "Tasks: "+str(tpool.queued_tasks())


# Done
exitall()

