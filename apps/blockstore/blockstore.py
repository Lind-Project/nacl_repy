"""
Author: Armon Dadgar
Description:
  File storage program with HTTP interface
"""

# Import the rsa library
rsa = dy_import_module("rsa")
pageserver = dy_import_module("pageserver", additional_globals=LIBREPY_EXPORTS)

# This array holds the public and private keys
# Each entry is of the type (filename, RSA key dict)
KEYS = [None, None]

# This flag is checked every once in a while
# to signal a clean termination
SHOULD_STOP = [False]

# This is the file used to store the data in
DATA_INDEX_FILENAME = "BLOCKSTORE_INDEX"
DATA_STORE_FILENAME = "BLOCKSTORE_DATA"
DATA_FILES = [None, None]
DATA_FILES_LOCK = Lock()

# Cache the file index
FILE_INDEX = {}


#### Initialization functions

def get_encryption_keys(args):
  """Gets the encryption keys to use"""
  if len(args) != 2:
    log("Bad invokation!\nusage: blockstore KEYNAME LISTEN_PORT\n")
    return False

  specified = args[0]
  pub_file_name = specified + ".publickey"
  prv_file_name = specified + ".privatekey"
  try:
    pub_file = open(pub_file_name, "r", False)
    prv_file = open(prv_file_name, "r", False)
  except FileNotFoundError, e:
    log("Public/Private key files not found!\nError: ", e)
    return False
  except:
    log("Fatal Error!\nError: ", e)
    return False

  # Read in the data
  pub_key_str = pub_file.read()
  prv_key_str = prv_file.read()
  
  # Convert to a key
  try:
    pub_key = rsa.rsa_string_to_publickey(pub_key_str)
    prv_key = rsa.rsa_string_to_privatekey(prv_key_str)
  except Exception, e:
    log("Error reading keys!\nError: ",e)
    return False

  # Store these
  KEYS[0] = (pub_file_name, pub_key)
  KEYS[1] = (prv_file_name, prv_key)
  return True


def get_listen_port(args):
  """Gets the port to listen on from argument array"""
  specified = args[1]
  try:
    port = int(specified)
  except:
    log("Specified listen port is not valid\n")
    return None

  lim, use, stops = getresources()
  if port not in lim["connport"]:
    log("Specified listen port is not allowed.\n Allowed port:",lim["connport"],"\n")
    return None

  return port


def initialize_datastore():
  """Initializes the data store"""
  try:
    DATA_FILES[0] = open(DATA_INDEX_FILENAME)
  except Exception,e:
    log("Fatal error opening the data index file!\nError: ", e)
    return False

  try:
    DATA_FILES[1] = open(DATA_STORE_FILENAME)
  except Exception,e:
    log("Fatal error opening the data store file!\nError: ", e)
    return False

  # Data files are ready to go
  return True


#### Page Handlers

def default_landing_page(request_dict):
  """Default landing page"""
  body = "<html><head><title>Data Storage: Home</title></head><body><h1>Data Storage: Home</h1>"
  body += "<h5>Encryption Keys: "+KEYS[0][0]+" (pub) "+KEYS[1][0]+" (prv) </h5>"
  body += "<iframe frameborder='0' src='/data/files.html'><p>IFrames not supported!</p></iframe>"
  body += "<p><a href='/upload/index.html'>Upload new file</a></p>"
  body += "<p><a href='/stop/index.html'>Check the server termination status</a></p>"
  body += "</body></html>"
  return {"body":body}


def stop_page(request_dict):
  """Page for showing status, and controling clean stop"""

  # Check for the "stop" get argument, signal stop
  if "stop" in request_dict["GET_ARGS"]:
    SHOULD_STOP[0] = True

  # Generate the page
  body = "<html><head><title>Data Storage: Status</title></head><body><h1>Stop Status:</h1><p><b>"
  if SHOULD_STOP[0]:
    body += "Clean termination signaled!"
  else:
    body += "Termination not signaled."
  body += "</b></p><br><p><a href='/stop/index.html?stop'>Click to signal termination</a></p></body></html>"

  # Return the response
  return {"body":body}


def list_files(request_dict):
  """Lists the files in a table"""
  
  body = "<table border='1'><tr><th>Filename</th><th>File Size</th><th>File Index</th></tr>"

  if len(FILE_INDEX) > 0:
    files = FILE_INDEX.keys()
    files.sort()

    for file in files:
      info = FILE_INDEX[file]
      body += "<tr><td><a href='/down/index.html?file="+file+"'>"+file+"</a></td><td>"+str(info[0])+"</td><td>"+str(info[1])+"</td></tr>"
  else:
    body += "<tr><td colspan='3'>No Files Stored</td></tr>"

  body += "</table>"

  return {"body":body}
    

def upload_page(request_dict):
  """Presents an upload page"""
  # Check the verb
  if request_dict["verb"] == "GET":
    body = "<html><head><title>Data Storage: Upload</title></head><body>"
    body += "<h1>Data Storage: Upload</h1>"
    body += "<form method='POST' enctype='multipart/form-data'>"
    body += "File Name: <input type='text' name='filename'></input><br>"
    body += "File: <input type='file' name='file'><br>"
    body += "<input type='submit' value='Upload'>"
    body += "</form></body></html>"

  else:
    # Buffer the entire POST'ed body
    form_data = pageserver.parse_form_data(request_dict)

    # Check if we got a file name, and file data
    if "filename" not in form_data or "file" not in form_data or form_data["filename"] == "" \
       or form_data["file"] == "":
      body = "<html><head><title>Data Storage: Upload</title></head><body>"
      body += "<h1>Data Storage: Upload</h1>"
      body += "<h4>Upload Failed! Bad POST fields!</h4>"
      body += "<p><a href='/'>Click to return to the home page.</a></p>"
      body += "</body></html>"

    else:
      filename = form_data["filename"].strip("\r\n")
      file_data = form_data["file"]

      # Store the file
      store_file(filename, file_data)

      body = "<html><head><title>Data Storage: Upload</title></head><body>"
      body += "<h1>Data Storage: Upload</h1>"
      body += "<h4>Upload succeeded!</h4>"
      body += "<p><a href='/'>Click to return to the home page.</a></p>"
      body += "</body></html>"

  return {"body":body}


def download_page(request_dict):
  """Handles a request to download a file"""
  # Check the arguments
  error = None
  if "file" not in request_dict["GET_ARGS"]:
    error = "No file specified!"
  else:
    file = request_dict["GET_ARGS"]["file"]
    if file not in FILE_INDEX:
      error = "Specified file does not exist!"

  # Check for an error
  if error is not None:
    body = "<html><head><title>Data Storage: Download</title></head><body>"
    body += "<h1>Data Storage: Download</h1>"
    body += "<h4>Download Failed! "+error+"</h4>"
    body += "<p><a href='/'>Click to return to the home page.</a></p>"
    body += "</body></html>"
    return {"body":body}

  # Otherwise, we can upload the file
  else:
    # Get the data
    data = get_file(file)

    # Download the file
    return {"body":data, "type":"application/x-download", "headers":{"Content-Disposition":"attachment; filename="+file}}


def setup_default_handlers():
  """Initializes the default request handlers"""
  # Add the welcome page
  pageserver.register_request_handler("GET", "/", default_landing_page)
  pageserver.register_request_handler("GET", "/index.html", default_landing_page)   

  # Add the page to stop the server
  pageserver.register_request_handler("GET", "/stop/index.html", stop_page)

  # Add the page to get the contents
  pageserver.register_request_handler("GET", "/data/files.html", list_files)

  # Add a page to handle uploads
  pageserver.register_request_handler("GET", "/upload/index.html", upload_page)
  pageserver.register_request_handler("POST", "/upload/index.html", upload_page)

  # Add a page to handle downloads
  pageserver.register_request_handler("GET", "/down/index.html", download_page)


#### Data store functions
"""
Data store info:
  The index file uses a fixed length entry for
  each file. There is a 10 character file length,
  a semi-colon, a 11 character index into the data store,
  a semi-colon, a 40 character file name, and a new line.
  This totals to 64 characters per entry.

  The storage file is a giant binary blob.
"""

def string_to_entry(s):
  """Converts a string to an entry"""
  length = int(s[0:10])
  index = long(s[11:22])
  filename = s[23:63].strip(" ")
  return (length,index,filename)


def entry_to_string(length,index,filename):
  """Converts an entry to a string"""
  length_s = "0"*10 + str(length)
  length_s = length_s[-10:]
  index_s = "0"*11 + str(index)
  index_s = index_s[-11:]
  filename = " "*40 + filename
  filename = filename[-40:]

  return length_s+";"+index_s+";"+filename+"\n"


def get_all_files():
  """
  Returns a dict of all the file names in the data store
  with their index and length
  """
  DATA_FILES_LOCK.acquire()
  index_file = DATA_FILES[0]
  index_file.seek(0)
  all_files = {}

  for entry in index_file:
    if entry == "\n": continue
    length,index,filename = string_to_entry(entry)
    all_files[filename] = (length, index)

  DATA_FILES_LOCK.release()

  return all_files


def store_file(name, data):
  """Stores a new data file"""
  # Encrypt the data
  data = rsa.rsa_encrypt(data, KEYS[0][1])
  data_len = len(data)

  index_file = DATA_FILES[0]
  data_file = DATA_FILES[1]
  DATA_FILES_LOCK.acquire()

  # Seek to the end of the files
  index_file.seek(0,False)
  data_file.seek(0, False)

  data_index = data_file.tell()

  # Make an entry for the file
  entry = entry_to_string(data_len, data_index, name)

  # Write to the index and data store
  index_file.write(entry)
  data_file.write(data)

  # Update the file index
  FILE_INDEX[name] = (data_len, data_index)

  DATA_FILES_LOCK.release()


def get_file(name):
  """Gets the contents of a given file"""
  # Check if the file exists
  if name not in FILE_INDEX:
    raise Exception("File does not exist!")

  # Get the info on the file
  length, index = FILE_INDEX[name]

  index_file = DATA_FILES[0]
  data_file = DATA_FILES[1]
  DATA_FILES_LOCK.acquire()
  
  # Seek to the data index
  data_file.seek(index)

  # Read the data in
  data = data_file.read(length)

  DATA_FILES_LOCK.release()

  # Decrypt the data
  data = rsa.rsa_decrypt(data, KEYS[1][1])

  # Return the file's data
  return data


#### Main Entry

def main(args):
  """
  Program entry
  args: first entry should be a string port to listen on
  """
  # Update the maximum cached disk blocks to 2M (512*4K)
  # for performance reasons
  libfile.set_max_cached_blocks(512)

  # Setup the encryption keys
  got_keys = get_encryption_keys(args)
  if not got_keys:
    return
  print "Using keys:",KEYS[0][0],KEYS[1][0]

  # Get the listener ports
  port = get_listen_port(args)
  if port is None:
    return

  # Initialize the data store
  is_setup = initialize_datastore()
  if not is_setup:
    return
  print "Index Size:",DATA_FILES[0].size()
  print "Data Size:",DATA_FILES[1].size()

  # Update the file index
  FILE_INDEX.update(get_all_files())
  print "File Index:", FILE_INDEX

  # Setup the HTTP page handlers
  setup_default_handlers()

  # Start the listeners
  stop_func = pageserver.setup_listener(port)
  log("Listening on",getmyip()+":"+str(port),"\n")

  # Define a function which checks if we should
  # terminate the webserver
  def check_stop():
    if SHOULD_STOP[0]:
      log("Stopping listeners...\n")
      stop_func()
      log("Waiting 5 seconds...\n")
      sleep(5)
      log("Flushing the data files...\n")
      DATA_FILES[0].close()
      DATA_FILES[1].close()
      log("Exiting\n")
      exitall()

  # Schedule this to run every 10 seconds
  runEvery(10, check_stop)


if callfunc == "initialize":
  main(callargs)

