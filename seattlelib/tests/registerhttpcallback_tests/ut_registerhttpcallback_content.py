# tests a if the registorhttpcallback sends the content as of what the callback function returns

# prints failed message if the test failes and raises an exception the registorhttpcallback
# or httpretrieve raises an exception and just excutes if the test passes


include registerhttpcallback.repy
include httpretrieve.repy


def test_normal_server(httprequest_dictionary, http_query, http_post):
  # normal server just sends a message  
  return [mycontext['msg_sent'], None]
   

    
if callfunc == 'initialize':
  # msg sent when client makes a connection to server
  mycontext['msg_sent'] = 'Normal server'

  try:
    # register the callback server that acts normal and send a content as of what the callback
    # function returns
    handle = registerhttpcallback('http://127.0.0.1:12345', test_normal_server)
  except Exception, e:
     raise Exception('failed test: server raised an exception: ' + str(e))

  else:
    # send a request to receive the content sent from the server
    try: 
      recvd_content = httpretrieve_get_string('http://127.0.0.1:12345') 
    except Exception, e:
      raise Exception('httpretrieve raised an exception: ' + str(e))

    else:
      # check if the content sent matches what the callback function sent  
      if recvd_content != mycontext['msg_sent']:
        print 'failed test the received content didnt match the content that was sent by registorhttpcallback'
        print 'server sent ' + mycontext['msg_sent']
        print 'cleint received ' + recvd_content
        
    finally: 
      # stop the server
      stop_registerhttpcallback(handle)
