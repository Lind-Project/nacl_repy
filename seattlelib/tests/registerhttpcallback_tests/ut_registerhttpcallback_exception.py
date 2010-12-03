# tests a if the registorhttpcallback sends correct error msg when excepion is raised in the callback function  


# prints failed message if the test failes and raises an exception the registorhttpcallback
# or httpretrieve raises an exception and just excutes if the test passes


include registerhttpcallback.repy
include httpretrieve.repy



def test_callbackfunc_error(httprequest_dictionary, http_query, http_post):
  # server that raises an exception    
  raise HttpError404('The file no longer exists')
   

    
if callfunc == 'initialize':

  try:
    # register the callback that should send http error 404  
    server_handle = registerhttpcallback('http://127.0.0.1:12345', test_callbackfunc_error)
    
  except Exception, e:
    # if the server fails at any point raise an excepion   
    raise Exception('failed test: server raised an exception: ' + str(e))
    
  
  # send a request to receive the content sent from the server
  try:  
    recvd_content = httpretrieve_get_string('http://127.0.0.1:12345') 
  except HttpError404, e:
    # check if the registorhttpcallback sent the right error msg
    if 'The file no longer exists' not in str(e):
      print 'failed test: server sent a different an error. Sent error: ' + str(e)
  except Exception, e:
    # if http retrieve raises a different exception print a filed msg  
    print 'httpretrieve raised an exception: ' + str(e)  

  finally:
    # stop the server
    stop_registerhttpcallback(server_handle)
