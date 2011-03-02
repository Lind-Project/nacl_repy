
#define REPYC_API_GETMYIP "getmyip"
#define REPYC_API_GETHOSTBYNAME "gethostbyname"
#define REPYC_API_GETRUNTIME "getruntime"
#define REPYC_API_GETRANDOMBYTES "randombytes"
#define REPYC_API_SLEEP "sleep"
#define REPYC_API_GETLOCK "createlock"
#define REPYC_API_LOCK_ACQUIRE "acquire"
#define REPYC_API_LOCK_RELEASE "release"
#define REPYC_API_LISTDIR "listfiles"
#define REPYC_API_OPEN "openfile"
#define REPYC_API_CLOSE "close"
#define REPYC_API_FLUSH "flush"
#define REPYC_API_WRITEAT "writeat"
#define REPYC_API_WRITELINES "writelines"
#define REPYC_API_SEEK "seek"
#define REPYC_API_READ "readat"
#define REPYC_API_READLINE "readline"
#define REPYC_API_EXITALL "exitall"
#define REPYC_API_REMOVEFILE "removefile"
#define REPYC_API_OPENCON "openconnection"
#define REPYC_API_OPENTCP "listenforconnection"
#define REPYC_API_SOCKETSEND "send"
#define REPYC_API_SOCKETRECV  "recv"
#define REPYC_API_SENDMESSAGE "sendmessage"
#define REPYC_API_OPENUDP "listenformessage"
#define REPYC_API_UDPGETMESSAGE "getmessage"

extern PyObject *client_dict;
extern PyObject * global_dict_b;
extern int repy_errno;

void CHECK_LIB_STATUS();
