""" 
Author: Justin Cappos

Module: Node Manager request handler.   This securely handles a request from a 
        client.   It does not worry about how it gets the connection, 
        concurrency, etc.   It does worry about slow retrieval attacks, etc.

Start date: August 28th, 2008

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

I think this is fairly straightforward...   Get requests, check them, and
pass them to the appropriate API function
"""

from repyportability import *
  
import repyhelper

# repy signeddata to protect request information
repyhelper.translate_and_import("signeddata.repy")

# get requests (encapsulated in session messages)
repyhelper.translate_and_import("session.repy")

# for using time_updatetime
repyhelper.translate_and_import("time.repy")

# the API for the node manager
import nmAPI

# for socket.error
import socket

# for logging informative errors
import traceback



import servicelogger


def initialize(myip, publickey, version):
  
  # this allows requests to specify they should only be enacted by us (by 
  # public key which should be unique)
  #BUG FIX: we are storing rsa_publickey_to_string(publickey) instead of str(publickey) so that the entry is in the same format as 
  #the way the data is stored and used by the client
  signeddata_set_identity(rsa_publickey_to_string(publickey))

  # init the node manager's API (mostly for information it returns when a call
  # gets generic node information)

  # we return the node dict
  return nmAPI.initialize(myip, publickey, version)


  
# Armon: Safely closes a socket object
def safe_close(socket):
  try:
    socket.close()
  except:
    pass


# this takes a connection and safely processes the request.   
def handle_request(socketobj):


  try:
    # let's get the request...
    # BUG: Should prevent endless data / slow retrival attacks
    fullrequest = session_recvmessage(socketobj)
  
  # Armon: Catch a vanilla exception because repy emulated_sockets
  # will raise Exception when the socket has been closed.
  # This is changed from just passing through socket.error,
  # which we were catching previously.
  except Exception, e:
    # close if possible
    safe_close(socketobj)

    # I can't handle this, let's exit
    # BUG: REMOVE LOGGING IN PRODUCTION VERSION (?)
    servicelogger.log_last_exception()
    return

  # handle the request as appropriate
  try:
    retstring = process_API_call(fullrequest)

  # Bad parameters, signatures, etc.
  except nmAPI.BadRequest,e:
    try:
      session_sendmessage(socketobj, str(e)+"\nError")
    except:
      pass
    # Armon: Moved out from the same try/catch because if session_sendmessage fails
    # then, the socket would not be closed, this is to prevent leaks
    safe_close(socketobj)
    return

  # Other exceptions only should happen on an internal error and should be
  # captured by servicelogger.log
  except Exception,e:
    try:
      servicelogger.log_last_exception()
      session_sendmessage(socketobj,"Internal Error\nError")
    except:
      pass
    # Armon: Prevent socket leaks
    safe_close(socketobj)
    return
 
  
  # send any output from the command
  try:
    session_sendmessage(socketobj,retstring)
  except:
    pass
  
  # Prevent leaks
  safe_close(socketobj)




# I'm going to have a table that defines what to check for the calls.   
# The idea is to make the logic as clear as possible and punt the "decision 
# making" about what needs to be checked into the table.

# The format of a request is:
#    requesttype|arg1|arg2 ... 
# requests are protected using the signeddata mechanism, so a trailer contains
# the signature information

# Entries are key / values like requesttype: (numargs, whocanperform, function)
# request type is the string that identifies which request
# numargs is the number of args that the string must have
# whocanperform is either 'Public', 'User', 'Owner' and specifies the minimum
#               amount of privilege one must have to perform the action
# function is the function that should be called with the arguments

# NOTE: if whocanperform is 'User' or 'Owner' the first argument MUST be the
# vessel name...

# Calls that the node manager understands.   The key is the "call name"
# the value is a tuple with number of args, protection, and the actual function
API_dict = { \
  'GetVessels': (0, 'Public', nmAPI.getvessels), \
  'GetVesselResources': (1, 'Public', nmAPI.getvesselresources), \
  'GetOffcutResources': (0, 'Public', nmAPI.getoffcutresources), \
  'StartVessel': (2, 'User', nmAPI.startvessel), \
  'StopVessel': (1, 'User', nmAPI.stopvessel), \
  'AddFileToVessel': (3, 'User', nmAPI.addfiletovessel), \
  'ListFilesInVessel': (1, 'User', nmAPI.listfilesinvessel), \
  'RetrieveFileFromVessel': (2, 'User', nmAPI.retrievefilefromvessel), \
  'DeleteFileInVessel': (2, 'User', nmAPI.deletefileinvessel), \
  'ReadVesselLog': (1, 'User', nmAPI.readvessellog), \
  'ResetVessel': (1, 'User', nmAPI.resetvessel), \
  'ChangeOwner': (2, 'Owner', nmAPI.changeowner), \
  'ChangeUsers': (2, 'Owner', nmAPI.changeusers), \
  'ChangeOwnerInformation': (2, 'Owner', nmAPI.changeownerinformation), \
  'ChangeAdvertise': (2, 'Owner', nmAPI.changeadvertise), \
  'SplitVessel': (2, 'Owner', nmAPI.splitvessel), \
  'JoinVessels': (2, 'Owner', nmAPI.joinvessels), \
# obsoleted
#  'SetRestrictions': (2, 'Owner', nmAPI.setrestrictions) \
}


def process_API_call(fullrequest):

  callname = fullrequest.split('|')[0]

  if callname not in API_dict:
    raise nmAPI.BadRequest("Unknown Call")

  # find the entry that describes this call...
  numberofargs, permissiontype, APIfunction = API_dict[callname]
  
  # we'll do the signature checks first... (the signature needs to be stripped
  # off to get the args anyways)...

  if permissiontype == 'Public':
    # There should be no signature, so this is the raw request...
    if len(fullrequest.split('|')) < numberofargs-1:
      raise nmAPI.BadRequest("Not Enough Arguments")

    # If there are 3 args, we want to split at most 3 times (the first item is 
    # the callname)
    callargs = fullrequest.split('|',numberofargs)
    # return any output for the user...
    return APIfunction(*callargs[1:])

  else:
    # strip off the signature and get the requestdata
    requestdata, requestsignature = signeddata_split_signature(fullrequest)
    

    # NOTE: the first argument *must* be the vessel name!!!!!!!!!!!
    vesselname = requestdata.split('|',2)[1]

    if vesselname not in nmAPI.vesseldict:
      raise nmAPI.BadRequest('Unknown Vessel')

    # I must have something to check...
    if permissiontype == 'Owner':
      # only the owner is allowed, so the list of keys is merely that key
      allowedkeys = [ nmAPI.vesseldict[vesselname]['ownerkey'] ]
    else:
      # the user keys are also allowed
      allowedkeys = [ nmAPI.vesseldict[vesselname]['ownerkey'] ] + nmAPI.vesseldict[vesselname]['userkeys']

    # I need to pass the fullrequest in here...
    ensure_is_correctly_signed(fullrequest, allowedkeys, nmAPI.vesseldict[vesselname]['oldmetadata'])
    
    # If there are 3 args, we want to split at most 3 times (the first item is 
    # the callname)
    callargs = requestdata.split('|',numberofargs)
    
    #store the request signature as old metadata
    nmAPI.vesseldict[vesselname]['oldmetadata'] = requestsignature
    
    # return any output for the user...
    return APIfunction(*callargs[1:])






# Raise a BadRequest exception if it's not correctly signed...
def ensure_is_correctly_signed(fullrequest, allowedkeys, oldmetadata):

  # check if time_updatetime has been called, if not, call it
  try:
    time_gettime()
  except TimeError:
    time_updatetime(34612)
  
  # check if request is still valid and has not expired
  # this code has been added to resolve an issue where we are not checking of the request is expired in the case that there is no old metadata
  thesigneddata, signature = fullrequest.rsplit('!',1)
  junk, rawpublickey, junktimestamp, expiration, sequencedata, junkdestination = thesigneddata.rsplit('!',5)
  if not signeddata_iscurrent(float(expiration)):
    raise nmAPI.BadRequest,"Bad Signature on '"+fullrequest+"'"
    
  
  # check if sequence id is equal to zero in the case that there is no data. 
  # This is intended to fix a previous issue where any value could be used as a sequence id when there was no old metadata (only 0 is valid in this case)
  if (sequencedata!="None"):
    junksequecename,sequenceno = sequencedata.rsplit(':',1)
    if not oldmetadata:
      if int(sequenceno) != 0:
        raise nmAPI.BadRequest, "Illegal sequence id on '"+fullrequest+"'"
    
  # ensure it's correctly signed, if not report this and exit
  if not signeddata_issignedcorrectly(fullrequest):
    raise nmAPI.BadRequest,"Bad Signature on '"+fullrequest+"'"

  request, requestsignature = signeddata_split_signature(fullrequest)

  signingpublickey = signeddata_split(fullrequest)[1]

  # If they care about the key, do they have a valid key?
  if allowedkeys and signingpublickey not in allowedkeys:
    raise nmAPI.BadRequest('Insufficient Permissions')

  #bug fix: old metadata may be storing full requests, so we are using a crude way to check if the full request is stored, or if just the signature is
  metadata_is_fullrequest = False
  if not(oldmetadata==None):
    oldrawpublickey, oldrawtimestamp, oldrawexpiration, oldrawsequenceno, oldrawdestination, oldjunksignature = oldmetadata.rsplit('!',5)
    try:
      conversion_try = rsa_string_to_publickey(oldrawpublickey[1:])
    except ValueError:
      #we catch any exception here that occurs when trying to convert, and assume it is because we are dealing with a full request
      #catching the general exception is ok here since we will do this same conversion in shouldtrust
      metadata_is_fullrequest = True
  
  #BUG FIX: only signature should be passed in for oldmetadata since full request may take extensive space
  if metadata_is_fullrequest:
    (shouldtrust, reasons) = signeddata_shouldtrust(oldmetadata, fullrequest)
  else:
    (shouldtrust, reasons) = signeddata_shouldtrustmeta(oldmetadata, fullrequest)
    
  if not shouldtrust:
    # let's tell them what is wrong.
    raise nmAPI.BadRequest,"Signature problem: "+' '.join(reasons)
  else:
    # We should trust...  All is well!
    return


