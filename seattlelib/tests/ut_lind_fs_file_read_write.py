import lind_fs_calls

from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_fs_calls._blank_fs_init()

myfd = lind_fs_calls.open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

# write should succeed
assert(lind_fs_calls.write_syscall(myfd,'hello there!') == 12)

# seek to the beginning...
assert(lind_fs_calls.lseek_syscall(myfd,0,SEEK_SET) == 0)

# read the first 5 bytes (hello)
assert(lind_fs_calls.read_syscall(myfd,5)=='hello')

# change it to hello world!
assert(lind_fs_calls.write_syscall(myfd,' world')==6)

# seek to the beginning again...
assert(lind_fs_calls.lseek_syscall(myfd,0,SEEK_SET) == 0)

# and read it all...
assert(lind_fs_calls.read_syscall(myfd,100) == 'hello world!')

lind_fs_calls.close_syscall(myfd)
