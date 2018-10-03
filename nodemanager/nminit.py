""" 
Author: Justin Cappos

Module: Node Manager initializer.   It initializes the state needed to run the
        node manager on the local node.   This would most likely be run by the
        installer.

Start date: September 10rd, 2008

This initializes the node manager for Seattle.   It sets up the starting 
resources, creates a configuration file, etc.

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

"""
from repyportability import *
_context = locals()
add_dy_support(_context)

# need to generate a public key
dy_import_module_symbols('rsa.r2py')

# need randomfloat...
import random
randomfloat = random.random


import os

import persist

import shutil

import glob

# embedded here.   Is this really the right thing to do?
justinpubkey = {'e':22599311712094481841033180665237806588790054310631222126405381271924089573908627143292516781530652411806621379822579071415593657088637116149593337977245852950266439908269276789889378874571884748852746045643368058107460021117918657542413076791486130091963112612854591789518690856746757312472362332259277422867, 'n':12178066700672820207562107598028055819349361776558374610887354870455226150556699526375464863913750313427968362621410763996856543211502978012978982095721782038963923296750730921093699612004441897097001474531375768746287550135361393961995082362503104883364653410631228896653666456463100850609343988203007196015297634940347643303507210312220744678194150286966282701307645064974676316167089003178325518359863344277814551559197474590483044733574329925947570794508677779986459413166439000241765225023677767754555282196241915500996842713511830954353475439209109249856644278745081047029879999022462230957427158692886317487753201883260626152112524674984510719269715422340038620826684431748131325669940064404757120601727362881317222699393408097596981355810257955915922792648825991943804005848347665699744316223963851263851853483335699321871483966176480839293125413057603561724598227617736944260269994111610286827287926594015501020767105358832476708899657514473423153377514660641699383445065369199724043380072146246537039577390659243640710339329506620575034175016766639538091937167987100329247642670588246573895990251211721839517713790413170646177246216366029853604031421932123167115444834908424556992662935981166395451031277981021820123445253}

# Vessels need to have a public key in order to be accessed
print "Generating user keys..."
keylen = 2 ** 10
publickeys = []

# Our unit tests need access to 4 guest users, from guest0...guest3
num_guests = 4

for i in range(num_guests):
  publickey, privatekey = rsa_gen_pubpriv_keys(keylen)
  publickeys.append(publickey)
  # The unit tests need access to these keys
  publickey_file = 'guest' + str(i) + '.publickey'
  privatekey_file = 'guest' + str(i) + '.privatekey'

  # We need to make sure the file that we're writing to doesn't yet
  # exist.
  for filename in (publickey_file, privatekey_file):
    # We shouldn't rely on querying if the files exist before
    # deleting, as someone can get to the file after we query
    # and before we delete.
    try:
      removefile(filename)
    except FileNotFoundError:
      pass

  rsa_publickey_to_file(publickey, publickey_file)
  rsa_privatekey_to_file(privatekey, privatekey_file)

( guest0pubkey,
  guest1pubkey,
  guest2pubkey,
  guest3pubkey) = publickeys


# This is the public key of the person who will control most of the resources.
controllerpubkey = {'e': 1515278400394037168869631887206225761783197636247636149274740854708478416229147500580877416652289990968676310353790883501744269103521055894342395180721167L, 'n': 8811850224687278929671477591179591903829730117649785862652866020803862826558480006479605958786097112503418194852731900367494958963787480076175614578652735061071079458992502737148356289391380249696938882025028801032667062564713111819847043202173425187133883586347323838509679062142786013585264788548556099117804213139295498187634341184917970175566549405203725955179602584979965820196023950630399933075080549044334508921319264315718790337460536601263126663173385674250739895046814277313031265034275415434440823182691254039184953842629364697394327806074576199279943114384828602178957150547925812518281418481896604655037L}



offcutresourcedata ="""# BUG: How do we come up with these values dynamically?
resource cpu .002
resource memory 1000000   # 1 MiB
resource diskused 100000 # .1 MiB
resource events 2
resource filewrite 1000
resource fileread 1000 
resource filesopened 1 
resource insockets 0
resource outsockets 0
resource netsend 0
resource netrecv 0
resource loopsend 0  # would change with prompt functionality (?)
resource looprecv 0
resource lograte 100 # the monitor might log something
resource random 0    # Shouldn't generate random numbers on our own
"""

bigresourcedata = """resource cpu .08
resource memory 100000000   # 100 MiB
resource diskused 80000000 # 80 MiB
resource events 50
resource filewrite 100000
resource fileread 100000
resource filesopened 10
resource insockets 10
resource outsockets 10
resource netsend 100000
resource netrecv 100000
resource loopsend 1000000
resource looprecv 1000000
resource lograte 30000
resource random 100
resource messport 11111
resource messport 12222
resource messport 13333
resource messport 14444
resource messport 15555
resource messport 16666
resource messport 17777
resource messport 18888
resource messport 19999
resource connport 11111
resource connport 12222
resource connport 13333
resource connport 14444
resource connport 15555
resource connport 16666
resource connport 17777
resource connport 18888
resource connport 19999

call gethostbyname_ex allow
call sendmess allow
call recvmess allow
call openconn allow
call waitforconn allow
call stopcomm allow                     # it doesn't make sense to restrict
call socket.close allow                 # let's not restrict
call socket.send allow                  # let's not restrict
call socket.recv allow                  # let's not restrict

# open and file.__init__ both have built in restrictions...
call open allow                         # can read / write
call file.__init__ allow                # can read / write
call file.close allow                   # shouldn't restrict
call file.flush allow                   # they are free to use
call file.next allow                    # free to use as well...
call file.read allow                    # allow read
call file.readline allow                # shouldn't restrict
call file.readlines allow               # shouldn't restrict
call file.seek allow                    # seek doesn't restrict
call file.write allow                   # shouldn't restrict (open restricts)
call file.writelines allow              # shouldn't restrict (open restricts)
call sleep allow                        # harmless
call settimer allow                     # we can't really do anything smart
call canceltimer allow                  # should be okay
call exitall allow                      # should be harmless 

call log.write allow
call log.writelines allow
call getmyip allow                      # They can get the external IP address
call listdir allow                      # They can list the files they created
call removefile allow                   # They can remove the files they create
call randomfloat allow                  # can get random numbers
call getruntime allow                   # can get the elapsed time
call getlock allow                      # can get a mutex
"""

smallresourcedata = """resource cpu 0.02
resource memory 30000000   # 30 MiB
resource diskused 20000000 # 20 MiB
resource events 15
resource filewrite 100000.0
resource fileread 100000.0
resource filesopened 5
resource insockets 5
resource outsockets 5
resource netsend 10000.0
resource netrecv 10000.0
resource loopsend 1000000.0
resource looprecv 1000000.0
resource lograte 30000.0
resource random 100.0
resource messport %s
resource messport %s
resource messport %s
resource messport %s
resource connport %s
resource connport %s
resource connport %s
resource connport %s

call gethostbyname_ex allow
call sendmess allow
call recvmess allow
call openconn allow
call waitforconn allow
call stopcomm allow                     # it doesn't make sense to restrict
call socket.close allow                 # let's not restrict
call socket.send allow                  # let's not restrict
call socket.recv allow                  # let's not restrict

# open and file.__init__ both have built in restrictions...
call open allow                         # can read / write
call file.__init__ allow                # can read / write
call file.close allow                   # shouldn't restrict
call file.flush allow                   # they are free to use
call file.next allow                    # free to use as well...
call file.read allow                    # allow read
call file.readline allow                # shouldn't restrict
call file.readlines allow               # shouldn't restrict
call file.seek allow                    # seek doesn't restrict
call file.write allow                   # shouldn't restrict (open restricts)
call file.writelines allow              # shouldn't restrict (open restricts)
call sleep allow                        # harmless
call settimer allow                     # we can't really do anything smart
call canceltimer allow                  # should be okay
call exitall allow                      # should be harmless 

call log.write allow
call log.writelines allow
call getmyip allow                      # They can get the external IP address
call listdir allow                      # They can list the files they created
call removefile allow                   # They can remove the files they create
call randomfloat allow                  # can get random numbers
call getruntime allow                   # can get the elapsed time
call getlock allow                      # can get a mutex
"""





def make_vessel(vesselname, pubkey, resourcetemplate, resourceargs):
  retdict = {'userkeys':[], 'ownerkey':pubkey, 'oldmetadata':None, 'stopfilename':vesselname+'.stop', 'logfilename':vesselname+'.log', 'statusfilename':vesselname+'.status', 'resourcefilename':'resource.'+vesselname, 'advertise':True, 'ownerinformation':'', 'status':'Fresh'}

  try:
    WindowsError

  except NameError: # not on windows...
    # make the vessel dirs...
    try:
      os.mkdir(vesselname)
    except OSError,e:
      if e[0] == 17:
        # directory exists
        pass
      else:
        raise

  else: # on Windows...

    # make the vessel dirs...
    try:
      os.mkdir(vesselname)
    except (OSError,WindowsError),e:
      if e[0] == 17 or e[0] == 183:
        # directory exists
        pass
      else:
        raise


  #### write the vessel's resource file...
  outfo = open(retdict['resourcefilename'],"w")
  # write the args into the resource data template
  outfo.write(resourcetemplate % resourceargs)
  outfo.close()
  
  return retdict



# lots of little things need to be initialized...   
def initialize_state():

  # first, let's clean up any existing directory data...
  for vesseldirectoryname in glob.glob('v[0-9]*'):
    if os.path.isdir(vesseldirectoryname):
      print 'Removing:',vesseldirectoryname
      shutil.rmtree(vesseldirectoryname)

  # initialize my configuration file.   This involves a few variables:
  #    seattle_installed -- signal that the installation succeeded
  #    pollfrequency --  the amount of time to sleep after a check when "busy
  #                      waiting".   This trades CPU load for responsiveness.
  #    ports         --  the ports the node manager could listen on.
  #    publickey     --  the public key used to identify the node...
  #    privatekey    --  the corresponding private key for the node...
  configuration = {}

  configuration['pollfrequency'] = 1.0

  # NOTE: I chose these randomly (they will be uniform across all NMs)...   
  # Was this wise?
  configuration['ports'] = [1224, 2888, 9625, 10348, 39303, 48126, 52862, 57344, 64310]

  print "Generating key..."
  keys = rsa_gen_pubpriv_keys(100)
  configuration['seattle_installed'] = True
  configuration['publickey'] = keys[0]
  configuration['privatekey'] = keys[1]
  configuration['service_vessel'] = 'v2'

  print "Writing config file..."
  # write the config file...
  persist.commit_object(configuration,"nodeman.cfg")

  # write the offcut file...
  outfo = open("resources.offcut","w")
  outfo.write(offcutresourcedata)
  outfo.close()

#  vessel1 = make_vessel('v1',controllerpubkey,bigresourcedata, []) 
  vessel1 = make_vessel('v1',controllerpubkey,smallresourcedata, ('12345','12346', '12347','12348','12345','12346','12347','12348')) 
  vessel2 = make_vessel('v2',justinpubkey,smallresourcedata, ('20000','20001', '20002','20003','20000','20001','20002','20003')) 
  vessel3 = make_vessel('v3',guest0pubkey,smallresourcedata, ('30000','30001', '30002','30003','30000','30001','30002','30003')) 
  vessel4 = make_vessel('v4',guest0pubkey,smallresourcedata, ('21000','21001', '21002','21003','21000','21001','21002','21003')) 
  vessel5 = make_vessel('v5',guest1pubkey,smallresourcedata, ('22000','22001', '22002','22003','22000','22001','22002','22003')) 
  vessel6 = make_vessel('v6',guest1pubkey,smallresourcedata, ('23000','23001', '23002','23003','23000','23001','23002','23003')) 
  vessel7 = make_vessel('v7',guest2pubkey,smallresourcedata, ('24000','24001', '24002','24003','24000','24001','24002','24003')) 
  vessel8 = make_vessel('v8',guest2pubkey,smallresourcedata, ('25000','25001', '25002','25003','25000','25001','25002','25003')) 
  vessel9 = make_vessel('v9',guest3pubkey,smallresourcedata, ('26000','26001', '26002','26003','26000','26001','26002','26003')) 
  vessel10 = make_vessel('v10',guest3pubkey,smallresourcedata, ('27000','27001', '27002','27003','27000','27001','27002','27003')) 
  

  vesseldict = {'v1':vessel1, 'v2':vessel2, 'v3':vessel3, 'v4':vessel4, 'v5':vessel5, 'v6':vessel6, 'v7':vessel7, 'v8':vessel8, 'v9':vessel9, 'v10':vessel10}

  print "Writing vessel dictionary..."
  # write out the vessel dictionary...
  persist.commit_object(vesseldict,"vesseldict")

  print "Done initializing state."








if __name__ == '__main__':
  initialize_state() 
