import wrapped_lind_fs_calls as lind_fs_calls


from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_fs_calls._blank_fs_init()

myfd = lind_fs_calls.open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

# write should succeed
assert(lind_fs_calls.write_syscall(myfd,'hello') == 5)

# seek past the end
assert(lind_fs_calls.lseek_syscall(myfd,10,SEEK_SET) == 10)

# write should succeed again (past the end)
assert(lind_fs_calls.write_syscall(myfd,'yoyoyo') == 6)

# seek to the start
assert(lind_fs_calls.lseek_syscall(myfd,0,SEEK_SET) == 0)

# read 20 bytes but get 16 (hello\0\0\0\0\0yoyoyo)
assert(lind_fs_calls.read_syscall(myfd,20)=='hello\0\0\0\0\0yoyoyo')

lind_fs_calls.close_syscall(myfd)
