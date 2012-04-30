import lind_test_server

from emultimer import createthread as createthread
from emulmisc import getruntime as getruntime
from time import sleep
from lind_net_constants import AF_INET, SOCK_STREAM, SHUT_RDWR
from lind_fs_constants import O_CREAT, O_EXCL, O_RDWR, S_IRWXA

SyscallError = lind_test_server.SyscallError

# Try read / write of a file and see if it works...
lind_test_server._blank_fs_init()

myfd = lind_test_server.open_syscall('/foo',O_CREAT | O_EXCL | O_RDWR,S_IRWXA)

# write should succeed
assert(lind_test_server.write_syscall(myfd,'hello there!') == 12)


# I'll listen, accept, and connect...
serversockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)
clientsockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)


# bind to a socket
assert lind_test_server.bind_syscall(serversockfd, '127.0.0.1', 50431) == 0
assert lind_test_server.listen_syscall(serversockfd, 10) == 0


def do_server():
    sleep(0.1)
    
    newsocketfd = lind_test_server.accept_syscall(serversockfd)
    fd = newsocketfd[2]
    
    start = lind_test_server.getruntime()
    ret = lind_test_server.select_syscall(20, [myfd, fd],[],[], 0.00, nonblocking=True)
    finish = lind_test_server.getruntime()
    assert myfd in ret[1], "File should always be ready for writing"
    assert not fd in ret[1], "socket should not be ready yet!"
    assert (finish - start) < 0.1, "Non-blocking call to a long time!"

    start = lind_test_server.getruntime()
    ret =  lind_test_server.select_syscall(20, [fd],[],[], 1.0)
    finish =  lind_test_server.getruntime()
    assert ret[0] == 0, "Should not have any results here."
    assert 1.0 < (finish - start) < 1.5 , "One second sleep was not within time window." 

    start = lind_test_server.getruntime()
    ret = lind_test_server.select_syscall(20, [fd],[],[], 0.0, notimer=True)
    finish = lind_test_server.getruntime()
    assert fd in ret[1], "Expecting fd now"
    assert 1.8 < (finish - start) < 3, "Did not correcly sleep for remaining time"
    
    sleep(0.1)
    
    ret = lind_test_server.select_syscall(20, [myfd, fd],[myfd],[], 0.10)
    print ret
    sleep(0.1)
    try:
      lind_test_server.select_syscall(20, [fd],[fd],[], 0.10)
    except AssertionError:
      pass
    lind_test_server.setshutdown_syscall(fd, SHUT_RDWR)

createthread(do_server)


# should be okay...
assert lind_test_server.connect_syscall(clientsockfd, '127.0.0.1', 50431) == 0
sleep(3.0)

try:
  for i in xrange(0,100):
    sleep(0.1)

    assert lind_test_server.send_syscall(clientsockfd, "test", 0),"A send failed"
except lind_test_server.SocketClosedRemote, e:
  pass

