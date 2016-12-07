"""
Times the length of time taken to do a
specified number of calls to noop()
"""

# Get the number of calls
num_calls = int(callargs[0])

# Get the start time
start = getruntime()

for x in xrange(num_calls):
  try:
    noop()
  except:
    pass

end = getruntime()

# Output the time
log("Encasement Start:",start,"End:",end,"Time:",(end-start),"\n")

