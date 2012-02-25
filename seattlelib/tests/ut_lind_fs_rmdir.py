import lind_test_server

from lind_fs_constants import *

# Let's add a few directories to the system and see if it works...
lind_test_server._blank_fs_init()

lind_test_server.mkdir_syscall('/bar',S_IRWXA)

lind_test_server.mkdir_syscall('/bar/baz',S_IRWXA)

lind_test_server.access_syscall('/bar/baz',F_OK)

# should not be able 
try:
  lind_test_server.rmdir_syscall('/bar')
except:
  pass
else:
  print 'could remove directory with items inside!!!'

lind_test_server.rmdir_syscall('/bar/baz')
try:
  lind_test_server.access_syscall('/bar/baz',F_OK)
except:
  pass
else:
  print 'error!   Directory exists after removal'



