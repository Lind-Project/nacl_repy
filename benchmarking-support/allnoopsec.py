"""
This no-op security layer interposes
on all the most calls, but does nothing.

Does not wrap:
  - createvirtualnamespace()
  - VN objects
"""

TYPE="type"
ARGS="args"
RETURN="return"
EXCP="exceptions"
TARGET="target"
FUNC="func"
OBJC="objc"

class SecureSocket():
  def __init__(self, sock):
    self.sock = sock

  def recv(self, bytes):
    return self.sock.recv(bytes)

  def send(self, mess):
    return self.sock.send(mess)

  def close(self):
    return self.sock.close()

# Functional wrapper
def get_SecureSocket(sock):
  return SecureSocket(sock)

sec_socket_def = {"obj-type":SecureSocket,
                  "name":"SecureSocket",
                  "recv":{TYPE:FUNC,ARGS:[(int,long)],RETURN:str,EXCP:Exception,TARGET:SecureSocket.recv},
                  "send":{TYPE:FUNC,ARGS:(str,),RETURN:int,EXCP:Exception,TARGET:SecureSocket.send},
                  "close":{TYPE:FUNC,ARGS:None,RETURN:bool,EXCP:Exception,TARGET:SecureSocket.close},
                 }

# Define the initializer of SecureSocket
sec_sock_constr = {"get_SecureSocket":{
                    TYPE:OBJC,
                    ARGS:("any",),
                    RETURN:sec_socket_def,
                    EXCP:None,
                    TARGET:get_SecureSocket
                    }
                  }

# Wrap this ourselves
wrapped_constructor = wrap_references(sec_sock_constr)

# Expose this "safe" constructor
safe_SecureSocket = wrapped_constructor["get_SecureSocket"]


class SecureTCPServer():
  def __init__(self, sock):
    self.sock = sock

  def getconnection(self):
    ip,port,s = self.sock.getconnection()
    return (ip, port, safe_SecureSocket(s))

  def close(self):
    return self.sock.close()

sec_tcp_def = {"obj-type":SecureTCPServer,
               "name":"SecureTCPServer",
               "getconnection":{TYPE:FUNC,ARGS:None,RETURN:tuple,EXCP:Exception,TARGET:SecureTCPServer.getconnection},
               "close":{TYPE:FUNC,ARGS:None,RETURN:bool,EXCP:Exception,TARGET:SecureTCPServer.close}
              }

class SecureUDPServer():
  def __init__(self, sock):
    self.sock = sock

  def getmessage(self):
    return self.sock.getmessage()

  def close(self):
    return self.sock.close()

sec_udp_def = {"obj-type":SecureUDPServer,
               "name":"SecureUDPServer",
               "getmessage":{TYPE:FUNC,ARGS:None,RETURN:tuple,EXCP:Exception,TARGET:SecureUDPServer.getmessage},
               "close":{TYPE:FUNC,ARGS:None,RETURN:bool,EXCP:Exception,TARGET:SecureUDPServer.close}
              }


def secure_getmyip():
  return getmyip()

def secure_gethostbyname(name):
  return gethostbyname(name)

def secure_sendmessage(destip, destport, message, localip, localport):
  return sendmessage(destip, destport, message, localip, localport)

def secure_listenformessage(localip, localport):
  return SecureUDPServer(listenformessage(localip, localport))

def secure_openconnection(destip, destport, localip, localport, timeout):
  return SecureSocket(openconnection(destip, destport, localip, localport, timeout))

def secure_listenforconnection(localip, localport):
  return SecureTCPServer(listenforconnection(localip, localport))


CHILD_CONTEXT_DEF["getmyip"] = {TYPE:FUNC,ARGS:None,RETURN:str,EXCP:RepyException,TARGET:secure_getmyip}
CHILD_CONTEXT_DEF["gethostbyname"] = {TYPE:FUNC,ARGS:str,RETURN:str,EXCP:RepyException,TARGET:secure_gethostbyname}
CHILD_CONTEXT_DEF["sendmessage"] = {TYPE:FUNC,ARGS:(str,int,str,str,int),RETURN:int,
                                    EXCP:RepyException,TARGET:secure_sendmessage}
CHILD_CONTEXT_DEF["listenformessage"] = {TYPE:OBJC,ARGS:(str,int),RETURN:sec_udp_def,
                                         EXCP:Exception,TARGET:secure_listenformessage}
CHILD_CONTEXT_DEF["openconnection"] = {TYPE:OBJC,ARGS:(str,int,str,int,(int,float)),RETURN:sec_socket_def,
                                       EXCP:Exception,TARGET:secure_openconnection}
CHILD_CONTEXT_DEF["listenforconnection"] = {TYPE:OBJC,ARGS:(str,int),RETURN:sec_tcp_def,
                                       EXCP:Exception,TARGET:secure_listenforconnection}


def secure_listfiles():
  return listfiles()

CHILD_CONTEXT_DEF["listfiles"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:list,TARGET:secure_listfiles}

def secure_removefile(file):
  return removefile(file)

CHILD_CONTEXT_DEF["removefile"] = {TYPE:FUNC,ARGS:(str,),EXCP:Exception,RETURN:(bool,None),TARGET:secure_removefile}

def secure_getruntime():
  return getruntime()

CHILD_CONTEXT_DEF["getruntime"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:float,TARGET:secure_getruntime}

def secure_randombytes():
  return randombytes()

CHILD_CONTEXT_DEF["randombytes"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:str,TARGET:secure_randombytes}

def secure_createthread(f):
  return createthread(f)

CHILD_CONTEXT_DEF["createthread"] = {TYPE:FUNC,ARGS:("any",),EXCP:Exception,RETURN:None,TARGET:secure_createthread}

def secure_sleep(time):
  sleep(time)

CHILD_CONTEXT_DEF["sleep"] = {TYPE:FUNC,ARGS:((int,long,float),),EXCP:None,RETURN:None,TARGET:secure_sleep}

def secure_getthreadname():
  return getthreadname()

CHILD_CONTEXT_DEF["getthreadname"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:str,TARGET:secure_getthreadname}

def secure_getresources():
  return getresources()

CHILD_CONTEXT_DEF["getresources"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:tuple,TARGET:secure_getresources}

def secure_getlasterror():
  return getlasterror()

CHILD_CONTEXT_DEF["getlasterror"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:(str,None),TARGET:secure_getlasterror}

def secure_exitall():
  return exitall()

CHILD_CONTEXT_DEF["exitall"] = {TYPE:FUNC,ARGS:None,EXCP:None,RETURN:None,TARGET:secure_exitall}

class SecureLock():
  def __init__(self,lock):
    self.lock = lock

  def acquire(self, blocking):
    return self.lock.acquire(blocking)

  def release(self):
    return self.lock.release()

sec_lock_def = {"obj-type":SecureLock,
                  "name":"SecureLock",
                  "acquire":{TYPE:FUNC,ARGS:(bool,),RETURN:bool,EXCP:None,TARGET:SecureLock.acquire},
                  "release":{TYPE:FUNC,ARGS:None,RETURN:None,EXCP:Exception,TARGET:SecureLock.release},
                 }

def secure_createlock():
  l = createlock()
  return SecureLock(l)

CHILD_CONTEXT_DEF["createlock"] = {TYPE:OBJC,ARGS:None,EXCP:None,RETURN:sec_lock_def,TARGET:secure_createlock}

class SecureFile():
  def __init__(self,file):
    self.file = file

  def readat(self,bytes,offset):
    return self.file.readat(bytes,offset)

  def writeat(self,data,offset):
    return self.file.writeat(data,offset)

  def close(self):
    return self.file.close()

sec_file_def = {"obj-type":SecureFile,
                "name":"SecureFile",
                "readat":{TYPE:FUNC,ARGS:((int,long),(int,long)),EXCP:Exception,RETURN:str,TARGET:SecureFile.readat},
                "writeat":{TYPE:FUNC,ARGS:(str,(int,long)),EXCP:Exception,RETURN:(int,long),TARGET:SecureFile.writeat},
                "close":{TYPE:FUNC,ARGS:None,EXCP:None,RETURN:(bool,type(None)),TARGET:SecureFile.close}
               }

def secure_openfile(filename, create):
  f = openfile(filename,create)
  return SecureFile(f)

CHILD_CONTEXT_DEF["openfile"] = {TYPE:OBJC,ARGS:(str,bool),EXCP:Exception,RETURN:sec_file_def,TARGET:secure_openfile}


# Dispatch
secure_dispatch_module()

