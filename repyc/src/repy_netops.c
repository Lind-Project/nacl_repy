#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <repy.h>
#include <linux/limits.h>
#include <assert.h>

#include "util.h"
#include "repy_private.h"
#include "handle_storage.h"


repy_socket_handle repy_openconnection(char * destip, int destport, char * localip, int localport, double timeout) {
  CHECK_LIB_STATUS();
  if (destip == NULL || localip == NULL || destport < 0 || localport < 0 || timeout < 0) {
    return -1;
  }
  PyObject* instance, * params, *rc = NULL;
  instance = PyDict_GetItemString(client_dict, REPYC_API_OPENCON);

  params = Py_BuildValue("(sisid)", destip, destport, localip, localport, timeout);
  rc = PyObject_Call(instance, params, NULL );
  if (rc == NULL) {
    PyErr_Print();
    return -1;
  }
  repy_socket * sp = malloc(sizeof(struct repy_socket_s));
  sp->repy_python_socket = rc;
  return repy_ft_set_handle(sp);
}


repy_tcpserver_handle repy_listenforconnection(char * localip, int localport) {
  CHECK_LIB_STATUS();
  if (localip == NULL || localport < 0) {
    return -1;
  }
  PyObject* instance, * params, *rc = NULL;
  instance = PyDict_GetItemString(client_dict, REPYC_API_OPENTCP);

  params = Py_BuildValue("(si)", localip, localport);
  rc = PyObject_Call(instance, params, NULL );
  if (rc == NULL) {
    PyErr_Print();
    return -1;
  }
  repy_tcpserversocket * sp = malloc(sizeof(struct repy_tcpserversocket_s));
  sp->repy_python_socket = rc;
  return repy_ft_set_handle(sp);
}


void repy_closesocket(repy_socket_handle hp) {
  CHECK_LIB_STATUS();
  repy_socket* tofree = repy_ft_get_handle(hp);
  repy_ft_clear(hp);
  PyObject * rc = NULL;
  if (tofree == NULL || tofree->repy_python_socket == NULL)
    return;
  rc = PyObject_CallMethod(tofree->repy_python_socket, REPYC_API_CLOSE, NULL);
  if (rc == NULL) {
    PyErr_Print();
    return;
  }
  REF_WIPE(rc);
  PyObject * socket = (PyObject*) tofree->repy_python_socket;
  REF_WIPE(socket);
	
}


void repy_closesocketserver(repy_tcpserver_handle hp) {
  CHECK_LIB_STATUS();
  repy_tcpserversocket* tofree = repy_ft_get_handle(hp);
  repy_ft_clear(hp);
  PyObject * rc = NULL;
  if (tofree == NULL || tofree->repy_python_socket == NULL)
    return;
  rc = PyObject_CallMethod(tofree->repy_python_socket, REPYC_API_CLOSE, NULL);
  if (rc == NULL) {
    PyErr_Print();
    return;
  }
  REF_WIPE(rc);
  PyObject * socket = (PyObject*) tofree->repy_python_socket;
  REF_WIPE(socket);
	
}


long int repy_socket_send(char* message, repy_socket_handle hp) {
  CHECK_LIB_STATUS();
  repy_socket* sp = repy_ft_get_handle(hp);
  PyObject * rc = NULL;
  if (message == NULL || sp == NULL || sp->repy_python_socket == NULL)
    return -1;
  rc = PyObject_CallMethod(sp->repy_python_socket, REPYC_API_SOCKETSEND, "s", message);
  if (rc == NULL) {
    PyErr_Print();
    return -1;
  }

  return PyInt_AsLong(rc);

}


repy_socket_handle repy_tcpserver_getconnection(repy_tcpserver_handle  sh) {
  CHECK_LIB_STATUS();
  repy_tcpserversocket* server = repy_ft_get_handle(sh);
  if (server == NULL) {
    return -1;
  }
  PyObject * rc = NULL;

  rc = PyObject_CallMethod(server->repy_python_socket, "getconnection", NULL );
  if (rc == NULL) {
    PyErr_Print();
    return -1;
  }
  repy_socket * sp = malloc(sizeof(struct repy_socket_s));
  sp->repy_python_socket = PyTuple_GetItem(rc, 2);
  return repy_ft_set_handle(sp);
}


char * repy_socket_recv(int size, repy_socket_handle shp) {
  CHECK_LIB_STATUS();
  repy_socket* sp = repy_ft_get_handle(shp);
  if (sp == NULL) {
    return NULL;
  }
  PyObject * rc = NULL;
  rc = PyObject_CallMethod(sp->repy_python_socket,REPYC_API_SOCKETRECV ,"(i)", size, NULL );
  if (rc == NULL) {
    PyErr_Print();
    return NULL;
  }
  char * val = strdup(PyString_AsString(rc));
  REF_WIPE(rc);
  return val;
}


repy_udpserver_handle repy_listenformessage(char * localip, int localport) {
  CHECK_LIB_STATUS();
  if (localip == NULL || localport < 0) {
    return -1;
  }
  PyObject* instance, * params, *rc = NULL;
  instance = PyDict_GetItemString(client_dict, REPYC_API_OPENUDP);

  params = Py_BuildValue("(si)", localip, localport);
  rc = PyObject_Call(instance, params, NULL );
  if (rc == NULL) {
    PyErr_Print();
    return -1;
  }
  repy_udpserver * sp = malloc(sizeof(struct repy_udpserver_s));
  sp->repy_python_udpserver = rc;
  return repy_ft_set_handle(sp);
}

void repy_close_udpserver(repy_udpserver_handle hserver) {
  CHECK_LIB_STATUS();
  repy_udpserver* server = repy_ft_get_handle(hserver);
  repy_ft_clear(hserver);
  PyObject * rc = NULL;
  if (server == NULL || server->repy_python_udpserver == NULL)
    return;
  rc = PyObject_CallMethod(server->repy_python_udpserver, REPYC_API_CLOSE, NULL);
  if (rc == NULL) {
    PyErr_Print();
    return;
  }
  REF_WIPE(rc);
  PyObject * towipe = (PyObject*) server->repy_python_udpserver;
  REF_WIPE(towipe);
}


repy_message * repy_udpserver_getmessage(repy_udpserver_handle hserver) {
  CHECK_LIB_STATUS();
  repy_udpserver * server = repy_ft_get_handle(hserver);
  PyObject * rc = NULL;
  if (server == NULL || server->repy_python_udpserver == NULL)
    return NULL;
  rc = PyObject_CallMethod(server->repy_python_udpserver, REPYC_API_UDPGETMESSAGE, NULL);
  if (rc == NULL) {
    PyErr_Print();
    return NULL;
  }
  repy_message * retval = malloc(sizeof(struct repy_message_s));
  retval->message = strdup(PyString_AsString(PyTuple_GetItem(rc,2)));
  retval->ip = strdup(PyString_AsString(PyTuple_GetItem(rc,0)));
  retval->port = (int) PyInt_AsLong(PyTuple_GetItem(rc,1));
  REF_WIPE(rc);
  return retval;
}


long int repy_sendmessage(char * destip, int destport, char * message, char * localip, int localport ) {
  CHECK_LIB_STATUS();
  if (destip == NULL || message == NULL || localip == NULL) {
    return -1;
  }
  PyObject* instance, * params, *rc = NULL;
  instance = PyDict_GetItemString(client_dict, REPYC_API_SENDMESSAGE);
  params = Py_BuildValue("(sissi)",
			 destip,
			 destport,
			 message,
			 localip,
			 localport);
  rc = PyObject_Call(instance, params, NULL);
  REF_WIPE(params);
  long int val = PyInt_AsLong(rc);
  if (val == -1) {
    PyErr_Print();
  }
  REF_WIPE(rc);
  return val;
}
