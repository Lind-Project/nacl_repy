import wrapped_lind_fs_calls as lind_fs_calls


from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_fs_calls._blank_fs_init()
myfd = lind_fs_calls.open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

myfd2 = lind_fs_calls.open_syscall('/foo',O_RDWR,S_IRWXA)

assert(myfd!= myfd2)

flags = O_TRUNC | O_CREAT | O_RDWR
mode = 438   # 0666
name = 'double_open_file'

#print "CM: failing double open here:"
myfd3 = lind_fs_calls.open_syscall(name, flags, mode)
assert(lind_fs_calls.write_syscall(myfd3,'hi')==2)

myfd4 = lind_fs_calls.open_syscall(name, flags, mode)

# should still work
assert(lind_fs_calls.write_syscall(myfd3,'boo')==3)

# reading data should get \0\0boo
assert(lind_fs_calls.read_syscall(myfd4,10)=='\0\0boo')

