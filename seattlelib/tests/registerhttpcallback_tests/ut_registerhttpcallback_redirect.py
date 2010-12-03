# tests a if the registorhttpcallback with a correct redirect works right and redirects
# to the new location

# prints failed message if the test failes and raises an exception the registorhttpcallback
# or httpretrieve raises an exception and just excutes if the test passes


include registerhttpcallback.repy
include httpretrieve.repy


def test_redirect(httprequest_dictionary, http_query, http_post):
  # server that redirects to a different server(http://127.0.0.2:12345)   
  raise HttpError302('http://127.0.0.2:12345')

def test_redirected(httprequest_dictionary, http_query, http_post):
 # normal server that sends a content  
 return [mycontext['redirect_content'], None]  

    
if callfunc == 'initialize':
  # msg sent when redirect is makes a connection to server
  mycontext['redirect_content'] = 'Normal server'

  try:
    # register the callback that should redirect to http://127.0.0.2:12345 
    redirecting_handle = registerhttpcallback('http://127.0.0.1:12345', test_redirect)
    # the first server will redirect to this server, and this server just acts
    # as a normal server and just send content
    redirected_handle = registerhttpcallback('http://127.0.0.2:12345', test_redirected)
    
  except Exception, e:
    # raise an exception if any one of the servers fail
    raise Exception('failed test: server raised an exception: ' + str(e))
    
  
  # send a request to receive the content sent from redirecting server
  try:  
    recvd_content = httpretrieve_get_string('http://127.0.0.1:12345') 
  except Exception, e:  
    print 'httpretrieve raised an exception: ' + str(e)
  else:
    # check if the redirect content matchs the actual sent content.   
    if recvd_content != mycontext['redirect_content']:  
      print 'failed: didnt redirect to the right server'
      print 'received content: ' + recvd_content
      print 'redirect content: ' + mycontext['redirect_content']

  finally:
    # stop the servers
    stop_registerhttpcallback(redirecting_handle)
    stop_registerhttpcallback(redirected_handle)
