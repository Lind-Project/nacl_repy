# tests if the http post and query arguments are similar to what is sent from a client


# prints failed message if the test failes and raises an exception the registorhttpcallback
# or httpretrieve raises an exception and just excutes if the test passes


include registerhttpcallback.repy
include httpretrieve.repy



def test_normal_server(httprequest_dictionary, http_query, http_post):
  # normal server just sends a message

  #copy the received query and post, which is used check 
  mycontext['received_http_query'] = http_query
  mycontext['received_http_post'] = http_post

  return [' ', None]
   
    
if callfunc == 'initialize':
  # used to copy the query and the post that the server received  
  mycontext['received_http_query'] = {}
  mycontext['received_http_post'] = {}

  try:
    # set up a normal server   
    handle = registerhttpcallback('http://127.0.0.1:12345', test_normal_server)
  except Exception, e: 
    raise Exception()

  # data to post as query and post to a server
  http_query = {"First": "1st", "Second": "2nd"}
  http_post = {"Third": "3rd", "Fourth": "4th"}

  try:
    httpretrieve_get_string('http://127.0.0.1:12345', http_query, http_post)
  except Exception, e:
    raise Exception('http retrieve failed on retrieving data from server')  
  else:
    if mycontext['received_http_query'] != http_query:
      print 'query failed'
      print 'sent query dict was ' + str(http_query)
      print 'received query dict was ' + str(mycontext['received_http_query'])

    if mycontext['received_http_post'] != http_post:
      print 'post failed'
      print 'sent query dict was ' + str(http_query)
      print 'received query dict was ' + str(mycontext['received_http_post'])    
      
  finally:
    #stop sever
    stop_registerhttpcallback(handle)
