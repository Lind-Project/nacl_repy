"""
Author: Armon Dadgar
Description:
  Very basic IP restriction security layer
"""

# Constant values for enforment level
DISABLED = 0          # Disables the layer
PREFERENCE_ONLY = 1   # Allowed IP's are favored (returned by getmyip())
ENFORCED = 2          # Only Allowed IPs permitted

# Sets the enforement level
ENFORCEMENT_LEVEL = ENFORCED

# Set of allowed IP's, specified in order of preference
ALLOWED_IPS = ["192.168.0.100", "127.0.0.1"]

def invalid_ip():
  raise AddressBindingError("Invalid local IP specified!")

def filtered_getmyip():
  # Check the mode
  if ENFORCEMENT_LEVEL == DISABLED:
    return getmyip()

  # Otherwise, use prefered IP's
  elif len(ALLOWED_IPS) > 0:
    return ALLOWED_IPS[0]

  # No internet otherwise
  else:
    raise InternetConnectivityError("No public facing IP address available!")

CHILD_CONTEXT_DEF["getmyip"] = {"type":"func",
                                "args":None,
                                "return":str,
                                "exceptions":InternetConnectivityError,
                                "target":filtered_getmyip}


def filtered_sendmessage(destip, destport, message, localip, localport):
  # Check the mode
  if ENFORCEMENT_LEVEL in (DISABLED,PREFERENCE_ONLY) or localip in ALLOWED_IPS:
    return sendmessage(destip, destport, message, localip, localport)
  invalid_ip()

CHILD_CONTEXT_DEF["sendmessage"] = {"type":"func",
                                    "args":(str,int,str,str,int),
                                    "return":int,
                                    "exceptions":RepyException,
                                    "target":filtered_sendmessage}


def filtered_listenformessage(localip, localport):
  if ENFORCEMENT_LEVEL in (DISABLED,PREFERENCE_ONLY) or localip in ALLOWED_IPS:
    return listenformessage(localip, localport)
  invalid_ip()

CHILD_CONTEXT_DEF["listenformessage"] = {"type":"func",
                                         "args":(str,int),
                                         "return":"any",
                                         "exceptions":RepyException,
                                         "target":filtered_listenformessage}


def filtered_openconnection(destip, destport, localip, localport, timeout):
  if ENFORCEMENT_LEVEL in (DISABLED,PREFERENCE_ONLY) or localip in ALLOWED_IPS:
    return openconnection(destip, destport, localip, localport, timeout)
  invalid_ip()

CHILD_CONTEXT_DEF["openconnection"] = {"type":"func",
                                       "args":(str,int,str,int,(int,long,float)),
                                       "return":"any",
                                       "exceptions":RepyException,
                                       "target":filtered_openconnection}


def filtered_listenforconnection(localip, localport):
  if ENFORCEMENT_LEVEL in (DISABLED,PREFERENCE_ONLY) or localip in ALLOWED_IPS:
    return listenforconnection(localip,localport)
  invalid_ip()

CHILD_CONTEXT_DEF["listenforconnection"] = {"type":"func",
                                            "args":(str,int),
                                            "return":"any",
                                            "exceptions":RepyException,
                                            "target":filtered_listenforconnection}


# Dispatch the next module
secure_dispatch_module()

