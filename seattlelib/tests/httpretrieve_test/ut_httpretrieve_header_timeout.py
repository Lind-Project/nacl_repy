# checks if httpretrieve raises an timeout exception if the http header isnt sent by the server 

# prints failed error msg if httpretrieve fails the test and excutes without printing
# if the test pass's


include httpretrieve.repy
include registerhttpcallback.repy



def server_test_header_timeout(httprequest_dictionary, http_query, http_post):
  # build a server that takes too long to response to the httpretrieve

  # use a forever loop so the server acts as if the it failed(this will not send any http header)
  while True:
    pass    



if callfunc == 'initialize':  
    
  # build temp server that fails to send http header 
  try:    
    handle = registerhttpcallback('http://127.0.0.1:12345', server_test_header_timeout)
  except Exception, e:
    raise Exception('Server failed internally ' + str(e))  

  # use http retrieve to retrieve the content form the server and if the fuction failes to raise
  # a timeout exception, print failed_error_msg
  failed_error_msg = 'Failed: HttpContentReceivingError should have raised a timeout exception'
  try:
    recv_msg = httpretrieve_get_string('http://127.0.0.1:12345', timeout=5)  

  # catch the right Exception(HttpHeaderReceivingError) if there is a different exception print failed_error_msg
  except SocketTimeoutError, e:
    # check if the error message is correct    
    if 'Timeout Error on receiving header' not in str(e): 
      print failed_error_msg + ' :Raised: ' + str(e)  
  except Exception, e:
    print failed_error_msg + ' :Raised: ' + str(e)  
  else:
    print failed_error_msg

  finally:
    # stop the server from waiting for more connections
    stop_registerhttpcallback(handle)
    
