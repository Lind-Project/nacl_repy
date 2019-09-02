import lind_test_server


from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_test_server._blank_fs_init()

myfd = lind_test_server.get_fs_call(-1,"open_syscall")('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

# write should succeed
assert(lind_test_server.get_fs_call(-1,"write_syscall")(myfd,'hello there!') == 12)

# seek to the beginning...
assert(lind_test_server.get_fs_call(-1,"lseek_syscall")(myfd,0,SEEK_SET) == 0)

# read the first 5 bytes (hello)
assert(lind_test_server.get_fs_call(-1,"read_syscall")(myfd,5)=='hello')

# change it to hello world!
assert(lind_test_server.get_fs_call(-1,"write_syscall")(myfd,' world')==6)

# seek to the beginning again...
assert(lind_test_server.get_fs_call(-1,"lseek_syscall")(myfd,0,SEEK_SET) == 0)

# and read it all...
assert(lind_test_server.get_fs_call(-1,"read_syscall")(myfd,100) == 'hello world!')

lind_test_server.get_fs_call(-1,"close_syscall")(myfd)
