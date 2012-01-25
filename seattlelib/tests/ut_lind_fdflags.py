import wrapped_lind_fs_calls as lind_fs_calls
from lind_fs_constants import *

lind_fs_calls._blank_fs_init()


myfd = lind_fs_calls.creat_syscall('/hello', S_IRWXA)

lind_fs_calls.close_syscall(myfd)

# Read only file descriptor opened
rdfd = lind_fs_calls.open_syscall('/hello', O_RDONLY, S_IRWXA)

try:
  # File written
  lind_fs_calls.write_syscall(rdfd, 'Hello everyone!')
except lind_fs_calls.SyscallError:
  # should be an error 
  pass
else:
  print "Error!   Should have been blocked from writing with O_RDONLY"

lind_fs_calls.lseek_syscall(rdfd, 0, SEEK_SET)

# should work...
lind_fs_calls.read_syscall(rdfd, 100)

lind_fs_calls.close_syscall(rdfd)

# Alternately

wrfd = lind_fs_calls.open_syscall('/hello', O_WRONLY, S_IRWXA)

try:
  # Can I read a write only file?
  lind_fs_calls.read_syscall(wrfd, 50)
except lind_fs_calls.SyscallError:
  # should be an error 
  pass
else:
  print "Error!   Should have been blocked from reading with O_WRONLY"

# should work
lind_fs_calls.write_syscall(wrfd, 'Hello everyone!')

lind_fs_calls.close_syscall(wrfd)
