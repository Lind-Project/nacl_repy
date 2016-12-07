# checks if httpretrieve recieves raises an timeout exception when the server donesnt
# send http conent  

# prints failed error msg if httpretrieve failes the test and excutes without printing
# if the test passes


include httpretrieve.repy



def runhttpserver(ip, port, sock, thiscommhandle, listencommhandle):
  try:
    # recieve the http client request 
    client_request(sock)
    # send a httpresponse including http header with no http content
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
  # sends http header with no conent to check if the httpretrieve timout works  
  httpheader = 'HTTP/1.1 200 Ok\n\n'
  # send the http content and http header to http retrieve
  sock.send(httpheader)
  # normal server will send the content followed by closing the conneciton


if callfunc == 'initialize':
  # wait for a connection and start up the http server(that doesnt send http content)   
  listencommhandle = waitforconn('127.0.0.1', 12345, runhttpserver)

  # prints this failed msg if the http retrieve doesnt raise HttpContentLengthError 
  failed_error_msg = 'Failed: HttpContentReceivingError should have raised timeout exception' 

  try:
    # start up http retrieve to retieve the content from http server
    recv_msg = httpretrieve_get_string('http://127.0.0.1:12345/', timeout=30)

  #catch the right Exception if there is a different exception print failed_error_msg
  except HttpContentReceivingError, e:
    # check if the error message is correct    
    if 'Timeout Error on receiving content' not in str(e): 
      print failed_error_msg + ' :Raised: ' + str(e)
    pass  
  except Exception, e:
    print failed_error_msg + ' :Raised: ' + str(e)  
  else:
    print failed_error_msg    
  stopcomm(listencommhandle)
