import wrapped_lind_fs_calls as lind_fs_calls


from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_fs_calls._blank_fs_init()
myfd = lind_fs_calls.open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

myfd2 = lind_fs_calls.open_syscall('/foo',O_RDWR,S_IRWXA)

assert(myfd!= myfd2)

flags = 577
mode = 438
name = 'double_open_file'

#print "CM: failing double open here:"
myfd3 = lind_fs_calls.open_syscall(name, flags, mode)
lind_fs_calls.write_syscall(myfd3,'hi there')

myfd4 = lind_fs_calls.open_syscall(name, flags, mode)

assert(myfd3!=myfd4)
