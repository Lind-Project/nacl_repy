# checks if filelikeobj read called with a limit higher than the actual content of the
# server excute without raising an exception. 

# prints failed error msg if httpretrieve failes the test and excutes without printing
# if the test passes



include httpretrieve.repy
include registerhttpcallback.repy



def server_test_read(httprequest_dictionary, http_query, http_post):
  # for this test the server should just act normal and send a http content
  return ['normal server', None]



if callfunc == 'initialize':  
    
  # build temp server that acts normal and raise an excecption if the server fails 
  try:    
    handle = registerhttpcallback('http://127.0.0.1:12345', server_test_read)
  except Exception, e:
    raise Exception('Server failed internally ' + str(e))  

  try:
    filelikeobj = httpretrieve_open('http://127.0.0.1:12345/')
    # server will send less than a 1000 charactors as the http content, this should'nt
    # raise an exception, it should just return a emtpy string 
    read_after_done = filelikeobj.read(1000)

  # catch any Exception and print the failed msg  
  except Exception, e: 
    print 'Failed: shouldnt have raise an exception, Raised: ' + str(e)

  else:
    # the read didnt raise an exception, thus the test passed
    if read_after_done != 'normal server':
      print 'Failed: the file like obj read didnt receive the right content'
      print 'Receieved: ' + read_after_done
      print 'Server sent: normal server'  

  finally:
    # stop the server from waiting for more connections
    stop_registerhttpcallback(handle)
