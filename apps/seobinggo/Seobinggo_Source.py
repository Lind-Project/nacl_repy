
dy_import_module_symbols('rsa')
dy_import_module_symbols('advertise')
dy_import_module_symbols('httpserver')

"""
<Name>
  Seobinggo - P2P Backup System for Seattle

<Author>
  YoonSung Hong

<Date & Version>
  Feb 8: Beta 0.1(Before commit)
  Feb 8 ~ UI is scheduled for improvement
  
<Purpose>
  User of Seattle can backup their files anywhere in the cloud use this software 
  through very simple UI on web-browsers as well as retrieve their back up files.
  Backup files are stored both locally and other peers in real time.

<Prerequisite>
  .publickey file must exist in the working directory. Obtain '.publickey' from
  Seattle Geni.

<Data Files>
  localbackuplist.txt:
    saves list of files saved locally.
    @Each line:  public key,original file name, backup file name, version
  
  nextfilenum.txt
    saves next backup file number. backup files are save as file1, file2, file3...
    in order they are saved. 
  
  backupversionlist.txt
    save list of sets that maps original files names to their latest version. One
    file cannot have two listings.
    @Each line:  original file nmae,latest version number.
    
<Global Variables>
  'pubkey':
      My public key from *.publickey in the working directory.
      
  'prvkey':
      My private key from *.privatekey in the working directory.
      
  'VER':
      Verstion information that maps original file name to latest corresponding 
      version number. No same file allows to be in the 'VER' dictionary.
     
<Uses>
  1. Start Seobinggo using repy: python repy.py <restriction file> seobinggo.repy
  2. When Sebinggo prompts 'Ready', browse 127.0.0.1 through your favorite web 
     browser.
  3. You can backup files to any peer node availabe in Seattle and retrieve them
     as you wish.
     
<Experiments & Tests>
  If you are interested in learning how P2P works or experimenting how Seobinggo
  behave, it is suggested to use virtual machine to simulate two peer system. For
  example, you can run a virtual machine software such as Virtual Box and run Seo
  binggo in the virtual environment. Now you have controls on two OS at the same 
  time as well as two different Seobinggo instances on the top of the OS. Make 
  sure to have different public keys. 

<Limitation>
  1. Currently, Seobinggo does not support seash environment.
  2. File transfer for peer to peer is limited to 10 MB.
  
<Known Issues>
  1. SendAll: file transfer failed to tranfer big data. Small chunks are fine.
"""



def log_webServer(request):
  try:
    return webServer(request)
  except Exception,e:
    log("webServer function had uncaught exception!\nTraceback:\n",getlasterror(),"\n")
    raise


def webServer(request):
  """
  <Purpose>
    Runs a web server on 127.0.0.1. This is UI for Seobinggo. UI have three
    functionalities. First, file-backup by uploading a file. Second, retrieve
    file backed up. Third, display latest distribution of back-up files in
    local working folder and peer storages.
    
  <Funtionalities>
    <Upload>
      Upload uses POST. webServer has POST data handling that specifically
      design to handle back-up reqeust.
      
    <Retrieve>
      Files are retrieved through browser. File names will be randomly 
      generated when retrieving. 
      
    <Display>
      1. My public key and ip information
      2. My backup files stored in the local working folder.
      3. My backup files stored in peers(real-time)
      
  <UI>
    Currently, super basic html that handles three functionalities.
    UI is scheduled to change.
    
  <Exception>
    None. Exceptions are handled in httpserver.repy.
    
  <Return>
    dictionary(header + content). Look at httpserver.repy. 
  """
  
  
  """
    <File Retrieve Handling>
  """
  # Receive client request from the browser and save in a dictionary form.  
  querydict = request['querydict']
  
  # File Transfer Request though query request.
  retrieved_file = None
  if querydict:
    retrieved_file = queryRequestProcess(querydict)

  
  """
    <File Upload & Post-data Handling>
  """  
  # Uploaded file backup through POST request & Post data handling
  if request['verb'] == 'POST':
    posted_data = request['datastream'].read()
    postDataProcess(posted_data)
    
  
  """
    <UI>
  """  
  htmlfrontpage = frontPageUI()


  # Header + Content sent to client(web-browser)
  res = {}
  res["version"] = "1.1"
  res["statuscode"] = 200
  res["statusmsg"] = "OK"
  if retrieved_file == None:
    res["headers"] = {"Content-Type": "text/html"}
    res["message"] = htmlfrontpage
  else:
    res["headers"] = {"Content-Type": "application/download"}
    res["message"] = retrieved_file
  
  return res




"""
  <Purpose>
    Front page users will see through a web browser. Contents of this page
    must be wrapped with html tags.
  <Exception>
    None
  <Return>
    Html tag that will shown as front page of Seobinggo.
"""
def frontPageUI():
  # Heading
  html = """<html>
            <h1>Seobinggo</h1>
            <h4>P2P Backup System for Seattle</h4>
         """
         
  # public key load
  html += "<p>My Public Key: "
  pub_key = mycontext['pubkey']
  html += pub_key + "</p><hr />"
  
  # My ip and port
  myip = getmyip()
  port = 12345
  
  # My key, ip info
  html += "<h3>My Information</h3>"
  for n in advertise_lookup(pub_key):
    html += n
  html += "<hr />"
  
  # able to upload file
  html += """<form method='POST' enctype='multipart/form-data' action='/'> 
             File to upload: <input type=file name=upfile><input type=submit value=Upload>
             </form> 
          """
  
  # my file in local
  html += "<hr /><h3>My Files in Local</h3>"
  html += showMyLocalFileList()
  
  # my file in peers(real time)
  html += "<hr /><h3>My Files in Peer Real Time</h3>"
  html += showMyFileListPeersReal()
  
  
  # Tail Info
  html += """<HR />Seobinggo 0.1 for Seattle. YoonSung Hong. hys235@cs.washington.edu"""

  return html





def showMyLocalFileList():
  """
  <Purpose>
    
    <Generic>
      HTML UI wrapper for getMyLocalFileList. 
    
    <Current Implementation>
      Display the latest file from the file lists returned from getMyLocalFileList.
      
  <Return>
    HTML Tag in a string.
     
  <Exception>
    None
  """
  
  
  # List of my local files.
  mylocalfilelist = getMyLocalFileList(mycontext['pubkey']) 
  
  """
  # Keep track of latest version of each file.
  latestfiledict = dict()    
  
  # Traverse each file info from the file list and update latestfiledict.
  for fileinfo in mylocalfilelist:
    
    filename, version, backupfilename, pub_key = fileinfo
    if (filename in latestfiledict):
      dictfilename, dictversion, dictbackupfilename, dictpubkey = latestfiledict[filename]
    else:
      dictversion = 0
      
    # Update laterfiledict to keep it latest for each file.
    if filename in latestfiledict:
      if version > dictversion:
        latestfiledict[filename] = (filename, version, backupfilename, pub_key)
    else:
      latestfiledict[filename] = (filename, version, backupfilename, pub_key)
  """
  
  latestfiledict = _latestFileDict(mylocalfilelist, "local")
  
  # Create a link to the file. User will be able to download the file on a web browser.
  result_html = ""
  for fileinfo in latestfiledict:
    filename, version, backupfilename, pub_key = latestfiledict[fileinfo]
    result_html += "<a href = \"./?lc_filename=" + backupfilename + "\">" + filename + "</a>" + "<br />"
    
  return result_html



  



def showMyFileListPeersReal():
  """
  <Purpose>
    HTML UI, List of lastest(version) of my files in peer nodes.
    
  <Return>
    HTML hyper-link list
    
  <Exception>
    None
  """
  
  
  # Resultant UI list of files in html.
  result_html = ''
  
  # Create a link to the backup file in peer node(retrieval purpose).
  filelistdict = getMyFileListPeersReal()
  for fileinfo in filelistdict:
    filename, version, backupfilename, peerpubkey = filelistdict[fileinfo]
    result_html += "<a href = \"./?peer=" + peerpubkey + "&pr_filename=" + backupfilename + "\">" + filename + "</a><br />"
  
  return result_html





def getMyLocalFileList(pubkey):
  """
    <Purpose>
      Examine localbackuplist.txt. Returns a list of local files belongs to my public key.
    
    <Returns>
      A list of local files belongs to the public key.
     
      Each element in the list contains a tuple like following.
        (original filename, version, stored filename, public key)
    
    <Exception>
      None.
  """
  
  
  # Open localbackup list.
  fileobj = open('localbackuplist.txt')
  
  # List of files stored locally that belongs to the pubkey.          
  result = []            
  
  # Read each line from the file.           
  line = fileobj.readline()
  while line:
    retrievedPubkey, retrievedOrgFilename, retrievedBackupFilename, retrievedVersion = line.split(",")  
    # Matches with the pubkey -> append to result list.
    if (retrievedPubkey == pubkey):
      result.append((retrievedOrgFilename, retrievedVersion, retrievedBackupFilename, retrievedPubkey))
    line = fileobj.readline() 
  
  fileobj.close()
  
  return result






def getMyFileListPeersReal():  
  """
  <Purpose>
    Create a list(dictionary) of latest(version) files stored in 
    peer nodes.
    
  <Return>
    A dictionary of my files stored in peers.
      Key    : original file name
      Value  : tuple(stored_filename, peer_public_key, version)
      
  <Exception>
    None
  """
  
  
  # File list will be returned.
  latestfiledict = dict()
  
  # List of peers running Seobinggo in real time.
  peerlist = getPeerList()
  
  for peer in peerlist: 
    # Search my backup files on other peers except me.
    if peer != mycontext['pubkey']:

      # Takes first of multiple address info belongs to a peer.  
      peeraddressinfo = advertise_lookup(peer)[0]
      
      # Peer not registered. False Alarm. 
      if peeraddressinfo == ['']:
        break;
          
      # [pubkey, ip, port]
      peerinfo = peeraddressinfo.split(",")
      
      # Open connection with a peer.
      targetip, targetport = peerinfo[1], int(peerinfo[2])
      try:
        conn = openconn(targetip, targetport)
      except Exception:
        raise Exception("Connection error with a peer")
        
      # Request file list that belong to my public key.
      try:
        conn.send("#" + mycontext['pubkey'])
      except Exception:
        raise Exception("Failed to request to a peer")
        
      # String of my files saved in other peer.
      # 10 MB is transaction is reasonable for file list data.
      try:
        filelistdata = conn.recv(10000000)
      except Exception:
        raise Exception("Fail to receive data from a peer")
        filelistdata = ''
      
      conn.close()
      
      # Split raw data into a list of files. Last line is an empty line(removed).
      filelistlines = filelistdata.split("\n")
      filelistlines = filelistlines[:len(filelistlines)-1]
      
      # One latest file for each original file saved in a dictionary.
      latestfiledict = _latestFileDict(filelistlines, "peer")  
        
  return latestfiledict




def _latestFileDict(list, type):
  """
    <Purpose>
      Create a list of files with their latest version. Each file will be listed 
      only one time(one with latest version). this is used by get*FileList()
    <Arguments>
      List of files.
        Local:
          filename, version, backupfilename, pub_key
        Peer:
          mypubkey, filename, backupfilename, version, peerpubkey
    <Return>
      dictionary that save information about the latest files from the argument
      list such as file name, version, backup file name, and file owner pub key.
  """
  
  # Keep track of latest version of each file.
  latestfiledict = dict()    
  
  # Traverse each file info from the file list and update latestfiledict.
  for fileinfo in list:
    
    if (type == "local"): #showMyLocalFileList()
      filename, version, backupfilename, pub_key = fileinfo
    elif (type == "peer"): #getMyFileListPeersReal()
      mypubkey, filename, backupfilename, version, peerpubkey = fileinfo.split(",")
      pub_key = peerpubkey
    else:
      raise Exception("Fileinfo has wrong number of arguments in _latestFileDict") 
      break
    
    if (filename in latestfiledict):
      dictfilename, dictversion, dictbackupfilename, dictpubkey = latestfiledict[filename]
    else:
      dictversion = 0
      
    # Update laterfiledict to keep it latest for each file.
    if filename in latestfiledict:
      if version > dictversion:
        latestfiledict[filename] = (filename, version, backupfilename, pub_key)
    else:
      latestfiledict[filename] = (filename, version, backupfilename, pub_key)

  return latestfiledict



def requestPeerFileTransfer(peer, filename):
  """
  <Purpose>
    Retrieve a file from a peer.
    
  <Argument>
    peer:
      A peer's public key where file is retrieved from
    filename:
      A file name that will be retrieved from the peer's node.
      
  <Exception>
    None.
    
  <Return>
    Retrieved data in string.
  """
  
  
  # Look for peer's address
  peer_list = getPeerList()
  
  # If public key has space and passed through query, spaces are replaced by %.
  peer = peer.replace("%", " ")
  
  # Open connection with a peer
  peerip = getPeerIp(peer)
  try:
    conn = openconn(peerip, 12345) # default file transfer port: 12345
  except Exception:
    log("could not connect to peer to request file transfer\n")
    raise NameError("ConnectionError")
    
  conn.send("$"+filename) # request a specific file.
  
  # Retrieve requested file data
  #file_data = conn.recv(10000000)
  try:
    #filedata = recvAll(conn)
    filedata = conn.recv(100000)
  except Exception:
    raise Exception("Could not retrieve data from a peer")
    filedata = "Retrieve Error"
    
  conn.close()
  
  return filedata






def queryRequestProcess(querydict):
  """
    <Purpose>
      Retrieve a file at either at local or peer node as the use request through UI.
    
    <Argument>
      Querydict:
        A dictionary generated by 'httpserver.repy'. It contains a client request to
        the server such as GET query. 
    
    <Return>
      File content returned in a string.
  """
  
  
  retrievedfile = None
  # Read local file request and return the file through a browser.
  if 'lc_filename' in querydict:
    # open the local file.
    localfilename = querydict['lc_filename']
    fileobj = open(localfilename)
    retrievedfile = fileobj.read()
    fileobj.close()
  elif 'peer' in querydict and 'pr_filename' in querydict:
    # open the file at the peer node.
    retrievedfile = requestPeerFileTransfer(querydict['peer'], querydict['pr_filename'])
  else:
    # Wrong query pattern. Cannot be processed.
    pass
  
  # Decryption
  retrievedfile = dataDecrypt(retrievedfile)
  
  return retrievedfile



def postDataProcess(rawdata):
  """
    <Purpose>
      Posted data is passed from httpsever. This function appropriately separate header information
      contains such as file name and pure content in raw data and call update function to back up the 
      uploaded file by the user.
      
    <Argument>
      rawdata:
        raw data from htpserver.repy. A string chunk contains header information such as file
        name and the content of file in string.
    
    <Return> 
      None.
  """
  
  # Posted datastream process. Retrieve filename and content.
  rawdatalines = rawdata.splitlines(True)
  datainfo = rawdatalines[1].split(" ")
  
  # Retrieve file name from the posted raw data.
  filenametemp = ''
  # File names separeted by space must combine together.
  for partialfilename in datainfo[3:]:
    filenametemp += partialfilename + ' '
  
  # Clean up extra spaces at the tail.   
  filenametemp = filenametemp.rstrip()
  # filename="...". Only need ... part.
  filename = filenametemp[10:len(filenametemp)-1]
  
  # File contents are all lines of raw data except header information.
  puredatalines = rawdatalines[4:len(rawdatalines)-1] 
  filecontent = ''
  for puredataline in puredatalines:
    filecontent += puredataline
  
  # Encryption
  filecontent = dataEncrypt(filecontent)
    
  # Backup the uploaded file in local and peer storages(if peers available)
  update(filename, filecontent)



def dataEncrypt(content):
  pub_key = rsa_string_to_publickey(mycontext['pubkey'])
  prv_key = rsa_string_to_privatekey(mycontext['prvkey'])
  
  if rsa_is_valid_publickey(pub_key) and rsa_is_valid_privatekey(prv_key):
    if rsa_matching_keys(prv_key, pub_key):
      result = rsa_encrypt(content, pub_key)
    else:
      raise Exception("Public key and private key cannot be used together")
  else:
    raise Exception("Public key or private is/are not valid")
  
  return result



def dataDecrypt(content):
  pub_key = rsa_string_to_publickey(mycontext['pubkey'])
  prv_key = rsa_string_to_privatekey(mycontext['prvkey'])
  
  if rsa_is_valid_publickey(pub_key) and rsa_is_valid_privatekey(prv_key):
    if rsa_matching_keys(prv_key, pub_key):
      result = rsa_decrypt(content, prv_key)
    else:
      raise NameError("public key and private key cannot be used together")
  else:
    raise NameError("public key or private is/are not valid")
  
  return result



def startGossip(sockobj): #ip,port,sockobj,thiscommhandle,listencommhandle): 
  """
    <Purpose>
      File transfer agent/server/protocol. It handles some requests 
      such as ?, # and $.
    <Request Handling>
      ?:
        A peer asking for local back up. If local space is enough 
        'OK' sign is sent to the peer. Received format: ?size. For
        example, ?1000.
      #:
        A peer asking for his backup files in my local directory.
        The list(String) of his files are returned.
      $:
        A peer asking for one of his backup files in my local directory.
        If the file exist, the file is returned to the peer. 
    <Return>
      None
  """
  ip,port = sockobj.getpeername()
  
  # Socket liimit.
  receive_limit = 1000000
  
  try: 
    mes = sockobj.recv(receive_limit)    
  except Exception, e:
    log("could not receive requests\n")
  else:
    # peer asks for local back up.
    if mes[0] == '?':
      # format: ?filesize > ?30
      filesize = mes[1:]
      _askPeerEnoughSpace(sockobj, filesize)
    
    # peer asks for list of local files belong to the peer.    
    elif mes[0] == '#':
      # format: #,peerpubkey > #,1234
      peerpubkey = mes[1:]
      _askListOfPeerFiles(sockobj, peerpubkey)
    
    # a peer asks for his file stored locally.    
    elif mes[0] == '$':
      # backupfilename in local directory.
      backupfilename = mes[1:]
      _returnPeerFile(sockobj, backupfilename)
      
    # Undefined sign. 
    else:
      pass
      
  
  sockobj.close()






def _askPeerEnoughSpace(sockobj, filesize):
  receivelimit = 100000
  if int(filesize) < receivelimit:
    sockobj.send('OK')
    
    # File information received.
    tempinforcv = sockobj.recv(receivelimit)
    peerfileinfo = tempinforcv.split(",")
    
    # Backup in the local directory.
    filecontent = sockobj.recv(receivelimit)
    localPeerBackup(peerfileinfo, filecontent)

  else:
    # File size is larger than the limit.
    sockobj.send('Denied') 






def _askListOfPeerFiles(sockobj, peerpubkey):
  try:
    fileobj = open('localbackuplist.txt', 'r')
  except IOError:
    # localbackuplist.txt does not exist
    sockobj.send('')
  else:
    # Create a list of peer's file stored locally.
    peerfilelist = ''
    
    # Create a list. 
    # Each line saves: peer pubkey, backup file name, version, my pubkey
    line = fileobj.readline()
    while line:
      if line.strip() != '':
        peerfilelist += line.rstrip() + "," + mycontext['pubkey'] + "\n"
      line = fileobj.readline()
    
    fileobj.close()
    
    # Send back with the list of files belongs to the pub key.
    #sockobj.send(peerfilelist)
    log(peerfilelist,"\n")
    try:
      sendAll(sockobj, peerfilelist)
    except Excetpion:
      raise Exception("Fail to send peer file list in _askListOfPeerFiles()")


def _returnPeerFile(sockobj, backupfilename):
  # Open the requested backup file
  try:
    fileobj = open(backupfilename, 'r')
  except IOError:
    # if file not found, "File Not Found" returned.
    filedata = "File Not Found"
  else:
    filedata = fileobj.read()
  
  fileobj.close()
  
  # Send back the file content
  #sockobj.send(filedata)
  try:
    sendAll(sockobj, filedata)
  except Exception:
    raise Exception("faile to send file data to owner node")


def localPeerBackup(peerfileinfo, filecontent):
  """
  <Purpose>
    Allows peer to backup files in my directory.
  <Exception>
    None.
  <Return>
    None.
  """
  
  # Decode peer file info
  peerpubkey, peerfilename, peerfileversion = peerfileinfo
  
  # Create new file(backup). Backup file name scheme: file#
  newbackupfilenum = getNextBackupFileNum()
  newbackupfilename = "file" + str(newbackupfilenum)

  # Back up file in my directory with new storage name.
  fileobj = open(newbackupfilename)
  fileobj.write(filecontent)
  fileobj.close()
  
  # Update the localbackuplist.txt
  fileobj = open('localbackuplist.txt')
  fileobj.seek(0,False) # Seek to end

  # Query = peerpubkey, peer file name, backup file name, version.
  query = peerpubkey + "," + peerfilename + "," + newbackupfilename + "," + peerfileversion+"\n"
  fileobj.write(query)
  fileobj.close()
  




def update(filename, filecontent):
  """
    <Purpose>
      Backup a file both locally and on peer's node if available. Also, appropriate
      database files are updated such as localbackuplist.txt.
      
    <Exception>
      None.
      
    <Return>
      None.
  """
  
  
  # Local Backup process
  localBackup(filename, filecontent)
  
  # Peer Backup process
  peerBackup(filename, filecontent)




  
def localBackup(filename, content):
  """
    <Purpose>
      Back up the content to local working directory. Updates the backup information
      in 'localbackuplist.txt'. Every bakcup file is saved as file* where * is number
      in the local working directory.
      
    <Argument>
      file_name: 
        the original file name.
      content: 
        content of the original file.
      
    <Return>
      True if success.
  """
  
  
  # Assign appropriate version base upon the original file name.
  versionlist = mycontext['VER']
  try:
    version = versionlist[filename] 
    newversion = int(version) + 1
  except KeyError:
    newversion = 1
    
  # Update version information for the file.
  versionUpdate(filename)
  
  # New backupfile name such as file1, file2, file3...fileN.
  newbackupfilenum = getNextBackupFileNum()
  newbackupfilename = "file" + str(newbackupfilenum)
  
  # Create new backupfile.
  fileobj = open(newbackupfilename)
  fileobj.write(content)
  fileobj.close()
  
  # Update the localbackuplist.txt (appending)
  fileobj = open('localbackuplist.txt')
  fileobj.seek(0,False)
  
  # pubkey, filename, newbackupfilename, newversion >> localbackuplist.txt
  query = mycontext['pubkey'] + "," + filename + "," + newbackupfilename + "," + str(newversion)+"\n"
  fileobj.write(query)
  fileobj.close()

  # Local backup process is sucessful.
  return True





def peerBackup(filename, filecontent):
  """
    <Purpose>
      Backup a file in peer storage.
      
    <Argumetn>
      filename:
          Saved as this file name.
      filecontent:
          String of file content.
    
    <Exception>
      Connection Error:
          Socket fail to communicate with peer node. It raise an exception.
          
    <Return>
      None
      
  """
  
  
  # List of Peer running Seobinggo.
  peerlist = getPeerList()
  
  # backup the file to all available peers.
  for peer in peerlist:
    
    # back up to other peer nodes.
    if peer != mycontext['pubkey']:
      #peer contact information. Need first thing in the returned list.
      peeraddress = advertise_lookup(peer)[0]
      
      # Peer not running Seobinggo. False alarm.
      if peeraddress == ['']:
        break;
      
      # a peer contact infromation in a list.
      peerinfo = peeraddress.split(",")
      peerpubkey, peerip, peerport = peerinfo
      
      # connect wit the peer.
      try:
        conn = openconn(peerip, int(peerport))
      except Exception, e:
        raise Exception("Could not connect to peer ip and peer port")
        break
      
      # File updated.
      filesize = len(filecontent)
      
      # Check with other peer if they have enough space.
      response = "DENIED"
      try:
        conn.send("?" + str(filesize))
        response = conn.recv(10000000)
      except Exception, e:
        raise Exception("Communication error in peerBackup()")
        break
      
      # Responsive is positive > send the file filecontent to back it up.
      if response == 'OK':
        # File information.
        version = mycontext['VER'][filename]
        # File information snet = mypubkey, filename, version
        query = mycontext['pubkey'] + "," +  filename + "," +version
        
        # Sending to the target peer.
        try:
          sendAll(conn, query)
          sendAll(conn, filecontent)
        except Exception, e:
          log("connection error sending\n")
        
      conn.close()





def versionUpdate(filename):
  """
    <Purpose>
      Update backupversionlist.txt with new backup file number.
      
    <Argument>
      file_name: 
          original file name.
      
    <Return>
      None
      
    <Note>
      backupversionlist.txt maps original file name and its latest version
      information. 
  """
  
  
  # Open database file for backup-version
  fileobj = open('backupversionlist.txt')
  versionlist = mycontext['VER']
  
  try:
    version = versionlist[filename]
  except KeyError:
    # First version for this file.
    query = filename + ",1\n"
    fileobj.write(query)
  else:    
    # Update version information.
    for eachfilename in versionlist:
      # Current version of this file.
      eachfileversion = versionlist[eachfilename]
      
      # Update version information if file names match.
      if eachfilename == filename:
        newversion = int(eachfileversion) + 1
        query = eachfilename + "," + str(newversion) + "\n"
        fileobj.write(query)
      else:
        query = eachfilename + "," + eachfileversion + "\n"
        fileobj.write(query)
        
  fileobj.close()
  
  # Construct new version list. Update mycontext['VER']
  constructVersionList()
 
 
 
 
 
 
def constructVersionList():
  """
    <Purpose>
      Make sure mycontext['VER'] is up-to-date. It guarantees to have
      the right version during file back-up process. This functions is
      called as Seobinggo starts to make sure version for backed up files
      are up-to-date.
      
    <Returns>
      None
      
    <Exception>
      None
        IOError: backupversionlist.txt not exist -> create an empty file.
    
    <Note>
      backupversionlist.txt maps original file name and its latest version.
  """
  
  
  try:
    fileobj = open('backupversionlist.txt')
  except IOError:
    # backupversionlist.txt not existing.
    fileobj = open('backupversionlist.txt')
    constructVersionList()
  else:
    line = fileobj.readline()
    while line:
      log(line,"\n")
      # Information each line contains.
      filename, version = line.split(",")
      
      versionlist = mycontext['VER']
      # sync mycontext['VER'] with the latest backupversionlist.txt
      versionlist[filename] = version
      
      line = fileobj.readline()   

  fileobj.close()




def getNextBackupFileNum():
  """
    <Purpose>
      Read current latest backup file number and update with next backup file number.
      
    <Exception>
      None.
      
    <Return>
      New file name in string.
      
    <Note>
      nextbackupfilenum.txt stores the latest backup file number.
      Backup file have name scheme like file1, file2, file3....fileN.
  """ 
  
   
  # Get latest backup file name in local disk such as file1.
  try:
    fileobj = open('nextbackupfilenum.txt') 
  except IOError:
    # nextbackupfilenum.txt not existing.
    fileobj = open('nextbackupfilenum.txt', 'w')
    getNextBackupFileNum()
  else:
    # Latest backup file name. 
    currentbackupfilenum = fileobj.read()
    fileobj.close()
    
    # No backup file exists
    if currentbackupfilenum == '':
      currentbackupfilenum = 0
    
    # Next backup file number updated(current + 1)  
    nextbackupfilenum = int(currentbackupfilenum) + 1
    fileobj = open('nextbackupfilenum.txt', 'w') 
    fileobj.write(str(nextbackupfilenum))
    
    fileobj.close()
  
  return nextbackupfilenum






def sendAll(sockobj, datastr):
  # Sends all the data in datastr to sock. If besteffort is True,
  # we don't care if it fails or not.
  
  amountsent = 0
  while amountsent < len(datastr):
    amountsent = amountsent + sockobj.send(datastr[amountsent:])






def recvAll(sockobj):
  # not working.
  
  # recv all the data in datastr to sock. If besteffort is True,
  # we don't care if it fails or not.
  lastdatasize = 0
  datastr = ''
  while 1:
    log("entered while loop", datastr, "\n")
    datastr = datastr + sockobj.recv(100000)
    log("entered while loop", datastr, "\n")
    if lastdatasize == len(datastr):
      log("size same", lastdatasize,"\n")
      break
    lastdatasize += len(datastr)
  
  return datastr



def log_err(funcname, content):
  """
    <Purpose>
      Log importance incidents like erros in sebinggolog.txt.
    
    <Argument>
      funcname:
          function name where the incident is caused.
      content:
          description of the incident.
    <Exception>
      None
    <Return>
      None
  """
  
  # not used but for later purpose.
  try:
    fileobj = open("sebinggolog.txt", "w")
  except IOError:
    raise LogError
  else:
    fileobj.write(funcname + " " + content)
     
     
             
             
              
              
              
def registerPubKey(pub_key, ip, port):
  """
    <Purpose>
      Register my public key as a key and my ip and port as values in advertise
      servers continuously. Lease is renewed every 120 seconds. This advertise allows
      other users running Seobinggo to openconn with this user. 

    <Arugment>
      pub_key:
        public key of this user.
      ip:
        ip address of this user.
      port:
        port opened for the file transfer.
      
    <Return>
      None
      
    <Exception>
      AdvertiseError:
        When one of advertise server is down. If one of servers are working, pass.
  """
  
  
  try:
    advertise_announce(pub_key, "P2P," + ip + "," + str(port) , 300)
  except AdvertiseError:
    pass
  settimer(120, registerPubKey, [pub_key, ip, port])






def registerSeobinggo(pub_key):
  """
    <Purpose>
      Register my public key to indicate Seobinggo is running with this public
      key. Lease is renewed every 120 seconds. 
    
    <Argument>
      pubkey:
        public will be registered as running Seobinggo.
      
    <Exception>
      AdvertiseError:
        When one of advertise server is down. If one of servers are working, pass.
      
    <Return>
      None.
  """
  
  
  try:
    advertise_announce("P2P", pub_key, 300)
  except AdvertiseError:
    pass
  settimer(120, registerSeobinggo, [pub_key])





def getPeerList():
  """
  <Purpose>
    Get list of peers running Seobinggo on Seattle.
    
  <Return>
    Return a list of peers on running Seobinggo in real time. An empty list
    is returned if no peer online including local user.
  """
  
  
  result = []
  # Seobinggo is flagged with P2P key on advertise servers.
  for peer in advertise_lookup("P2P"):
    result.append(peer)
    
  return result





def getPeerIp(peerpubkey):
  """
    <Purpose>
      Search for peer's ip from the announcing service with the peer's
      public key. (Peer is running Seobinggo as well)
      
    <Return>
      Peer's IP address in string. If peer's public key is not registered in 
      announcing service, return None
  """
  # Look up on the announcing service.
  rawdata = advertise_lookup(peerpubkey)
  
  peerip = None
  if rawdata != []:
    # raw data is list of advetises that has peerpubkey as key.
    temp = rawdata[0]
    peerinfo = temp.split(",")
    
    # Peer_info contains [pubkey, ip, port]
    peerip = peerinfo[1]
  
  return peerip





def getPubKey():  
  # Returns public key saved in *.publickey file.
  
  return _getKeyFromFile(".publickey")



def getPrvKey():
  # Returns private keyu saved in *.privatekey file.
  
  return _getKeyFromFile(".privatekey")



def _getKeyFromFile(ext):
  """
    <Purpose>
      Read my public key from *.publickey file. 
      
    <Exception>
      None
      
    <Return>
      public key in string. if not exist, return "None"
  """
  
  
  # Find .publickey file in the working directory.
  for filename in listdir(): 
    # file extension
    filetype = filename[(len(filename)-len(ext)):]
    
    # first file that has .publickey is opened
    if filetype == ext:
      # Open .publickey
      fileobj = open(filename)
      keyval = fileobj.read()
      fileobj.close()
      
      return keyval

  # No Such a file.
  return "None" 



def checkRequiredFile():
  """
    <Purpose>
      Check if localbackuplist.txt exit. This is one of required file for Seobinggo.
      Other required files are handled when they are called.
      
    <Exception>
      None
      
    <Return>
      None
  """
  
  
  try:
    file = open('localbackuplist.txt', 'r')
  except IOError:
    # localbackuplist.txt does not present. Create new one.
    file = open('localbackuplist.txt', 'w')
  else:
    pass
  
  file.close()




  
if callfunc=='initialize':
  # Check if required files present in the working directory.
  checkRequiredFile()
  
  # Start p2p UI on 127.0.0.1:12345
  webServerH = httpserver_registercallback(('127.0.0.1', 12345), log_webServer)
  
  # Retrieve local user's pubic key from the working directory.
  pub_key = getPubKey()
  prv_key = getPrvKey()
  mycontext['pubkey'] = pub_key
  mycontext['prvkey'] = prv_key
  
  # Load version information for all files.
  mycontext['VER'] = dict()
  constructVersionList()  
  
  # Construct File Transfer agent(server/protocol).
  myip = getmyip()
  port = 12345
  gossip = waitforconn(myip, port, startGossip)
  
  # Announce that local user joined p2p network.
  registerPubKey(pub_key, myip, port)     
  registerSeobinggo(pub_key)
  
  log("Start servicing Seobinggo on 127.0.0.1:12345\n")
  log("Ready, Rock & Roll!\n")

