"""
Author: Armon Dadgar
Description:
    This test checks the behavior of dy_dispatch_module and makes sure it is sane.

Expected Output:
    You should see 'Steps (i/4)' where i is 1..4
"""

# We should alway have HAS_DYLINK = True
if not HAS_DYLINK:
  print "We don't have Dylink available!"


# Switch our behavior on the callfunc
if callfunc == "initialize":
  print "Step (1/4)"

  # Set the next module to be ourself
  callargs = ["test_dylink_dispatch"]

  # Set the callfunc to "check" now
  callfunc = "check"

# This checks that the dispatch worked
elif callfunc == "check":
  print "Step (2/4)"

# This tests that exit is being propogated
elif callfunc == "exit":
  # Update the callfunc again
  callfunc = "check_exit"

  print "Step (3/4)"

# Check the exit propogates
elif callfunc == "check_exit":
  print "Step (4/4)"

# Catch any weird behavior
else:
  print "Error! Unknown callfunc!"



# Always do a dispatch
did_run = dy_dispatch_module()

# If the callfunc doesn't have "check" in it, then did_run should be true.
# This is because the module directly after dylink should always evaluate
# itself again.
if "check" not in callfunc and not did_run:
  print "Did not perform a recursive evaluation!"


