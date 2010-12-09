#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <repy.h>
#include <linux/limits.h>
#include <assert.h>

#include "util.h"
/** We only need to init python once, use this as a gaurd.  */
int is_init = 0;

/** The location of the RePyC API file.  */
char * path_to_repyc_python_binding = NULL;
/** The name of the repyc API file. */
const char * repy_fn = "repyc.py";

/** Contains the bound objects which constitiue the RePy API. */
static PyObject *client_dict = NULL;
static PyObject * global_dict_b = NULL;

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


void static inline CHECK_LIB_STATUS() {
	if (client_dict == NULL || is_init == 0) {
		printf("RepyC is not Currently initialized... Exiting.");
		fflush(stdout);
		exit(2);
	}
}


char * repy_getmyip() {
	PyObject * instnace, * rc;
	CHECK_LIB_STATUS();
	instnace = PyDict_GetItemString(client_dict, REPYC_API_GETMYIP);
	rc = PyObject_CallObject(instnace, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	char* temp = strdup(PyString_AsString(rc));
	REF_WIPE(rc);
	return temp;
}

char * repy_gethostbyname(char * name) {
	PyObject * instnace, * rc, * param;
	CHECK_LIB_STATUS();
	if( name == NULL) {
		return NULL;
	}
	param = Py_BuildValue("(s)", name);
	instnace = PyDict_GetItemString(client_dict, REPYC_API_GETHOSTBYNAME);
	rc = PyObject_CallObject(instnace, param);
	REF_WIPE(param);
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}

	char * new_string = strdup(PyString_AsString(rc));
	REF_WIPE(rc);
	return new_string;

}


double * repy_getruntime() {
	CHECK_LIB_STATUS();
	double * time = NULL;
	PyObject* instance, * rc;
	instance = PyDict_GetItemString(client_dict, REPYC_API_GETRUNTIME);
	rc = PyObject_CallObject(instance, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	time = (double*) malloc(sizeof(double));
	*time = PyFloat_AS_DOUBLE(rc);
	REF_WIPE(rc);

	return time;
}

void * repy_randombytes() {
	CHECK_LIB_STATUS();
	void * rbytes = NULL;
	PyObject* instance, * rc;
	instance = PyDict_GetItemString(client_dict, REPYC_API_GETRANDOMBYTES);
	rc = PyObject_CallObject(instance, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	rbytes = malloc(1024);
	memcpy(rbytes, PyString_AsString(rc), 1024);

	REF_WIPE(rc);

	return rbytes;
}

void repy_sleep(double seconds) {
	CHECK_LIB_STATUS();
	PyObject* instance, * params, *rc;
	instance = PyDict_GetItemString(client_dict, REPYC_API_SLEEP);
	params = Py_BuildValue("(d)", seconds);
	rc = PyObject_CallObject(instance, params);
	REF_WIPE(params);
	REF_WIPE(rc);
}



repy_lock * repy_createlock() {
	CHECK_LIB_STATUS();
	repy_lock * l = NULL;
	PyObject* instance, * rc;
	instance = PyDict_GetItemString(client_dict, REPYC_API_GETLOCK);
	rc = PyObject_CallObject(instance, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	l = (repy_lock*) calloc(1, sizeof(repy_lock));
	//lose the type so the API does not expose a python object
	l->python_lock = (void *) rc;

	return l;

}

void free_repy_lock(repy_lock * l) {
	CHECK_LIB_STATUS();
	REF_WIPE(l->python_lock);
	free(l);
}

int repy_lock_blocking_acquire(repy_lock* l) {
	CHECK_LIB_STATUS();
	//good idea to check type of l->python_lock here?
	PyObject  *rc;

	rc = PyObject_CallMethod(l->python_lock, REPYC_API_LOCK_ACQUIRE,
			"O",Py_True);
	if (rc == NULL) {
		PyErr_Print();
		return 0;
	}

	REF_WIPE(rc);
	return 1;
}


int repy_lock_nonblocking_acquire(repy_lock* l) {
	CHECK_LIB_STATUS();
	//good idea to check type of l->python_lock here?
	PyObject *rc;

	rc = PyObject_CallMethod(l->python_lock, REPYC_API_LOCK_ACQUIRE,
			"O",Py_False);
	if (rc == NULL) {
		PyErr_Print();
		return 0;
	}
	int got_lock = (rc == Py_True)?1:0;
	REF_WIPE(rc);
	return got_lock;

}


void repy_lock_release(repy_lock* l) {
	CHECK_LIB_STATUS();
	//good idea to check type of l->python_lock here?
	PyObject * rc;

	rc = PyObject_CallMethod(l->python_lock, REPYC_API_LOCK_RELEASE,
				NULL);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}

	REF_WIPE(rc);
	return;

}



char** repy_listfiles(int* num_entries) {

	PyObject * instnace, * rc;
	CHECK_LIB_STATUS();

	instnace = PyDict_GetItemString(client_dict, REPYC_API_LISTDIR);
	rc = PyObject_CallObject(instnace, NULL);

	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}

	int size = PyList_Size(rc);
	char ** list = (char**) calloc(size, sizeof(char*));
	int i;

	for (i = 0; i < size; i++) {
		PyArg_Parse(PyList_GetItem(rc,i),"s", &(list[i]) );
	}


	*num_entries = size;
	REF_WIPE(rc);
	return list;

}


repy_file * repy_openfile(char * filename, int create)  {
	CHECK_LIB_STATUS();
	if (filename == NULL) {
		return NULL;
	}
	repy_file * fp = NULL;
	PyObject* instance, * params, *rc = NULL;
	instance = PyDict_GetItemString(client_dict, REPYC_API_OPEN);
	PyObject * bool = (create)?Py_True:Py_False;
	params = Py_BuildValue("(sO)", filename, bool);
	rc = PyObject_Call(instance, params, NULL);
	REF_WIPE(params);

	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}

	fp = (repy_file *) malloc(sizeof(struct repy_file_s));

	fp->repy_python_file = rc;

	return fp;
}


void repy_close(repy_file * fp)  {
	CHECK_LIB_STATUS();
	if (fp == NULL || fp->repy_python_file == NULL) {
		return;
	}

	PyObject * params = NULL, *rc = NULL;


	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_CLOSE, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}

	REF_WIPE(params);
	REF_WIPE(rc);
	REF_WIPE(fp->repy_python_file);
	free(fp);
	return;

}



void repy_flush(repy_file * fp)  {
	CHECK_LIB_STATUS();

	if (fp == NULL || fp->repy_python_file == NULL) {
		return;
	}

	PyObject *rc = NULL;

	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_FLUSH, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}

	REF_WIPE(rc);

	return;
}



void repy_next(repy_file * fp)  {
	CHECK_LIB_STATUS();

}

#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))


char * repy_readat( int size_to_read, int offset, repy_file * fp)  {
	CHECK_LIB_STATUS();
	if (fp == NULL || fp->repy_python_file == NULL) {
		return NULL;
	}

	PyObject *rc = NULL;
	rc = PyObject_CallMethod(fp->repy_python_file,REPYC_API_READ,"ii", size_to_read, offset);
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	char * python_string = PyString_AsString(rc);
	python_string = strdup(python_string);
	REF_WIPE(rc);
	return python_string;
}


//int repy_readline(char * location, int size_to_read, repy_file * fp)  {
//	CHECK_LIB_STATUS();
//
//	if (fp == NULL || fp->repy_python_file == NULL) {
//		return -1;
//	}
//
//	PyObject *rc = NULL;
//
//	rc = PyObject_CallMethod(fp->repy_python_file,REPYC_API_READLINE,"i",size_to_read);
//
//	if (rc == NULL) {
//		PyErr_Print();
//		return -1;
//	}
//	char * python_string = PyString_AsString(rc);
//	int py_s_size = PyString_Size(rc);
//	int min = MIN(size_to_read,py_s_size);
//	memcpy(location, python_string, min );
//
//	REF_WIPE(rc);
//
//	return min;
//
//}



//void repy_readlines(repy_file * fp, int size)  {
//	CHECK_LIB_STATUS();
//	assert(1);
//}
//
//
//
//void repy_seek(repy_file * fp, int offset, int whence)  {
//	CHECK_LIB_STATUS();
//	if (fp == NULL || fp->repy_python_file == NULL || offset > -1 || whence > -1) {
//		return;
//	}
//
//	PyObject * rc = NULL;
//	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_SEEK, "(dd)", offset, whence);
//	if (rc == NULL) {
//		PyErr_Print();
//		return;
//	}
//
//	REF_WIPE(rc);
//
//	return;
//
//
//}



void repy_writeat(char * data, int offset, repy_file * fp)  {
	CHECK_LIB_STATUS();
	if (fp == NULL || fp->repy_python_file == NULL || data == NULL) {
		return;
	}

	PyObject * rc = NULL;
	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_WRITEAT, "(si)", data, offset);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}

	REF_WIPE(rc);

	return;


}



void repy_writelines(repy_file * fp, char ** lines)  {
	CHECK_LIB_STATUS();

	if (fp == NULL || fp->repy_python_file == NULL || lines == NULL) {
		return;
	}

	int num_elements = 0;
	char * curr = *lines;
	while (curr != NULL) {
		num_elements++;
		curr = lines[num_elements];
	}

	PyObject * string_list = PyList_New(0);
	Py_INCREF(string_list);
	int i;
	for (i = 0; i < num_elements; i++) {
		char * curr = lines[i];
		PyObject * s = PyString_FromString(curr);
		PyList_Append(string_list, s);
	}

	PyObject * rc = NULL;
	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_WRITELINES,
			"O", string_list);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}
	REF_WIPE(string_list);
	REF_WIPE(rc);

	return;


}


void repy_exitall() {

	PyObject * instnace, * rc;
	CHECK_LIB_STATUS();

	instnace = PyDict_GetItemString(client_dict, REPYC_API_EXITALL);
	rc = PyObject_CallObject(instnace, NULL);

	if (rc == NULL) {
		PyErr_Print();
		return;
	}


}


void repy_removefile(char * filename) {
	PyObject * instnace = NULL, * rc = NULL;
	CHECK_LIB_STATUS();
	if (filename == NULL)
		return;
	instnace = PyDict_GetItemString(client_dict, REPYC_API_REMOVEFILE);
	PyObject * params = Py_BuildValue("(s)", filename);
	rc = PyObject_CallObject(instnace, params);

	if (rc == NULL) {
		PyErr_Print();
		return;
	}
}


repy_socket * repy_openconnection(char * destip, int destport, char * localip, int localport, double timeout) {
	CHECK_LIB_STATUS();
	if (destip == NULL || localip == NULL || destport < 0 || localport < 0 || timeout < 0) {
		return NULL;
	}
	PyObject* instance, * params, *rc = NULL;
		instance = PyDict_GetItemString(client_dict, REPYC_API_OPENCON);

	params = Py_BuildValue("(sisid)", destip, destport, localip, localport, timeout);
	rc = PyObject_Call(instance, params, NULL );
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	repy_socket * sp = malloc(sizeof(struct repy_socket_s));
	sp->repy_python_socket = rc;
	return sp;



}


repy_tcpserversocket * repy_listenforconnection(char * localip, int localport) {
	CHECK_LIB_STATUS();
	if (localip == NULL || localport < 0) {
		return NULL;
	}
	PyObject* instance, * params, *rc = NULL;
		instance = PyDict_GetItemString(client_dict, REPYC_API_OPENTCP);

	params = Py_BuildValue("(si)", localip, localport);
	rc = PyObject_Call(instance, params, NULL );
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	repy_tcpserversocket * sp = malloc(sizeof(struct repy_tcpserversocket_s));
	sp->repy_python_socket = rc;
	return sp;



}


void repy_closesocket(repy_socket * tofree) {
	PyObject * rc = NULL;
	if (tofree == NULL || tofree->repy_python_socket == NULL)
		return;
	rc = PyObject_CallMethod(tofree->repy_python_socket, REPYC_API_CLOSE, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}
	REF_WIPE(rc);
	REF_WIPE(tofree->repy_python_socket);
	free(tofree);
}


void repy_closesocketserver(repy_tcpserversocket * tofree) {
	PyObject * rc = NULL;
	if (tofree == NULL || tofree->repy_python_socket == NULL)
		return;
	rc = PyObject_CallMethod(tofree->repy_python_socket, REPYC_API_CLOSE, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}
	REF_WIPE(rc);
	REF_WIPE(tofree->repy_python_socket);
	free(tofree);
}


long int repy_socket_send(char* message, repy_socket* sp) {

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


repy_socket * repy_tcpserver_getconnection(repy_tcpserversocket * server) {
	CHECK_LIB_STATUS();
	if (server == NULL) {
		return NULL;
	}
	PyObject * rc = NULL;

	rc = PyObject_CallMethod(server->repy_python_socket, "getconnection", NULL );
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	repy_socket * sp = malloc(sizeof(struct repy_socket_s));
	sp->repy_python_socket = PyTuple_GetItem(rc, 2);
	return sp;
}


char * repy_socket_recv(int size, repy_socket* sp) {
	CHECK_LIB_STATUS();
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


repy_udpserver * repy_listenformessage(char * localip, int localport) {
	CHECK_LIB_STATUS();
	if (localip == NULL || localport < 0) {
		return NULL;
	}
	PyObject* instance, * params, *rc = NULL;
		instance = PyDict_GetItemString(client_dict, REPYC_API_OPENUDP);

	params = Py_BuildValue("(si)", localip, localport);
	rc = PyObject_Call(instance, params, NULL );
	if (rc == NULL) {
		PyErr_Print();
		return NULL;
	}
	repy_udpserver * sp = malloc(sizeof(struct repy_udpserver_s));
	sp->repy_python_udpserver = rc;
	return sp;
}

void repy_close_udpserver(repy_udpserver * server) {
	PyObject * rc = NULL;
	if (server == NULL || server->repy_python_udpserver == NULL)
		return;
	rc = PyObject_CallMethod(server->repy_python_udpserver, REPYC_API_CLOSE, NULL);
	if (rc == NULL) {
		PyErr_Print();
		return;
	}
	REF_WIPE(rc);
	REF_WIPE(server->repy_python_udpserver);
	free(server);
}

repy_message * repy_udpserver_getmessage(repy_udpserver * server) {
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

static void setup_python_path() {

	PyRun_SimpleString("import sys");
	const char * format = "sys.path.append('%s')";
	int len = strlen(format);

	char * syspath = calloc(len + strlen(path_to_repyc_python_binding), sizeof(char));
	snprintf(syspath, len + strlen(path_to_repyc_python_binding), format, path_to_repyc_python_binding );
	PyRun_SimpleString(syspath);

}


int repy_init() {
	printf("Loading RePy...\n");
	path_to_repyc_python_binding = getenv("REPY_PATH");
	if (path_to_repyc_python_binding == NULL) {
		path_to_repyc_python_binding = "/home/cmatthew/naclrepy/testing";
	}
	if (chdir(path_to_repyc_python_binding)) {
		printf("chdir failed.");
	}

	Py_Initialize();
	setup_python_path();
	//Derived from: http://www.linuxjournal.com/article/8497
	FILE*        exp_file;
	PyObject*    main_module_b, * expression;
	PyObject* rc, * repy_init_b;

	// Open and execute the Python file
	exp_file = fopen(repy_fn, "r");
	PyRun_SimpleFile(exp_file, repy_fn);
	fclose(exp_file);

	// Get a reference to the main module
	// and global dictionary
	main_module_b = PyImport_AddModule("__main__");
	global_dict_b = PyModule_GetDict(main_module_b);
	repy_init_b = PyDict_GetItemString(global_dict_b, "repyc_init_helper");
	pid_t mypid = getpid();
	rc = PyObject_CallObject(repy_init_b, NULL);

	//when repy exits the monitor process returns here too, we have to
	//terminate the extra control flow.
	pid_t new_pid = getpid();
	if (mypid == new_pid) {
		exit(0);
	}

	if (rc == NULL) {
		printf("C: Problem calling RePy Init.\n");
	} else {
		printf(" RePy has loaded.\n");
		REF_WIPE(rc);
	}

	// Extract a reference to the function "get_repyAPI"
	// from the global dictionary
	expression =
		PyDict_GetItemString(global_dict_b, "get_repyAPI");

	client_dict = NULL;
	client_dict = PyObject_CallObject(expression, NULL);

	//PyObject_Print(client_dict, stdout, 0);
	//	printf("\n\n\n");
	if (client_dict == NULL) {
		printf("Failed to get Client Dict.");
		return 1;
	}


	is_init = 1;
	return 0;
}


int repy_shutdown() {

	is_init = 0;
	PyObject * repy_shutdown_fp = NULL, * rc = NULL;

	repy_shutdown_fp = PyDict_GetItemString(global_dict_b, "repyc_shutdown");

	rc = PyObject_CallObject(repy_shutdown_fp, NULL);
	REF_WIPE(client_dict);
	//Py_Finalize();
	return (rc == NULL)? 1:0;
}


