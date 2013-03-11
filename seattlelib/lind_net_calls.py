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
#  'sndbuf':131070, 'rcvbuf': 262140, 'state':NOTCONNECTED}
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

connectedsocket = []

# This is raised to return an error...   It's the same as for the file 
# system calls
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""


class CompositeTCPSocket:
  """This class can be used in place of a regular repy socket,
  when you need to bind and operate on two sockets at once.
  """

  def __init__(self, ip1, ip2, port):
    self.ip1 = ip1
    self.ip2 = ip2
    self.port = port
    self.c1 = listenforconnection(ip1, port)
    self.c2 = listenforconnection(ip2, port)
  
  def close(self):
    self.c1.close()
    self.c2.close()
    

  def getconnection(self):
    try:
     conn = self.c1.getconnection()
    except SocketWouldBlockError, e:
      conn = self.c2.getconnection()
    return conn


class CompositeUDPSocket:
  """This class can be used in place of a regular repy socket,
  when you need to bind and operate on two sockets at once.
  """

  def __init__(self, ip1, ip2, port):
    self.ip1 = ip1
    self.ip2 = ip2
    self.port = port
    self.c1 = listenformessage(ip1, port)
    self.c2 = listenformessage(ip2, port)
  
  def close(self):
    self.c1.close()
    self.c2.close()
    

  def getmessage(self):
    try:
      msg = self.c1.getmessage()
    except SocketWouldBlockError, e:
      msg = self.c2.getmessage()
    return msg



######################   Generic Helper functions   #########################


# a list of udp ports already used.   This is used to help us figure out a good
# available port
_usedudpportsset = set([])
# these are the ports we possibly could use...
_usableudpportsset = map(int, getresources()[0]['messport'].copy())

# the same for tcp...
_usedtcpportsset = set([])
_usabletcpportsset = map(int, getresources()[0]['connport'].copy())

# collect all the port list operations
_port_operations_debug = []

_port_list_lock = createlock()
# We need a helper that gets an available port...
# Get the last unused port and return it...
def _get_available_udp_port():
  for port in list(_usableudpportsset)[::-1]:
    if port not in _usedudpportsset:
      _port_operations_debug.append("suggesting UDP port " + str(port))
      return port
  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_udp_port","ENOBUFS","No UDP port available")


# A verbatim copy of the above...   It's so simple, I guess it's okay to do so
def _get_available_tcp_port():
  for port in list(_usabletcpportsset)[::-1]:
    if port not in _usedtcpportsset:
      _port_operations_debug.append("suggesting TCP port " + str(port))
      return port

  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_tcp_port","ENOBUFS","No TCP port available")


def _reserve_localport(port, protocol):
  global _usedtcpportsset
  global _usedudpportsset
  
  _port_list_lock.acquire(True)
  status = True
  _port_operations_debug.append("Reserving port " + str(port))
  if protocol == IPPROTO_UDP:
    if port == 0:
      port = _get_available_udp_port()
    if port not in _usedudpportsset:
      _usedudpportsset.add(port)
    else:
      status = False
  elif protocol == IPPROTO_TCP:
    if port == 0:
      port = _get_available_tcp_port()

    if port not in _usedtcpportsset:
      _usedtcpportsset.add(port)
    else:
      status = False
  _port_list_lock.release()
  if not status:
    warning("_reserve_local_port", _port_operations_debug)
  return (status, port)

# give a port and protocol, return the port to that portocol's pool
def _release_localport(port, protocol):
  global _usedtcpportsset
  global _usedudpportsset
  _port_list_lock.acquire(True)
  _port_operations_debug.append("Releasing port " + str(port))

  try:
    if protocol == IPPROTO_UDP:
      _usedudpportsset.remove(port)
    elif protocol == IPPROTO_TCP:
      _usedtcpportsset.remove(port)
  except KeyError:
    warning("Warning: freeing a port which is already free.  Port is", port)
    warning(_port_operations_debug)
  finally:
    _port_list_lock.release()

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
def _socket_initializer(domain,socktype,protocol, blocking=False, cloexec=False):
  # get a file descriptor
  flags = 0
  if blocking:
    flags = flags | O_NONBLOCK
  if cloexec:
    flags = flags | O_CLOEXEC
  newfd = get_next_fd()
  
  # NOTE: I'm intentionally omitting the 'inode' field.  This will make most
  # of the calls I did not change break.
  filedescriptortable[newfd] = {
      'mode':S_IFSOCK|0666, # set rw-rw-rw- perms too. This is what POSIX does.
      'domain':domain,
      'type':socktype,      # I'm using this name because it's used by POSIX.
      'protocol':protocol,
      # BUG: I may need to handle the global setting of options here...
      'options':0,          # start with all options off...
      'sndbuf':131070,      # buffersize (only used by getsockopt)
      'rcvbuf':262140,      # buffersize (only used by getsockopt)
      'state':NOTCONNECTED, # we start without any connection
      'lock':createlock(),
      'flags':flags,
      'errno':0
# We don't set the ip / ports or socketobjectid because they are unknown now.
  }
  return newfd
      


# int socket(int domain, int type, int protocol);
def socket_syscall(domain, socktype, protocol):
  """ 
    http://linux.die.net/man/2/socket
  """
  # this code is basically one huge case statement by domain

  # sock type is stored in last 3 or 4 bits, the rest is flags

  real_socktype = socktype & 7 # the type without the extra flags

  blocking = (socktype & SOCK_NONBLOCK) != 0 # check the non-blocking flag
  cloexec = (socktype & SOCK_CLOEXEC) != 0 # check the cloexec flag

  if blocking:
    warning("Warning: trying to create a non-blocking socket - we don't support that yet.")

  # okay, let's do different things depending on the domain...
  if domain == PF_INET:

    
    if real_socktype == SOCK_STREAM:
      # If is 0, set to default (IPPROTO_TCP)
      if protocol == 0:
        protocol = IPPROTO_TCP


      if protocol != IPPROTO_TCP:
        raise UnimplementedError("The only SOCK_STREAM implemented is TCP.  Unknown protocol:"+str(protocol))
      
      return _socket_initializer(domain,real_socktype,protocol, blocking, cloexec)


    # datagram!
    elif real_socktype == SOCK_DGRAM:
      # If is 0, set to default (IPPROTO_UDP)
      if protocol == 0:
        protocol = IPPROTO_UDP

      if protocol != IPPROTO_UDP:
        raise UnimplementedError("The only SOCK_DGRAM implemented is UDP.  Unknown protocol:"+str(protocol))
    
      return _socket_initializer(domain,real_socktype,protocol)
    else:
      raise UnimplementedError("Unimplemented sockettype: "+str(real_socktype))

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

  intent_to_rebind = False

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
      # SO_REUSEPORT (at least this is true on some OSes.   It's OS dependent)
      if filedescriptortable[fd]['options'] & filedescriptortable[otherfd]['options'] & SO_REUSEPORT == SO_REUSEPORT:
        # all is well, continue...
        intent_to_rebind = True
      else:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")

  # BUG (?): hmm, how should I support multiple interfaces?   I could either 
  # force them to pick the result of getmyip here or could return a different 
  # error later....   I think I'll wait.
  if not intent_to_rebind:
    (ret, localport) = _reserve_localport(localport, filedescriptortable[fd]['protocol'])
    assert ret
  # If this is a UDP interface, then we should listen for udp datagrams
  # (there is no 'listen' so the time to start now)...
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    if 'socketobjectid' in filedescriptortable[fd]:
      # BUG: I need to avoid leaking sockets, so I should close the previous...
      raise UnimplementedError("I should close the previous UDP listener when re-binding")
    if localip == '0.0.0.0':
      udpsockobj = CompositeUDPSocket('127.0.0.1', getmyip(), localport)
    else:
      udpsockobj = listenformessage(localip, localport)
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


  filedescriptortable[fd]['last_peek'] = ''


  # What I do depends on the protocol...
  # If UDP, set the items and return
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport
    rc = 0
    try:
      a = filedescriptortable[fd]['localip']
    except KeyError:
      # if the local IP is not yet set, allocate it and bind to it.
      rc = bind_syscall(fd, getmyip(), _get_available_udp_port())
    return rc


  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # Am I already bound?   If not, we'll need to get an ip / port
    if 'localip' not in filedescriptortable[fd]:
      localip = getmyip()
      
      localport = _get_available_tcp_port()
      while not _reserve_localport(localport, filedescriptortable[fd]['protocol'])[0]:
        localport = _get_available_tcp_port()
    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']



    try:
      # BUG: The timeout it configurable, right?
      newsockobj = openconnection(remoteip, remoteport, localip, localport, 10)

    except AddressBindingError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')

    except InternetConnectivityError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')

    except TimeoutError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ETIMEDOUT','Connection timed out')

    except DuplicateTupleError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')

    except ConnectionRefusedError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ECONNREFUSED','Connection refused.')

    # fill in the file descriptor table...
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport
    filedescriptortable[fd]['state'] = CONNECTED
    filedescriptortable[fd]['errno'] = 0
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

  if flags != 0 and flags != MSG_NOSIGNAL:
    raise UnimplementedError("Flags are not understood by sendto!")

  # if there is no IP / port, call send instead.   It will assume the other
  # end is connected...
  if remoteip == '' and remoteport == 0:
    warning("Warning: sending back to send.")
    return send_syscall(fd,message, flags)

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
      localport = _get_available_udp_port()
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
  if fd not in filedescriptortable:
    raise SyscallError("send_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("send_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags  != 0 and flags != MSG_NOSIGNAL: 
    raise UnimplementedError("Flagss are not understood by send!")

  # includes NOTCONNECTED and LISTEN
  if  filedescriptortable[fd]['protocol'] == IPPROTO_TCP and filedescriptortable[fd]['state'] != CONNECTED:
    raise SyscallError("send_syscall","ENOTCONN","The descriptor is not connected.")


  if filedescriptortable[fd]['protocol'] != IPPROTO_TCP and filedescriptortable[fd]['protocol'] != IPPROTO_UDP:
    raise SyscallError("send_syscall","EOPNOTSUPP","send not supported on this protocol.")
    
  # I'll check this anyways, because I later might have multiple protos 
  # supported
  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # get the socket so I can send...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    
    # retry until it does not block...
    while True:
      try:
        bytessent = sockobj.send(message)
      # sleep and retry
      except SocketWouldBlockError, e:
         sleep(RETRYWAITAMOUNT)
        
      except Exception, e:
        # I think this shouldn't happen.   A closed socket should go to
        # NOTCONNECTED state.   This is an internal error...
         raise 

      # return the characters sent!
      return bytessent
  elif filedescriptortable[fd]['protocol'] == IPPROTO_UDP:

    remoteip = filedescriptortable[fd]['remoteip']
    remoteport = filedescriptortable[fd]['remoteport']

    bytessent = sendto_syscall(fd, message, remoteip, remoteport, flags)
    return bytessent
  else:
    raise UnimplementedError("Unknown protocol in send()")

    

    





# ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, struct sockaddr *src_addr, socklen_t *addrlen);


##### RECVFROM  #####


# Wait this long between recv calls...
RETRYWAITAMOUNT = .00001


# Note that this call may be used by recv_syscall since they are so similar
def recvfrom_syscall(fd,length,flags):
  """ 
    http://linux.die.net/man/2/recvfrom
  """

  if fd not in filedescriptortable:
    raise SyscallError("recvfrom_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("recvfrom_syscall","ENOTSOCK","The descriptor is not a socket.")


  # What I do depends on the protocol...
  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # includes NOTCONNECTED and LISTEN
    if filedescriptortable[fd]['state'] != CONNECTED:
      raise SyscallError("recvfrom_syscall","ENOTCONN","The descriptor is not connected."+str(filedescriptortable[fd]['state']))
    # is this a non-blocking recv OR a nonblocking socket?
    
    # I'm ready to recv, get the socket object...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    peek = filedescriptortable[fd]['last_peek']
    remoteip = filedescriptortable[fd]['remoteip']
    remoteport = filedescriptortable[fd]['remoteport']
    # keep trying to get something until it works (or EOF)...
    while True:
      # if we have previous data from a peek, use that
      data = ''
      try:
        data = sockobj.recv(length)
      except SocketClosedRemote, e:
        data = ''
      except SocketClosedLocal, e:
        data = ''

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        if IS_NONBLOCKING(filedescriptortable[fd]['flags'], flags):
          raise e
        if peek == '':
          sleep(RETRYWAITAMOUNT)
          continue

      if peek == '':
        if (flags & MSG_PEEK) != 0:
          filedescriptortable[fd]['last_peek'] = data
        return remoteip, remoteport, data

      peek = peek + data
      if len(peek) <= length:
        ret_data = peek
        filedescriptortable[fd]['last_peek'] = ''
      else:
        ret_data = peek[:length]
        filedescriptortable[fd]['last_peek'] = peek[length:]
        # savd this data for later?
      if (flags & MSG_PEEK) != 0:
        # print "@@ peek next time"
        filedescriptortable[fd]['last_peek'] = peek
        
      return remoteip, remoteport, ret_data

  
   



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
        sleep(RETRYWAITAMOUNT)



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

    






# int getsockname(int sockfd, struct sockaddr *addrsocklen_t *" addrlen);


##### GETSOCKNAME  #####


def getsockname_syscall(fd):
  """ 
    http://linux.die.net/man/2/getsockname
  """

  if fd not in filedescriptortable:
    raise SyscallError("getsockname_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getsockname_syscall","ENOTSOCK","The descriptor is not a socket.")


  # if we know this, return it...
  if 'localip' in filedescriptortable[fd]:
    return filedescriptortable[fd]['localip'], filedescriptortable[fd]['localport']
  
  # otherwise, return '0.0.0.0', 0
  else:
    return '0.0.0.0',0
  

    


    




##### GETPEERNAME  #####


def getpeername_syscall(fd):
  """ 
    http://linux.die.net/man/2/getpeername
  """

  if fd not in filedescriptortable:
    raise SyscallError("getpeername_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getpeername_syscall","ENOTSOCK","The descriptor is not a socket.")


  # if we don't know this, we should raise an exception
  if 'remoteip' not in filedescriptortable[fd]:
    raise SyscallError("getpeername_syscall","ENOTCONN","The descriptor is not connected.")

  # if we know this, return it...
  return filedescriptortable[fd]['remoteip'], filedescriptortable[fd]['remoteport']
  
  





# int listen(int sockfd, int backlog);



##### LISTEN  #####


# I ignore the backlog
def listen_syscall(fd,backlog):
  """ 
    http://linux.die.net/man/2/listen
  """

  if fd not in filedescriptortable:
    raise SyscallError("listen_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("listen_syscall","ENOTSOCK","The descriptor is not a socket.")

  # BUG: I need to check if someone else is already listening here...


  # If UDP, raise an exception
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    raise SyscallError("listen_syscall","EOPNOTSUPP","This protocol does not support listening.")


  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    if filedescriptortable[fd]['state'] == LISTEN:
      # already done!
      return 0


    if 'localip' not in filedescriptortable[fd]:
      # the real POSIX impl picks a random port and listens on 0.0.0.0.   
      # I think this is unnecessary to implement.
      raise UnimplementedError("listen without bind")


    # If it's connected, this is still allowed, but I won't implement it...
    if filedescriptortable[fd]['state'] == CONNECTED:
      # BUG: I would need to close this (if the last) to handle this right...
      raise UnimplementedError("Listen should close the existing connected socket")


    # Is someone else already listening on this address?   This may happen
    # with SO_REUSEPORT
    for otherfd in filedescriptortable:
      # skip ours
      if fd == otherfd:
        continue

      # if not a socket, skip it...
      if 'domain' not in filedescriptortable[otherfd]:
        continue

      # if they are not listening, skip it...
      if filedescriptortable[otherfd]['state'] != LISTEN:
        continue

      # if the protocol / domain/ type differ, ignore
      if filedescriptortable[otherfd]['domain'] != filedescriptortable[fd]['domain'] or filedescriptortable[otherfd]['type'] != filedescriptortable[fd]['type'] or filedescriptortable[otherfd]['protocol'] != filedescriptortable[fd]['protocol']:
        continue

      # if they are already bound to this address / port
      if filedescriptortable[otherfd]['localip'] == filedescriptortable[fd]['localip'] and filedescriptortable[otherfd]['localport'] == filedescriptortable[fd]['localport']:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")



    # otherwise, all is well.   Let's set it up!
    filedescriptortable[fd]['state'] = LISTEN


    # BUG: I'll let anything go through for now.   I'm fairly sure there will 
    # be issues I may need to handle later.
    # #CM: this is really annoying, so for now we bind to local ip
    if filedescriptortable[fd]['localip'] == "0.0.0.0":
      newsockobj = CompositeTCPSocket('127.0.0.1', getmyip(), filedescriptortable[fd]['localport'])
    else:
      newsockobj = listenforconnection(filedescriptortable[fd]['localip'], filedescriptortable[fd]['localport'])
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)

    # change the state and return success
    return 0

  else:
    raise UnimplementedError("Unknown protocol in listen()")

    








# int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);




##### ACCEPT  #####


# returns ip, port, sockfd
def accept_syscall(fd, flags=0):
  """ 
    http://linux.die.net/man/2/accept
  """

  if fd not in filedescriptortable:
    raise SyscallError("accept_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("accept_syscall","ENOTSOCK","The descriptor is not a socket.")

  blocking = (flags & SOCK_NONBLOCK) != 0
  cloexec = (flags & SOCK_CLOEXEC) != 0

  # If UDP, raise an exception
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    raise SyscallError("accept_syscall","EOPNOTSUPP","This protocol does not support listening.")

  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # must be listening
    if filedescriptortable[fd]['state'] != LISTEN:
      raise SyscallError("accept_syscall","EINVAL","Must call listen before accept.")

    listeningsocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    
    # now we should loop (block) until we get an incoming connection
    while True:
      try:
        if connectedsocket != []:
          remoteip, remoteport, acceptedsocket = connectedsocket.pop(0)
        else:
          remoteip, remoteport, acceptedsocket = listeningsocket.getconnection() 

      # sleep and retry
      except SocketWouldBlockError, e:
        sleep(RETRYWAITAMOUNT)
      else:

        newfd = _socket_initializer(filedescriptortable[fd]['domain'],filedescriptortable[fd]['type'],filedescriptortable[fd]['protocol'], blocking, cloexec)
        filedescriptortable[newfd]['state'] = CONNECTED
        filedescriptortable[newfd]['localip'] = filedescriptortable[fd]['localip']
        newport = _get_available_tcp_port()
        (ret, newport) = _reserve_localport(newport, IPPROTO_TCP) 
        assert ret
        filedescriptortable[newfd]['localport'] = newport
        filedescriptortable[newfd]['remoteip'] = remoteip
        filedescriptortable[newfd]['remoteport'] = remoteport
        filedescriptortable[newfd]['socketobjectid'] = _insert_into_socketobjecttable(acceptedsocket)
        filedescriptortable[newfd]['last_peek'] = ''

        return remoteip, remoteport, newfd

  else:
    raise UnimplementedError("Unknown protocol in accept()")

    






# int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);


# I'm just going to set these binary options or return the previous setting.   
# In most cases, this will be while doing nothing.
STOREDSOCKETOPTIONS = [ SO_LINGER, # ignored
                        SO_KEEPALIVE, # ignored
                        SO_SNDLOWAT, # ignored
                        SO_RCVLOWAT, # ignored
                        SO_REUSEPORT, # used to allow duplicate binds...
                        SO_REUSEADDR,
                      ]


##### GETSOCKOPT  #####
def getsockopt_syscall(fd, level, optname):
  """ 
    http://linux.die.net/man/2/getsockopt
  """
  if fd not in filedescriptortable:
    raise SyscallError("getsockopt_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getsockopt_syscall","ENOTSOCK","The descriptor is not a socket.")

  # This should really be SOL_SOCKET, however, we'll also handle a few others
  if level == SOL_UDP:
    raise UnimplementedError("UDP is not supported for getsockopt")

  # TCP...  Ignore most things...
  elif level == SOL_TCP:
    # do nothing
    
    raise UnimplementedError("TCP options not remembered by getsockopt")



  elif level == SOL_SOCKET:
    # this is where the work happens!!!

    if optname == SO_ACCEPTCONN:
      # indicate if we are accepting connections...
      if filedescriptortable[fd]['state'] == LISTEN:
        return 1
      else:
        return 0

    # if the option is a stored binary option, just return it...
    if optname in STOREDSOCKETOPTIONS:
      if (filedescriptortable[fd]['options'] & optname) == optname:
        return 1
      else:
        return 0

    # Okay, let's handle the (ignored) buffer settings...
    if optname == SO_SNDBUF:
      return filedescriptortable[fd]['sndbuf']

    if optname == SO_RCVBUF:
      return filedescriptortable[fd]['rcvbuf']

    # similarly, let's handle the SNDLOWAT and RCVLOWAT, etc.
    # BUG?: On Mac, this seems to be stored much like the buffer settings
    if optname == SO_SNDLOWAT or optname == SO_RCVLOWAT:
      return 1


    # return the type if asked...
    if optname == SO_TYPE:
      return filedescriptortable[fd]['type']

    # I guess this is always true!?!?   I certainly don't handle it.
    if optname == SO_OOBINLINE:
      return 1

    if optname == SO_ERROR:
      warning("Warning: returning no error because error reporting is not done correctly yet.")
      tmp = filedescriptortable[fd]['errno']
      filedescriptortable[fd]['errno'] = 0
      return tmp

    if optname == SO_REUSEADDR:
      return 0


    raise UnimplementedError("Unknown option in getsockopt(). option = %s"%(oct(optname)))

  else:
    raise UnimplementedError("Unknown level in getsockopt(). level = %s"%(oct(level)))








# int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);

##### SETSOCKOPT  #####
def setsockopt_syscall(fd, level, optname, optval):
  """ 
    http://linux.die.net/man/2/setsockopt
  """
  if fd not in filedescriptortable:
    raise SyscallError("setsockopt_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("setsockopt_syscall","ENOTSOCK","The descriptor is not a socket.")

  # This should really be SOL_SOCKET, however, we'll also handle a few others
  if level == SOL_UDP:
    raise UnimplementedError("UDP is not supported for setsockopt")

  # TCP...  Ignore most things...
  elif level == SOL_TCP:
    # do nothing
    if optname == TCP_NODELAY:
      return 0
 
    # otherwise return an error
    raise UnimplementedError("TCP options not remembered by setsockopt")


  elif level == SOL_SOCKET:
    # this is where the work happens!!!
    
    if optname == SO_ACCEPTCONN or optname == SO_TYPE or optname == SO_SNDLOWAT or optname == SO_RCVLOWAT:
      raise SyscallError("setsockopt_syscall","ENOPROTOOPT","Cannot set option using setsockopt. %d"%(optname))

    # if the option is a stored binary option, just return it...
    if optname in STOREDSOCKETOPTIONS:

      newoptions = filedescriptortable[fd]['options']
            
      # if the value is set, unset it...
      if (newoptions & optname) == optname:
        newoptions = newoptions - optname
        filedescriptortable[fd]['options'] = newoptions
        return 1

      # now let's set this if we were told to
      if optval:
        # this value should be 1!!!   Nothing else is allowed
        # assert(optval == 1), "Invalid optval"  This is not a valid assertion for SO_LINGER
        newoptions = newoptions | optname
      filedescriptortable[fd]['options'] = newoptions
      return 0
      

    # Okay, let's handle the (ignored) buffer settings...
    if optname == SO_SNDBUF:
      filedescriptortable[fd]['sndbuf'] = optval
      return 0

    if optname == SO_RCVBUF:
      filedescriptortable[fd]['rcvbuf'] = optval
      return 0

    # I guess this is always true!?!?   I certainly don't handle it.
    if optname == SO_OOBINLINE:
      # I can only handle this being true...
      assert(optval == 1), "Optval must be true"
      return 0

    raise UnimplementedError("Unknown option in setsockopt()" + str(optname))

  else:
    raise UnimplementedError("Unknown level in setsockopt()")





def _cleanup_socket(fd):
  if 'socketobjectid' in filedescriptortable[fd]:
    thesocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    thesocket.close()
    localport = filedescriptortable[fd]['localport']
    _release_localport(localport, filedescriptortable[fd]['protocol'])
    del socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    del filedescriptortable[fd]['socketobjectid']
    
    filedescriptortable[fd]['state'] = NOTCONNECTED
    return 0




# int shutdown(int sockfd, int how);

##### SHUTDOWN  #####
def setshutdown_syscall(fd, how):
  """ 
    http://linux.die.net/man/2/shutdown
  """

  if fd not in filedescriptortable:
    raise SyscallError("shutdown_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("shutdown_syscall","ENOTSOCK","The descriptor is not a socket.")


  if how == SHUT_RD or how == SHUT_WR:

    raise UnimplementedError("Partial shutdown not implemented.")

  
  # let's shut this down...
  elif how == SHUT_RDWR:
    # BUG: need to check for duplicate entries (ala dup / dup2)
    _cleanup_socket(fd)
  else:
    # BUG: I'm not exactly clear as to how to handle this...
    
    raise SyscallError("shutdown_syscall","EINVAL","Shutdown given an invalid how")
  
  return 0







def _nonblock_peek_read(fd):
  """Do a read, but don't block or change the socket cursor. Called from select.

  @return False if socket will block, True if socket is ready for read. 
  """

  try:
    flags = O_NONBLOCK | MSG_PEEK
    data = recvfrom_syscall(fd, 1, flags)[2]
  except SocketWouldBlockError, e:
    return False
  except SyscallError, e:
    if e[1] == 'ENOTCONN':
      return False
    else:
      raise e
  except SocketClosedRemote, e:
    return False

  if len(data) == 1: #return True, if data is present...
    return True
  elif len(data) == 0: #return True, since it tells that remote socket is closed...
    return True
  else:
    return False
    # assert False, "Should never here here! data:%s"%(data)


def select_syscall(nfds, readfds, writefds, exceptfds, time):
  """ 
    http://linux.die.net/man/2/select
  """
  # for each fd in readfds,
  # if file, not socket, mark true
  # if socket
  #   perform read
  # if read fails with would block
  #   mark false
  # if read works, do it as a peek, so next time it won't block

  retval = 0
  
  # the bit vectors only support 1024 file descriptors, also lower FDs are not supported
  if nfds < STARTINGFD or nfds > MAX_FD:
    raise SyscallError("select_syscall","EINVAL","number of FDs is wrong: %s"%(str(nfds)))

  new_readfds = []
  new_writefds = []
  new_exceptfds = []

  start_time = getruntime()
  end_time = start_time + (time if time != None else -1)
  while True:

    # Reads
    for fd in readfds:
      if fd == 0:
        warning("Warning: Can't do select on stdin.")
        continue
      if fd not in filedescriptortable:
        raise SyscallError("select_syscall","EBADF","The file descriptor is invalid.")

      desc = filedescriptortable[fd]
      if not IS_SOCK_DESC(fd) and fd != 0:
        # files never block, so always say yes for them
        new_readfds.append(fd)
        retval += 1
      else:
        #Get an interim connection and save it, so when actual accept_syscall() is called
        #we pass the saved the connection.
        if filedescriptortable[fd]['state'] == LISTEN:
          listeningsocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
          try:
            connectedsocket.append(listeningsocket.getconnection())
          except SocketWouldBlockError, e:
            pass
          else:
            new_readfds.append(fd)
            retval += 1
        #If the socket is not a listener, then it should be able to read data from socket.
        else:
        #sockets might block, lets check by doing a non-blocking peek read
          if filedescriptortable[fd]['protocol'] == IPPROTO_UDP or _nonblock_peek_read(fd):
            new_readfds.append(fd)
            retval += 1

    # Writes
    for fd in writefds:
      if fd not in filedescriptortable:
        raise SyscallError("select_syscall","EBADF","The file descriptor is invalid.")

      desc = filedescriptortable[fd]
      if not IS_SOCK_DESC(fd) or fd == 1 or fd == 2:
        # files never block, so always say yes for them
        new_writefds.append(fd)
        retval += 1
      else:
        #sockets d
        new_writefds.append(fd)
        retval += 1
        # assert not writefds, "Lind does not support socket writefds yet. FD=%d"%(fd)

    # Excepts
    assert not exceptfds, "Lind does not support exceptfds yet."

    # if the timeout is given as null or negative value, block forever until 
    # an event has occured, if timeout is provided as zero, return immediatly.
    # if positive time provided, wait until time expires and return
    
    if retval != 0 or time == 0 or (getruntime() >= end_time and time > 0):
      break
    else:
      sleep(RETRYWAITAMOUNT)
  leftover_time = time - (getruntime() - start_time)
  if leftover_time < 0:
     leftover_time = 0;
  return (retval, new_readfds, new_writefds, new_exceptfds, leftover_time)


def getifaddrs_syscall():
  """ 
    http://linux.die.net/man/2/getifaddrs

    Returns a list of the IP addresses of this machine.

    Fake most of the values.  I dont think an overly restrictive
    netmask is going to cause problems?
  """
  try:
    ip = getmyip()
  except:
    raise SyscallError("getifaddrs syscall","EADDRNOTAVAIL","Problem getting the" \
                       " local ip address.")
  broadcast = (ip.split('.')[0:3]) # the broadcast address is just x.y.z.255?
  broadcast = '.'.join(broadcast + ['255']) 
  return 0, [{'ifa_name':'eth0',
           'ifa_flags':0,
           'ifa_addr':ip,
           'ifa_netmask':'255.255.255.0', 
           'ifa_broadaddr':broadcast,
          },

          {'ifa_name':'lo0',
           'ifa_flags':0,
           'ifa_addr':'127.0.0.1',
           'ifa_netmask':'255.0.0.0',
           'ifa_broadaddr':'127.0.0.1',
          }
          ]


def poll_syscall(fds, timeout):
  """ 
    http://linux.die.net/man/2/poll

    returns a list of io status indicators for each of the
    file handles in fds

  """

  return_code = 0

  endtime = getruntime() + timeout
  while True:
    for structpoll in fds:
      fd = structpoll['fd']
      events = structpoll['events']
      read = events & POLLIN > 0 
      write = events & POLLOUT > 0 
      err = events & POLLERR > 0
      reads = []
      writes = []
      errors = []
      if read:
        reads.append(fd)
      if write:
        writes.append(fd)
      if err:
        errors.append(fd)

      #select with timeout set to zero, acts as a poll... 
      newfd = select_syscall(fd, reads, writes, errors, 0)
      
      # this FD found something
      mask = 0

      if newfd[0] > 0:
        mask = mask + (POLLIN if newfd[1] else 0)
        mask = mask + (POLLOUT if newfd[2] else 0) 
        mask = mask + (POLLERR if newfd[3] else 0)
        return_code += 1
      structpoll['revents'] = mask

    #if timeout is a negative value, then poll should run indefinitely
    #until there's an event in one of the descriptors.
    if (getruntime() > endtime and timeout >= 0) or return_code != 0:
      break
    else:
      sleep(RETRYWAITAMOUNT)

  return return_code, fds


#### SOCKETPAIR ####

SOCKETPAIR = "socketpair-socket"
SOCKETPAIR_LISTEN = "socketpair-listen"


def _helper_sockpair():
  """
    Helper function for socktpair() syscall. This is a thread that runs to
    establish a TCP connection and immediatly exists.
  """
  socketfd = mycontext[SOCKETPAIR]
  rc = listen_syscall(socketfd, 1)
  assert rc == 0, "Listen failed"
  rc = accept_syscall(mycontext[SOCKETPAIR]) 
  mycontext[SOCKETPAIR_LISTEN] = rc[2]

def socketpair_syscall(domain, socktype, protocol):
  """
    http://linux.die.net/man/2/socketpair
  """
  sv = []

  # Our implementation use TCP/UDP ports to mimic Unix domain sockets
  # so if we find that, swap to internet domain
  if domain == AF_UNIX:
    domain = AF_INET

  # create two sockets...
  sockfd = socket_syscall(domain, socktype, protocol)
  listfd = socket_syscall(domain, socktype, protocol)

  # TCP connection happens differently...
  if socktype == SOCK_STREAM:
    port1 = _get_available_tcp_port()
    rc = bind_syscall(sockfd, '127.0.0.1', port1)
    assert rc == 0, "Bind failed in socket pair"

    mycontext[SOCKETPAIR] = sockfd
    createthread(_helper_sockpair)
    sleep(.1)

    connect_syscall(listfd, '127.0.0.1', port1)
    sleep(.1)

    sv.append(mycontext[SOCKETPAIR_LISTEN])
    sv.append(listfd)

    # we need to close this socket...
    close_syscall(sockfd)

  # Make a connection oriented UDP.
  else:
    port1 = _get_available_udp_port()
    bind_syscall(sockfd, '127.0.0.1', port1)
    port2 = _get_available_udp_port()
    bind_syscall(listfd, '127.0.0.1', port2)

    connect_syscall(sockfd, '127.0.0.1', port2)
    connect_syscall(listfd, '127.0.0.1', port1)

    sv.append(sockfd)
    sv.append(listfd)

  return (0, sv)
