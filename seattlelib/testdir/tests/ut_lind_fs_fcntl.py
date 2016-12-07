import lind_test_server
from emultimer import sleep
from lind_net_constants import *
from lind_fs_constants import *

lind_test_server._blank_fs_init()

SyscallError = lind_test_server.SyscallError

#create a file and socket descriptor...
sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
filefd = lind_test_server.open_syscall("/tmp", O_CREAT | O_EXCL, S_IRWXA)

#Set FD_CLOEXEC flag...
assert lind_test_server.fcntl_syscall(sockfd, F_SETFD, FD_CLOEXEC) == 0,\
  "F_SETFD failed..."

#Checking if the FD_CLOEXEC is set or not...
assert lind_test_server.fcntl_syscall(sockfd, F_GETFD) == 1, "F_GETFD failed."

#Reset FD_CLOEXEC flag...
#assert lind_test_server.fcntl_syscall(sockfd, F_SETFD, 0) == 0, "F_SETFD failed."

#Set some extra flags on file descriptor...
assert lind_test_server.fcntl_syscall(filefd, F_SETFL, O_RDONLY|O_NONBLOCK) == 0,\
  "F_SETFL failed."

#check if the flags are updated or not...
assert lind_test_server.fcntl_syscall(filefd, F_GETFL) == 2048, "F_GETFL failed."

lind_test_server.close_syscall(sockfd)
lind_test_server.close_syscall(filefd)
