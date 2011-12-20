import lind_fs_calls

from lind_fs_constants import *

# Let's add a few directories to the system and see if it works...
lind_fs_calls._blank_fs_init()

lind_fs_calls.mkdir_syscall('/bar',S_IRWXA)

lind_fs_calls.mkdir_syscall('/bar/baz',S_IRWXA)

lind_fs_calls.mkdir_syscall('/bar/bap',0)

fd = lind_fs_calls.open_syscall('/bar/bam',O_CREAT,0)

lind_fs_calls.close_syscall(fd)

rootfd = lind_fs_calls.open_syscall('/',0,0)
print lind_fs_calls.getdents_syscall(rootfd, 10)

barfd = lind_fs_calls.open_syscall('/bar',0,0)
print lind_fs_calls.getdents_syscall(barfd,10)
print lind_fs_calls.getdents_syscall(barfd,1)
