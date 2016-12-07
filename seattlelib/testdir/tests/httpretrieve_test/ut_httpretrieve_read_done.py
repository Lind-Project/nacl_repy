# checks httpretrieves filelikeobj read returns a empty string when called after all
# content is received

# prints failed error msg if httpretrieve fails the test and excutes without printing
# if the test pass's



include httpretrieve.repy
include registerhttpcallback.repy



def server_test_read(httprequest_dictionary, http_query, http_post):
  # for this test the server should just act normal and send a http content
  return ['normal server', None]      



if callfunc == 'initialize':  
    
  # build temp server that acts normal and raise an excecption if the server failes 
  try:    
    handle = registerhttpcallback('http://127.0.0.1:12345', server_test_read)
  except Exception, e:
    raise Exception('Server failed internally ' + str(e))  

  try:
    filelikeobj = httpretrieve_open('http://127.0.0.1:12345/')
    # read all content from server
    filelikeobj.read()
    # this should return a emty string because the server content is already read
    read_after_done = filelikeobj.read()

  # catch any Exception and print failed msg 
  except Exception, e: 
    print 'Failed: shouldnt have raise an exception when read was called after sever is done sending content'

  else:
    # check it the read after content was done is empty string  
    if read_after_done != '':
      print 'Failed should have returned an emtpy string, returned: ' + str(read_after_done)  

  finally:
    stop_registerhttpcallback(handle)
