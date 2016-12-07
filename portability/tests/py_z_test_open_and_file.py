from repyportability import *

try:
  open('hello','rextrajunk').close()
except ValueError:
  # for whatever reason, the major OSes don't care if you give extra letters
  # after the mode string when calling open.   Our implementation does...
  pass
else:
  print "open implementation seems to be built-in '"+str(open)+"'"


try:
  file('hello','rextrajunk').close()
except ValueError:
  # for whatever reason, the major OSes don't care if you give extra letters
  # after the mode string when calling open.   Our implementation does...
  pass
else:
  print "file implementation seems to be built-in '"+str(file)+"'"
