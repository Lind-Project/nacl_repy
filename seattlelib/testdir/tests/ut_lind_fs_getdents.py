import lind_test_server

from lind_fs_constants import *

lind_test_server._blank_fs_init()

# Let's add a few directories to the system and see if it works...
lind_test_server.mkdir_syscall('/bar',S_IRWXA)
lind_test_server.mkdir_syscall('/bar/baz',S_IRWXA)
lind_test_server.mkdir_syscall('/bar/bap',0)

# Create a new file...
fd = lind_test_server.open_syscall('/bar/bam',O_CREAT,0)
lind_test_server.close_syscall(fd)

# Read the root directory...
rootfd = lind_test_server.open_syscall('/',0,0)
val = lind_test_server.getdents_syscall(rootfd, 100)
assert (val==[(3, 'bar', DT_DIR, 24), (1, '..', DT_DIR, 24),\
  (1, '.', DT_DIR, 24)]), "Found: %s"%(str(val))

# Read the /bar directory...
barfd = lind_test_server.open_syscall('/bar',0,0)

# The buffer size is given small, only few entries are read. 
val = lind_test_server.getdents_syscall(barfd, 80)
assert (val == [(6, 'bam', DT_REG, 24), (4, 'baz', DT_DIR, 24),\
  (5, 'bap', DT_DIR, 24)]), "Found: %s"%(str(val))

# Again call on the same FD, should continue parsing the /bar directory.
val = lind_test_server.getdents_syscall(barfd, 80)
assert (val == [(1, '..', DT_DIR, 24), (3, '.', DT_DIR, 24)]),\
  "Found: %s"%(str(val))

lind_test_server.close_syscall(rootfd)
lind_test_server.close_syscall(barfd)
