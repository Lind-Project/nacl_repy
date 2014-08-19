# This code is almost verbatim from:
# http://blog.bjola.ca/2007/08/using-timeout-with-xmlrpclib.html
try:
  import xmlrpclib
  from xmlrpclib import *
except ImportError:
  # Python 3.0 portability fix...
  import xmlrpc.client as xmlrpclib
  from xmlrpc.client import *

import httplib

def Server(url, *args, **kwargs):
   t = TimeoutTransport()
   t.timeout = kwargs.get('timeout', 20)
   if 'timeout' in kwargs:
       del kwargs['timeout']
   kwargs['transport'] = t
   server = xmlrpclib.Server(url, *args, **kwargs)
   return server

ServerProxy = Server

class TimeoutTransport(xmlrpclib.Transport):

   def make_connection(self, host):
       conn = TimeoutHTTP(host)
       conn.set_timeout(self.timeout)
       return conn


class TimeoutHTTPConnection(httplib.HTTPConnection):

   def connect(self):
       httplib.HTTPConnection.connect(self)
       self.sock.settimeout(self.timeout)


class TimeoutHTTP(httplib.HTTP):
   _connection_class = TimeoutHTTPConnection

   def set_timeout(self, timeout):
       self._conn.timeout = timeout
