import lind_test_server


from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_test_server._blank_fs_init()

myfd = lind_test_server.get_fscall_obj(-1).open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

# write should succeed
assert(lind_test_server.get_fscall_obj(-1).write_syscall(myfd,'hello') == 5)

# seek past the end
assert(lind_test_server.get_fscall_obj(-1).lseek_syscall(myfd,10,SEEK_SET) == 10)

# write should succeed again (past the end)
assert(lind_test_server.get_fscall_obj(-1).write_syscall(myfd,'yoyoyo') == 6)

# seek to the start
assert(lind_test_server.get_fscall_obj(-1).lseek_syscall(myfd,0,SEEK_SET) == 0)

# read 20 bytes but get 16 (hello\0\0\0\0\0yoyoyo)
assert(lind_test_server.get_fscall_obj(-1).read_syscall(myfd,20)=='hello\0\0\0\0\0yoyoyo')

lind_test_server.get_fscall_obj(-1).close_syscall(myfd)
