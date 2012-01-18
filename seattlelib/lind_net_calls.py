"""
  Author: Justin Cappos
  Module: Network calls for Lind.   This is essentially POSIX written in
          Repy V2.   

  Start Date: January 14th, 2012

  My goal is to write a simple and relatively accurate implementation of POSIX
  in Repy V2.   This module contains most of the network calls.   A lind
  client can execute those calls and they will be mapped into my Repy V2 
  code where I will more or less faithfully execute them.   Since Repy V2
  does not support some of the socket options, I will fake (or ignore) these.
  There will also be a few minor parts of the implementation that might 
  need to interact with the file system portion of the API.   This will be 
  for things like getting file descriptors / socket descriptors.
  For Unix domain sockets, etc. we'll use loopback sockets.

  Much like the fs API, rather than do all of the struct packing, etc. here, I 
  will do it elsewhere.  This will allow me to test this in Python / Repy
  without unpacking / repacking.

"""



# Since Repy does not have a concept of descriptors or binding before 
# connecting, we will fake all of this.   I will determine the usable ports
# and then choose from them when it's unspecified.


# I'm not overly concerned about efficiency right now.   I'm more worried
# about correctness.   As a result, I'm not going to optimize anything yet.
#

# I'll keep a little metadata for each socket descriptor (in the file
# descriptor table).   It will look like this:
# {'domain': AF_INET, 'type': SOCK_STREAM, 'protocol': IPPROTO_TCP, 
#  'localip': '1.2.3.4', 'localport':12345, 'remoteip': '5.6.7.8', 
#  'remoteport':6789, 'socketobjectid':5, 'mode':S_IFSOCK | 0666, 'options':0,
#  'state':NOTCONNECTED}
#
# To make dup and dup2 work correctly, I'll keep a socketobjecttable instead
# of including them in the filedescriptortable...
#



# States for my own internal use:

NOTCONNECTED = 128
CONNECTED = 256
LISTEN = 512

# contains open file descriptor information... (keyed by fd)
# filedescriptortable = {}

# contains socket objects... (keyed by id)   Mostly done for dup / dup2
socketobjecttable = {}

# This is raised to return an error...   It's the same as for the file 
# system calls
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""







######################   Generic Helper functions   #########################


# a list of udp ports already used.   This is used to help us figure out a good
# available port
usedudpportsset = set([])
# these are the ports we possibly could use...
usableudpportsset = getresources()[0]['messport'].copy()

# the same for tcp...
usedtcpportsset = set([])
usabletcpportsset = getresources()[0]['connport'].copy()


# We need a helper that gets an available port...
# Get the first unused port and return it...
def _get_available_udp_port():
  for port in usableudpportsset:
    if port not in usedudpportsset:
      return port
  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_udp_port","ENOBUFS","No UDP port available")



# A verbatim copy of the above...   It's so simple, I guess it's okay to do so
def _get_available_tcp_port():
  for port in usabletcpportsset:
    if port not in usedtcpportsset:
      return port
  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_tcp_port","ENOBUFS","No TCP port available")



STARTINGSOCKOBJID = 0
MAXSOCKOBJID = 1024

# get an available socket object ID...
def _get_next_socketobjid():
  for sockobjid in range(STARTINGSOCKOBJID,MAXSOCKOBJID):
    if not sockobjid in socketobjecttable:
      return sockobjid

  raise SyscallError("_get_next_socketobjid","ENOBUFS","Insufficient buffer space is available to create a new socketobjid")

def _insert_into_socketobjecttable(socketobj):
  nextentry = _get_next_socketobjid()
  socketobjecttable[nextentry] = socketobj
  return nextentry



#################### The actual system calls...   #############################



##### SOCKET  #####


# A private helper that initializes a socket given validated arguments.
def _socket_initializer(domain,socktype,protocol):
  # get a file descriptor
  newfd = lind_fs_calls._get_next_fd()

  # NOTE: I'm intentionally omitting the 'inode' field.  This will make most
  # of the calls I did not change break.
  filedescriptortable[newfd] = {
      'mode':S_IFSOCK|0666, # set rw-rw-rw- perms too. This is what POSIX does.
      'domain':domain,
      'type':socktype,      # I'm using this name because it's used by POSIX.
      'protocol':protocol,
      # BUG: I may need to handle the global setting of options here...
      'options':0,          # start with all options off...
      'state':NOTCONNECTED, # we start without any connection
# We don't set the ip / ports or socketobjectid because they are unknown now.
  }

  return newfd
      


# int socket(int domain, int type, int protocol);
def socket_syscall(domain, socktype, protocol):
  """ 
    http://linux.die.net/man/2/socket
  """

  # this code is basically one huge case statement by domain

  # okay, let's do different things depending on the domain...
  if domain == PF_INET:

    
    if socktype == SOCK_STREAM:
      # If is 0, set to default (IPPROTO_TCP)
      if protocol == 0:
        protocol = IPPROTO_TCP


      if protocol != IPPROTO_TCP:
        raise UnimplementedError("The only SOCK_STREAM implemented is TCP.  Unknown protocol:"+str(protocol))
      
      return _socket_initializer(domain,socktype,protocol)


    # datagram!
    elif socktype == SOCK_DGRAM:
      # If is 0, set to default (IPPROTO_UDP)
      if protocol == 0:
        protocol = IPPROTO_UDP

      if protocol != IPPROTO_UDP:
        raise UnimplementedError("The only SOCK_DGRAM implemented is UDP.  Unknown protocol:"+str(protocol))
    
      return _socket_initializer(domain,socktype,protocol)
    else:
      raise UnimplementedError("Unimplemented sockettype: "+str(socktype))

  else:
    raise UnimplementedError("Unimplemented domain: "+str(domain))









##### BIND  #####


def bind_syscall(fd,localip,localport):
  """ 
    http://linux.die.net/man/2/bind
  """

  if fd not in filedescriptortable:
    raise SyscallError("bind_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("bind_syscall","ENOTSOCK","The descriptor is not a socket.")

  # Am I already bound?
  if 'localip' in filedescriptortable[fd]:
    raise SyscallError('bind_syscall','EINVAL',"The socket is already bound to an address")


  # Is someone else already bound to this address?
  for otherfd in filedescriptortable:
    # skip ours
    if fd == otherfd:
      continue

    # if not a socket, skip it...
    if 'domain' not in filedescriptortable[otherfd]:
      continue

    # if the protocol / domain/ type differ, ignore
    if filedescriptortable[otherfd]['domain'] != filedescriptortable[fd]['domain'] or filedescriptortable[otherfd]['type'] != filedescriptortable[fd]['type'] or filedescriptortable[otherfd]['protocol'] != filedescriptortable[fd]['protocol']:
      continue

    # if they are already bound to this address / port
    if 'localip' in filedescriptortable[otherfd] and filedescriptortable[otherfd]['localip'] == localip and filedescriptortable[otherfd]['localport'] == localport:
      # is SO_REUSEPORT in effect on both? I think everyone has to set 
      # SO_REUSEADDR
      if filedescriptortable[fd]['options'] & filedescriptortable[otherfd]['options'] & SO_REUSEPORT == SO_REUSEPORT:
        # all is well, continue...
        pass
      else:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")

  # BUG (?): hmm, how should I support multiple interfaces?   I could either 
  # force them to pick the result of getmyip here or could return a different 
  # error later....   I think I'll wait.

  # If this is a UDP interface, then we should listen for udp datagrams
  # (there is no 'listen' so the time to start now)...
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    if 'socketobjectid' in filedescriptortable[fd]:
      # BUG: I need to avoid leaking sockets, so I should close the previous...
      raise UnimplementedError("I should close the previous UDP listener when re-binding")
    udpsockobj = listenformessage(localip,localport)
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(udpsockobj)
    
  

  # Done!   Let's set the information and bind later since Repy V2 doesn't 
  # support a separate call for binding...
  filedescriptortable[fd]['localip']=localip
  filedescriptortable[fd]['localport']=localport

  return 0






# int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);


##### CONNECT  #####


def connect_syscall(fd,remoteip,remoteport):
  """ 
    http://linux.die.net/man/2/connect
  """

  if fd not in filedescriptortable:
    raise SyscallError("connect_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("connect_syscall","ENOTSOCK","The descriptor is not a socket.")

  # includes CONNECTED and LISTEN
  if filedescriptortable[fd]['state'] != NOTCONNECTED:
    raise SyscallError("connect_syscall","EISCONN","The descriptor is already connected.")


  # What I do depends on the protocol...
  # If UDP, set the items and return
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport
    return 0


  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # Am I already bound?   If not, we'll need to get an ip / port
    if 'localip' not in filedescriptortable[fd]:
      localip = getmyip()
      localport = _get_available_tcp_port()

    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']

    try:
      # BUG: The timeout it configurable, right?
      newsockobj = openconnection(remoteip, remoteport, localip, localport, 10)

    except AddressBindingError, e:
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except InternetConnectivityError, e:
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except TimeoutError, e:
      raise SyscallError('connect_syscall','ETIMEOUT','Connection timed out')
    except DuplicateTupleError, e:
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')
    except ConnectionRefusedError, e:
      raise SyscallError('connect_syscall','ECONNREFUSED','Connection refused.')
 
    # fill in the file descriptor table...
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport

    filedescriptortable[fd]['state'] = CONNECTED

    # change the state and return success
    return 0

  else:
    raise UnimplementedError("Unknown protocol in connect()")

    






# ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);

##### SENDTO  #####


def sendto_syscall(fd,message, remoteip,remoteport,flags):
  """ 
    http://linux.die.net/man/2/sendto
  """

  if fd not in filedescriptortable:
    raise SyscallError("sendto_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("sendto_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags != 0:
    raise UnimplementedError("Flags are not understood by sendto!")

  # if there is no IP / port, call send instead.   It will assume the other
  # end is connected...
  if remoteip == '' and remoteport == 0:
    return send_syscall(fd,message)

  if filedescriptortable[fd]['state'] == CONNECTED or filedescriptortable[fd]['state'] == LISTEN:
    raise SyscallError("sendto_syscall","EISCONN","The descriptor is connected.")


  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:
    raise SyscallError("sendto_syscall","EISCONN","The descriptor is connection-oriented.")
    
  # What I do depends on the protocol...
  # If UDP, set the items and return
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:

    # If unspecified, use a new local port / the local ip
    if 'localip' not in filedescriptortable[fd]:
      localip = getmyip()
      localport = _get_available_tcp_port()
    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']

    try:
      # BUG: The timeout it configurable, right?
      bytessent = sendmessage(remoteip, remoteport, message, localip, localport)

    except AddressBindingError, e:
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except DuplicateTupleError, e:
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')
 
    # fill in the file descriptor table...
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport


    # return the characters sent!
    return bytessent

  else:
    raise UnimplementedError("Unknown protocol in sendto()")








# ssize_t send(int sockfd, const void *buf, size_t len, int flags);

##### SEND  #####


def send_syscall(fd, message, flags):
  """ 
    http://linux.die.net/man/2/send
  """

  # TODO: Change write() to call send when on a socket!!!

  if fd not in filedescriptortable:
    raise SyscallError("send_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("send_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags != 0:
    raise UnimplementedError("Flags are not understood by send!")

  # includes NOTCONNECTED and LISTEN
  if filedescriptortable[fd]['state'] != CONNECTED:
    raise SyscallError("send_syscall","ENOTCONN","The descriptor is not connected.")


  if filedescriptortable[fd]['protocol'] != IPPROTO_TCP:
    raise SyscallError("send_syscall","EOPNOTSUPP","send not supported on this protocol.")
    
  # I'll check this anyways, because I later might have multiple protos 
  # supported
  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # get the socket so I can send...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjid']]
    try:
      bytessent = sockobj.send(message)

    except Exception, e:
      # I think this shouldn't happen.   A closed socket should go to
      # NOTCONNECTED state.   This is an internal error...
      raise 
 

    # return the characters sent!
    return bytessent

  else:
    raise UnimplementedError("Unknown protocol in send()")

    

    





# ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, struct sockaddr *src_addr, socklen_t *addrlen);


##### RECVFROM  #####


# Wait this long between recv calls...
RECVRETRYWAITAMOUNT = .001





# Note that this call may be used by recv_syscall since they are so similar
def recvfrom_syscall(fd,length,flags):
  """ 
    http://linux.die.net/man/2/recvfrom
  """

  if fd not in filedescriptortable:
    raise SyscallError("recvfrom_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("recvfrom_syscall","ENOTSOCK","The descriptor is not a socket.")

  # Most of these are uninteresting
  if flags != 0:
    raise UnimplementedError("Flags are not understood by recvfrom!")




  # What I do depends on the protocol...
  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # includes NOTCONNECTED and LISTEN
    if filedescriptortable[fd]['state'] != CONNECTED:
      raise SyscallError("recvfrom_syscall","ENOTCONN","The descriptor is not connected.")
    
    # I'm ready to recv, get the socket object...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjid']]

    remoteip = filedescriptortable[fd]['remoteip']
    remoteport = filedescriptortable[fd]['remoteport']

    # keep trying to get something until it works (or EOF)...
    while True:
      try:
        return remoteip, remoteport, sockobj.recv(length)

      except SocketClosedRemote, e:
        return remoteip, remoteport, ''

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        sleep(RECVRETRYWAITAMOUNT)



  # If UDP, recieve a message and return...
  elif filedescriptortable[fd]['protocol'] == IPPROTO_UDP:

    # BUG / HELP!!!: Calling this with UDP and without binding does something I
    # don't really understand...   It seems to block but I don't know what is 
    # happening.   The socket isn't bound to a valid inode,etc from what I see.
    if 'localip' not in filedescriptortable[fd]:
      raise UnimplementedError("BUG / FIXME: Should bind before using UDP to recv / recvfrom")


    # get the udpsocket object...
    udpsockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]



    # keep trying to get something until it works in most cases...
    while True:
      try:
        return udpsockobj.getmessage()

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        sleep(RECVRETRYWAITAMOUNT)



  else:
    raise UnimplementedError("Unknown protocol in recvfrom()")









# ssize_t recv(int sockfd, void *buf, size_t len, int flags);

##### RECV  #####


def recv_syscall(fd, length, flags):
  """ 
    http://linux.die.net/man/2/recv
  """

  # TODO: Change read() to call recv when on a socket!!!

  remoteip, remoteport, message = recvfrom_syscall(fd, length, flags)

  # we don't need the remoteip or remoteport for this...
  return message

    

    





# int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
# int getpeername(int sockfd, struct sockaddr *addr", socklen_t *" addrlen);
# int getsockname(int sockfd, struct sockaddr *addrsocklen_t *" addrlen);
# int listen(int sockfd, int backlog);
# int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
# int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);


# int shutdown(int sockfd, int how);
# int socketpair(int domain, int type, int protocol, int socket_vector[2]);
# ssize_t recvmsg(int sockfd, struct msghdr *msg, int flags);
# ssize_t sendmsg(int sockfd, const struct msghdr *msg, int flags);






