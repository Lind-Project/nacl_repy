import lind_test_server

from lind_fs_constants import *

# Try to do dup2
lind_test_server._blank_fs_init()

flags = O_TRUNC | O_CREAT | O_RDWR
mode = 438   # 0666
name = 'double_open_file'

myfd = lind_test_server.open_syscall(name, flags, mode)
assert(lind_test_server.write_syscall(myfd,'hi')==2)

# duplicate the file descriptor...
myfd2 = lind_test_server.dup_syscall(myfd)

assert(myfd != myfd2)

# this should actually be essentially a no-op.   It closes myfd+1 and sets it
# to be the same as the current fd (which was done by the prior call)
myfd3 = lind_test_server.dup_syscall(myfd)

# they should be different fds...
assert(myfd != myfd3 and myfd2 != myfd3)

# we don't need all three
lind_test_server.close_syscall(myfd3)

# should be at the same place...
assert(lind_test_server.lseek_syscall(myfd,0,SEEK_CUR) == 
       lind_test_server.lseek_syscall(myfd2,0,SEEK_CUR))

# write some data to move the first position
assert(lind_test_server.write_syscall(myfd,'yo')==2)

# _still_ should be at the same place...
assert(lind_test_server.lseek_syscall(myfd,0,SEEK_CUR) == 
       lind_test_server.lseek_syscall(myfd2,0,SEEK_CUR))

# reset the position within the file
lind_test_server.lseek_syscall(myfd2,0,SEEK_SET)

# read from the other fd
assert(lind_test_server.read_syscall(myfd,10)=='hiyo')

# close one fd
lind_test_server.close_syscall(myfd)

# the other should still work...
assert(lind_test_server.write_syscall(myfd2,'raar')==4)
lind_test_server.lseek_syscall(myfd2,0,SEEK_SET)
assert(lind_test_server.read_syscall(myfd2,10)=='hiyoraar')

lind_test_server.close_syscall(myfd2)
