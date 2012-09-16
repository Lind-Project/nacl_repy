"""
  Author: Justin Cappos
  Module: Network constants for Lind.   This is things like the #defines
          and macros.

  Start Date: January 14th, 2012

"""









################### Mostly used with socket() / socketpair()


# socket types...

SOCK_STREAM = 1    # stream socket
SOCK_DGRAM = 2     # datagram socket
SOCK_RAW = 3       # raw-protocol interface
SOCK_RDM = 4       # reliably-delivered message
SOCK_SEQPACKET = 5 # sequenced packet stream
SOCK_CLOEXEC = 02000000
SOCK_NONBLOCK = 0x4000


# Address families...

AF_UNSPEC = 0        # unspecified
AF_UNIX = 1          # local to host (pipes)
AF_LOCAL = AF_UNIX   # backward compatibility
PF_FILE = AF_UNIX    # common on Linux
AF_INET = 2          # internetwork: UDP, TCP, etc.
AF_IMPLINK = 3       # arpanet imp addresses
AF_PUP = 4           # pup protocols: e.g. BSP
AF_CHAOS = 5         # mit CHAOS protocols
AF_NS = 6            # XEROX NS protocols
AF_ISO = 7           # ISO protocols
AF_OSI = AF_ISO
AF_ECMA = 8          # European computer manufacturers
AF_DATAKIT = 9       # datakit protocols
AF_CCITT = 10        # CCITT protocols, X.25 etc
AF_SNA = 11          # IBM SNA
AF_DECnet = 12       # DECnet
AF_DLI = 13          # DEC Direct data link interface
AF_LAT = 14          # LAT
AF_HYLINK = 15       # NSC Hyperchannel
AF_APPLETALK = 16    # Apple Talk
AF_ROUTE = 17        # Internal Routing Protocol
AF_LINK = 18         # Link layer interface
pseudo_AF_XTP = 19   # eXpress Transfer Protocol (no AF)
AF_COIP = 20         # connection-oriented IP, aka ST II
AF_CNT = 21          # Computer Network Technology
pseudo_AF_RTIP = 22  # Help Identify RTIP packets
AF_IPX = 23          # Novell Internet Protocol
AF_SIP = 24          # Simple Internet Protocol
pseudo_AF_PIP = 25   # Help Identify PIP packets
pseudo_AF_BLUE = 26  # Identify packets for Blue Box - Not used
AF_NDRV = 27         # Network Driver 'raw' access
AF_ISDN = 28         # Integrated Services Digital Network
AF_E164 = AF_ISDN    # CCITT E.164 recommendation
pseudo_AF_KEY = 29   # Internal key-management function
AF_INET6 = 30        # IPv6
AF_NATM = 31         # native ATM access
AF_SYSTEM = 32       # Kernel event messages
AF_NETBIOS = 33      # NetBIOS
AF_PPP = 34          # PPP communication protocol
pseudo_AF_HDRCMPLT = 35 # Used by BPF to not rewrite headers in interface output routines
AF_RESERVED_36 = 36  # Reserved for internal usage
AF_IEEE80211 = 37    # IEEE 802.11 protocol
AF_MAX = 38

# protocols...

IPPROTO_IP = 0          # dummy for IP
IPPROTO_ICMP = 1        # control message protocol
IPPROTO_IGMP = 2        # group mgmt protocol
IPPROTO_GGP = 3         # gateway^2 (deprecated)
IPPROTO_IPV4 = 4        # IPv4 encapsulation
IPPROTO_IPIP = IPPROTO_IPV4        # for compatibility
IPPROTO_TCP = 6         # tcp
IPPROTO_ST = 7          # Stream protocol II
IPPROTO_EGP = 8         # exterior gateway protocol
IPPROTO_PIGP = 9        # private interior gateway
IPPROTO_RCCMON = 10     # BBN RCC Monitoring
IPPROTO_NVPII = 11      # network voice protocol
IPPROTO_PUP = 12        # pup
IPPROTO_ARGUS = 13      # Argus
IPPROTO_EMCON = 14      # EMCON
IPPROTO_XNET = 15       # Cross Net Debugger
IPPROTO_CHAOS = 16      # Chaos
IPPROTO_UDP = 17        # user datagram protocol
IPPROTO_MUX = 18        # Multiplexing
IPPROTO_MEAS = 19       # DCN Measurement Subsystems
IPPROTO_HMP = 20        # Host Monitoring
IPPROTO_PRM = 21        # Packet Radio Measurement
IPPROTO_IDP = 22        # xns idp
IPPROTO_TRUNK1 = 23     # Trunk-1
IPPROTO_TRUNK2 = 24     # Trunk-2
IPPROTO_LEAF1 = 25      # Leaf-1
IPPROTO_LEAF2 = 26      # Leaf-2
IPPROTO_RDP = 27        # Reliable Data
IPPROTO_IRTP = 28       # Reliable Transaction
IPPROTO_TP = 29         # tp-4 w/ class negotiation
IPPROTO_BLT = 30        # Bulk Data Transfer
IPPROTO_NSP = 31        # Network Services
IPPROTO_INP = 32        # Merit Internodal
IPPROTO_SEP = 33        # Sequential Exchange
IPPROTO_3PC = 34        # Third Party Connect
IPPROTO_IDPR = 35       # InterDomain Policy Routing
IPPROTO_XTP = 36        # XTP
IPPROTO_DDP = 37        # Datagram Delivery
IPPROTO_CMTP = 38       # Control Message Transport
IPPROTO_TPXX = 39       # TP++ Transport
IPPROTO_IL = 40         # IL transport protocol
IPPROTO_IPV6 = 41       # IP6 header
IPPROTO_SDRP = 42       # Source Demand Routing
IPPROTO_ROUTING = 43    # IP6 routing header
IPPROTO_FRAGMENT = 44   # IP6 fragmentation header
IPPROTO_IDRP = 45       # InterDomain Routing
IPPROTO_RSVP = 46       # resource reservation
IPPROTO_GRE = 47        # General Routing Encap.
IPPROTO_MHRP = 48       # Mobile Host Routing
IPPROTO_BHA = 49        # BHA
IPPROTO_ESP = 50        # IP6 Encap Sec. Payload
IPPROTO_AH = 51         # IP6 Auth Header
IPPROTO_INLSP = 52      # Integ. Net Layer Security
IPPROTO_SWIPE = 53      # IP with encryption
IPPROTO_NHRP = 54       # Next Hop Resolution
# 55-57: Unassigned
IPPROTO_ICMPV6 = 58     # ICMP6
IPPROTO_NONE = 59       # IP6 no next header
IPPROTO_DSTOPTS = 60    # IP6 destination option
IPPROTO_AHIP = 61       # any host internal protocol
IPPROTO_CFTP = 62       # CFTP
IPPROTO_HELLO = 63      # "hello" routing protocol
IPPROTO_SATEXPAK = 64   # SATNET/Backroom EXPAK
IPPROTO_KRYPTOLAN = 65  # Kryptolan
IPPROTO_RVD = 66        # Remote Virtual Disk
IPPROTO_IPPC = 67       # Pluribus Packet Core
IPPROTO_ADFS = 68       # Any distributed FS
IPPROTO_SATMON = 69     # Satnet Monitoring
IPPROTO_VISA = 70       # VISA Protocol
IPPROTO_IPCV = 71       # Packet Core Utility
IPPROTO_CPNX = 72       # Comp. Prot. Net. Executive
IPPROTO_CPHB = 73       # Comp. Prot. HeartBeat
IPPROTO_WSN = 74        # Wang Span Network
IPPROTO_PVP = 75        # Packet Video Protocol
IPPROTO_BRSATMON = 76   # BackRoom SATNET Monitoring
IPPROTO_ND = 77         # Sun net disk proto (temp.)
IPPROTO_WBMON = 78      # WIDEBAND Monitoring
IPPROTO_WBEXPAK = 79    # WIDEBAND EXPAK
IPPROTO_EON = 80        # ISO cnlp
IPPROTO_VMTP = 81       # VMTP
IPPROTO_SVMTP = 82      # Secure VMTP
IPPROTO_VINES = 83      # Banyon VINES
IPPROTO_TTP = 84        # TTP
IPPROTO_IGP = 85        # NSFNET-IGP
IPPROTO_DGP = 86        # dissimilar gateway prot.
IPPROTO_TCF = 87        # TCF
IPPROTO_IGRP = 88       # Cisco/GXS IGRP
IPPROTO_OSPFIGP = 89    # OSPFIGP
IPPROTO_SRPC = 90       # Strite RPC protocol
IPPROTO_LARP = 91       # Locus Address Resoloution
IPPROTO_MTP = 92        # Multicast Transport
IPPROTO_AX25 = 93       # AX.25 Frames
IPPROTO_IPEIP = 94      # IP encapsulated in IP
IPPROTO_MICP = 95       # Mobile Int.ing control
IPPROTO_SCCSP = 96      # Semaphore Comm. security
IPPROTO_ETHERIP = 97    # Ethernet IP encapsulation
IPPROTO_ENCAP = 98      # encapsulation header
IPPROTO_APES = 99       # any private encr. scheme
IPPROTO_GMTP = 100      # GMTP
IPPROTO_PIM = 103       # Protocol Independent Mcast
IPPROTO_IPCOMP = 108    # payload compression (IPComp)
IPPROTO_PGM = 113       # PGM
IPPROTO_SCTP = 132      # SCTP
IPPROTO_DIVERT = 254    # divert pseudo-protocol
IPPROTO_RAW = 255       # raw IP packet
IPPROTO_MAX = 256
# last return value of *_input(), meaning "all job for this pkt is done".
IPPROTO_DONE = 257








##################### Protocol families are derived from above...

PF_UNSPEC = AF_UNSPEC
PF_LOCAL = AF_LOCAL
PF_UNIX = PF_LOCAL           # backward compatibility
PF_FILE = PF_LOCAL           # used on Linux
PF_INET = AF_INET
PF_IMPLINK = AF_IMPLINK
PF_PUP = AF_PUP
PF_CHAOS = AF_CHAOS
PF_NS = AF_NS
PF_ISO = AF_ISO
PF_OSI = AF_ISO
PF_ECMA = AF_ECMA
PF_DATAKIT = AF_DATAKIT
PF_CCITT = AF_CCITT
PF_SNA = AF_SNA
PF_DECnet = AF_DECnet
PF_DLI = AF_DLI
PF_LAT = AF_LAT
PF_HYLINK = AF_HYLINK
PF_APPLETALK = AF_APPLETALK
PF_ROUTE = AF_ROUTE
PF_LINK = AF_LINK
PF_XTP = pseudo_AF_XTP      # really just proto family, no AF
PF_COIP = AF_COIP
PF_CNT = AF_CNT
PF_SIP = AF_SIP
PF_IPX = AF_IPX             # same format as AF_NS
PF_RTIP = pseudo_AF_RTIP    # same format as AF_INET
PF_PIP = pseudo_AF_PIP
PF_NDRV = AF_NDRV
PF_ISDN = AF_ISDN
PF_KEY = pseudo_AF_KEY
PF_INET6 = AF_INET6
PF_NATM = AF_NATM
PF_SYSTEM = AF_SYSTEM
PF_NETBIOS = AF_NETBIOS
PF_PPP = AF_PPP
PF_RESERVED_36 = AF_RESERVED_36
PF_MAX = AF_MAX



#################### max listen value
SOMAXCONN = 128




#################### for sendmsg and recvmsg

# These aren't the same as in Linux.   There is no MSG_NOSIGNAL, etc.
# Since I copied these from a Mac, these will be different than for Lind

MSG_OOB = 0x1
MSG_PEEK = 0x2
MSG_DONTROUTE = 0x4
MSG_EOR = 0x8
MSG_TRUNC = 0x10
MSG_CTRUNC = 0x20
MSG_WAITALL = 0x40
MSG_DONTWAIT = 0x80
MSG_EOF = 0x100
MSG_WAITSTREAM = 0x200
MSG_FLUSH = 0x400
MSG_HOLD = 0x800
MSG_SEND = 0x1000
MSG_HAVEMORE = 0x2000
MSG_NEEDSA = 0x10000
MSG_NOSIGNAL = 0x4000





#################### for shutdown()

SHUT_RD = 0
SHUT_WR = 1
SHUT_RDWR = 2





################### setsockopt / getsockopt...
SOL_SOCKET = 1
SO_DEBUG = 1
SO_REUSEADDR = 2
SO_TYPE = 3
SO_ERROR = 4
SO_DONTROUTE = 5
SO_BROADCAST = 6
SO_SNDBUF = 7
SO_RCVBUF = 8
SO_SNDBUFFORCE = 32
SO_RCVBUFFORCE = 33
SO_KEEPALIVE = 9
SO_OOBINLINE = 10
SO_NO_CHECK = 11
SO_PRIORITY = 12
SO_LINGER = 13
SO_BSDCOMPAT = 14
SO_REUSEPORT = 15
SO_PASSCRED = 16
SO_PEERCRED = 17
SO_RCVLOWAT = 18
SO_SNDLOWAT = 19
SO_RCVTIMEO = 20
SO_SNDTIMEO = 21

SO_SECURITY_AUTHENTICATION = 22
SO_SECURITY_ENCRYPTION_TRANSPORT = 23
SO_SECURITY_ENCRYPTION_NETWORK = 24

SO_BINDTODEVICE = 25

#/* Socket filtering */
SO_ATTACH_FILTER = 26
SO_DETACH_FILTER = 27

SO_PEERNAME = 28
SO_TIMESTAMP = 29
SCM_TIMESTAMP = SO_TIMESTAMP

SO_ACCEPTCONN = 30

SO_PEERSEC = 31
SO_PASSSEC = 34
SO_TIMESTAMPNS = 35
SCM_TIMESTAMPNS = SO_TIMESTAMPNS

SO_MARK = 36

SO_TIMESTAMPING = 37
SCM_TIMESTAMPING = SO_TIMESTAMPING

SO_PROTOCOL = 38
SO_DOMAIN = 39

SO_RXQ_OVFL = 40


# # More setsockopt / getsockopt

# SO_SNDBUF = 0x1001               # send buffer size
# SO_RCVBUF = 0x1002               # receive buffer size
# SO_SNDLOWAT = 0x1003             # send low-water mark
# SO_RCVLOWAT = 0x1004             # receive low-water mark
# SO_SNDTIMEO = 0x1005             # send timeout
# SO_RCVTIMEO = 0x1006             # receive timeout
# SO_ERROR = 0x1007             # get error status and clear
# SO_TYPE = 0x1008                 # get socket type
# SO_NREAD = 0x1020                # APPLE: get 1st-packet byte count
# SO_NKE = 0x1021                  # APPLE: Install socket-level NKE
# SO_NOSIGPIPE = 0x1022            # APPLE: No SIGPIPE on EPIPE
# SO_NOADDRERR = 0x1023            # APPLE: Returns EADDRNOTAVAIL when src is not available anymore
# SO_NWRITE = 0x1024               # APPLE: Get number of bytes currently in send socket buffer
# SO_REUSESHAREUID = 0x1025        # APPLE: Allow reuse of port/socket by different userids
# SO_NOTIFYCONFLICT = 0x1026       # APPLE: send notification if there is a bind on a port which is already in use
# SO_UPCALLCLOEEWAIT = 0x1027      # APPLE: block on close until an upcall returns
# SO_LINGER_SEC = 0x1080           # linger on close if data present (in seconds)
# SO_RESTRICTIONS = 0x1081         # APPLE: deny inbound/outbound/both/flag set
# SO_RESTRICT_DENYIN = 0x00000001  # flag for SO_RESTRICTIONS - deny inbound
# SO_RESTRICT_DENYOUT = 0x00000002 # flag for SO_RESTRICTIONS - deny outbound
# SO_RESTRICT_DENYSET = 0x80000000 # flag for SO_RESTRICTIONS - deny has been set
# SO_RANDOMPORT = 0x1082           # APPLE: request local port randomization
# SO_NP_EXTENSIONS = 0x1083        # To turn off some POSIX behavior
# SO_LABEL = 0x1010                # socket's MAC label
# SO_PEERLABEL = 0x1011            # socket's peer MAC label

TCP_NODELAY = 0x01           # don't delay send to coalesce packets
TCP_MAXSEG = 0x02            # set maximum segment size
TCP_NOPUSH = 0x04            # don't push last block of write
TCP_NOOPT = 0x08             # don't use TCP options
TCP_KEEPALIVE = 0x10         # idle time used when SO_KEEPALIVE is enabled
TCP_CONNECTIONTIMEOUT = 0x20 # connection timeout
PERSIST_TIMEOUT = 0x40       # time after which a connection in persist timeout
                             # will terminate.
                             # see draft-ananth-tcpm-persist-02.txt
TCP_RXT_CONNDROPTIME = 0x80  # time after which tcp retransmissions will be
                             # stopped and the connection will be dropped
TCP_RXT_FINDROP = 0x100      # When set, a connection is dropped after 3 FINs


# Use this to specify options on a socket.   Use the protocol with setsockopt
# to specify something for all sockets with a protocol
SOL_SOCKET = 1
SOL_TCP = IPPROTO_TCP
SOL_UDP = IPPROTO_UDP


POLLIN = 01  # There is data to read.
POLLPRI	= 02 #There is urgent data to read.
POLLOUT	= 04 # Writing now will not block.
POLLERR = 010 # Error condition.
POLLHUP =  020 # Hung up.
POLLNVAL =  040 # Invalid polling request.
