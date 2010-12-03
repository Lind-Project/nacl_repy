# checks if httpretrieve raises an exception if http redirect header doesnt include the location
# to redirect to

# prints failed error msg if httpretrieve failes the test and excutes without printing
# if the test passes



include httpretrieve.repy



def runhttpserver(ip, port, sock, thiscommhandle, listencommhandle):
  try:
    # recieve the http client request 
    client_request(sock)
    # send a httpresponse including http header(redirect with no location) and http content
    httpresponse(sock)  
  except Exception, e:
    print 'Error while running the webserver:  ' + str(e)


def client_request(client_conn):
  # recieve the http client request(not used in this context because
  # we assume httpretrieve always requests 'GET') 
  msg_recvd = ""
  while True:
    temp_recvd = client_conn.recv(1)
    msg_recvd += temp_recvd
    if '\r\n\r\n' in msg_recvd: 
      break 
    if '\n\n' in msg_recvd:
      break    


def httpresponse(sock):
  # sends response to http retrieve with a content length longer than the http header content length  
  httpheader = 'HTTP/1.1 301 Moved Permanently\r\n\r\n'
  # normal server should include the http redirect location over here 

  httpcontent = 'will not give the http redirect location' 
  # send the http content and http header to http retrieve
  sock.send(httpheader)
  sock.send(httpcontent) 
  sock.close()



if callfunc == 'initialize':
  # wait for a connection and start up the http server (that sends redirect header with no location)  
  listencommhandle = waitforconn('127.0.0.1', 12345, runhttpserver)

  # prints this failed msg if the http retrieve doesnt raise HttpContentLengthError 
  failed_error_msg = 'Failed: HttpHeaderFormatError should have raised the redirect location' 

  try:
    # start up http retrieve to retieve the content from http server
    recv_msg = httpretrieve_get_string('http://127.0.0.1:12345/')

  #catch the right Exception if there is a different exception print failed_error_msg
  except HttpBrokenServerError, e:
    pass  
  except Exception, e:
    print failed_error_msg + ' :Raised: ' + str(e)  
  else:
    print failed_error_msg    
  stopcomm(listencommhandle)
