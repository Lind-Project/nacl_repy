import lind_test_server

from lind_fs_constants import *

# Try to do dup2
lind_test_server._blank_fs_init()

(p1, p2) = lind_test_server.pipe_syscall()


assert(lind_test_server.write_syscall(p1, 'test') == 4)

assert(lind_test_server.read_syscall(p2, 2) == 'te')

# even though read 100, the nread will not exceed nwrite
assert(lind_test_server.read_syscall(p2, 100) == 'st')


# test exceed write will be discarded 
assert(lind_test_server.write_syscall(p1, 'A'*4096 + 'B'*4) == 4096)
assert(lind_test_server.read_syscall(p2, 4100) == 'A' * 4096)

stat_result = lind_test_server.fstat_syscall(p1)
inode = stat_result[1]

lind_test_server.close_syscall(p1)
lind_test_server.close_syscall(p2)

# after both fd of the pipe are closed, the inode should be deleted from inodetable
try:
  thisinode = lind_test_server.filesystemmetadata['inodetable'][inode]
except KeyError:
  pass
else:
  print('close pipe failed')
