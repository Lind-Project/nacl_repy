import lind_test_server


from lind_fs_constants import *

# Try read / write of a file and see if it works...
lind_test_server._blank_fs_init()
myfd = lind_test_server.open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

myfd2 = lind_test_server.open_syscall('/foo',O_RDWR,S_IRWXA)

assert(myfd!= myfd2)

flags = O_TRUNC | O_CREAT | O_RDWR
mode = 438   # 0666
name = 'double_open_file'

#print "CM: failing double open here:"
myfd3 = lind_test_server.open_syscall(name, flags, mode)
assert(lind_test_server.write_syscall(myfd3,'hi')==2)

myfd4 = lind_test_server.open_syscall(name, flags, mode)

# should still work
assert(lind_test_server.write_syscall(myfd3,'boo')==3)

# reading data should get \0\0boo
assert(lind_test_server.read_syscall(myfd4,10)=='\0\0boo')

