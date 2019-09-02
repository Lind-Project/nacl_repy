from lind_fs_constants import *
import lind_test_server

lind_test_server._blank_fs_init()


myfd = lind_test_server.get_fs_call(-1,"creat_syscall")('/hello', S_IRWXA)

lind_test_server.get_fs_call(-1,"close_syscall")(myfd)

# Read only file descriptor opened
rdfd = lind_test_server.get_fs_call(-1,"open_syscall")('/hello', O_RDONLY, S_IRWXA)

try:
  # File written
  lind_test_server.get_fs_call(-1,"write_syscall")(rdfd, 'Hello everyone!')
except lind_test_server.SyscallError:
  # should be an error 
  pass
else:
  print "Error!   Should have been blocked from writing with O_RDONLY"

lind_test_server.get_fs_call(-1,"lseek_syscall")(rdfd, 0, SEEK_SET)

# should work...
lind_test_server.get_fs_call(-1,"read_syscall")(rdfd, 100)

lind_test_server.get_fs_call(-1,"close_syscall")(rdfd)

# Alternately

wrfd = lind_test_server.get_fs_call(-1,"open_syscall")('/hello', O_WRONLY, S_IRWXA)

try:
  # Can I read a write only file?
  lind_test_server.get_fs_call(-1,"read_syscall")(wrfd, 50)
except lind_test_server.SyscallError:
  # should be an error 
  pass
else:
  print "Error!   Should have been blocked from reading with O_WRONLY"

# should work
lind_test_server.get_fs_call(-1,"write_syscall")(wrfd, 'Hello everyone!')

lind_test_server.get_fs_call(-1,"close_syscall")(wrfd)
