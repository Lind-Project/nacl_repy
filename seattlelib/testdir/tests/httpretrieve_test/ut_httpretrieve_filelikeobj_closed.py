# checks httpretrieves filelikeobj read raises an excepion when called after 
# file like object is closed 

# prints failed error msg if httpretrieve fails the test and excutes without printing
# if the test pass's



include httpretrieve.repy
include registerhttpcallback.repy



def server_test_filelikeobj(httprequest_dictionary, http_query, http_post):
  # for this test the server should just act normal because we are testing if the http retrieve raises an exception
  # when called after closed. 
  return ['normal server', None]     



if callfunc == 'initialize':  
    
  # build temp server that acts normal and raise an exception if the server fails
  try:    
    handle = registerhttpcallback('http://127.0.0.1:12345', server_test_filelikeobj)
  except Exception, e:
    raise Exception('Server failed internally ' + str(e))  

  # printed only if the test doesnt pass
  failed_error_msg = 'Failed: HttpContentReceivingError should have raised a timeout exception'
  try:
    filelikeobj = httpretrieve_open('http://127.0.0.1:12345/')
    filelikeobj.close()
    # this should raise an exception since filelikeobj is closed
    filelikeobj.read()

  #catch the right Exception(HttpUserInputError) if there is a different exception print failed_error_msg
  except ValueError, e:
    # check if the error message is correct    
    pass
  except Exception, e:
    print failed_error_msg + ' :Raised: ' + str(e)  
  else:
    print failed_error_msg
  
  finally:
    # stop the server from waiting for more connecitons
    stop_registerhttpcallback(handle)
