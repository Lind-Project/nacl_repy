# checks if httpretrieve receives the right content as sent from the http server


# prints failed error msg if httpretrieve failes the test and just excutes if the
# if it pass's the test


include httpretrieve.repy
include registerhttpcallback.repy



def server_test_content(httprequest_dictionary, http_query, http_post):
  # build temp server that sends http content normaly 

  # return the content to check if the httpretrieve gets the same content 
  return [mycontext['httpcontent'], None]
  
  
       

if callfunc == 'initialize':

  # inorder to check if the http content sent from the server matchs the http content received by the
  # httpretrieve. we make a global temp http content used to check the content from both side. 
  mycontext['httpcontent'] = ''
  for i in range(1000):
    mycontext['httpcontent'] += str(i)  
    
  # build temp server that acts normally and sends content
  try:    
    handle = registerhttpcallback('http://127.0.0.1:12345', server_test_content)
  except Exception, e:
    raise Exception('Server failed internally ' + str(e))  

  else: 
    # use httpretrieve to retrieve the content form the server.  
    try:
      recv_msg = httpretrieve_get_string('http://127.0.0.1:12345')  
    except Exception, e:
      print 'Http retrieve failed on receiving content, Raised: ' + str(e)
      
    # check if the content sent form the server is the same as received by the http retrieve
    else:  
      if mycontext['httpcontent'] != recv_msg:
        print 'Failed: http response sent and received doesnt match'
        print 'Server SENT MESSAGE: ' + mycontext['httpcontent']  
        print 'Httpretrieve RECIEVED MESSAGE: ' + recv_msg

    finally:
      # stop the server from waiting for other requests
      stop_registerhttpcallback(handle)

