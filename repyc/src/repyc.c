#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <repy.h>
#include <linux/limits.h>
#include <assert.h>
#include <errno.h>
#include "util.h"
#include "handle_storage.h"
#include "repy_private.h"

/** We only need to init python once, use this as a gaurd.  */
int is_init = 0;

/** The location of the RePyC API file.  */
char * path_to_repyc_python_binding = NULL;
/** The name of the repyc API file. */
const char * repy_fn = "repyc.py";

/** Contains the bound objects which constitiue the RePy API. */
PyObject *client_dict = NULL;
PyObject * global_dict_b = NULL;
int repy_errno = 0;


void CHECK_LIB_STATUS() {
  if (client_dict == NULL || is_init == 0) {
    fprintf(stderr,"RepyC is not Currently initialized... Exiting.\n");
    exit(ENODEV);
  }
  PyErr_Clear();
  repy_errno = 0;
}
#define name_as_string(x) PyString_AsString(PyObject_Str(PyObject_GetAttrString(x,"__name__"))) 

#define repy_check(type,str, rc)   if (!strcmp(type,str)) { return rc; }	     


int repy_get_errno() {
  PyObject* type, * value, *traceback;
  if(0 != repy_errno) {
    return repy_errno;
  }
  PyErr_Fetch(&type, &value, &traceback);
  char * et;
  if (type == NULL) {
    return 0;
  }
  
  et = name_as_string(type);
  repy_check(et,"FileNotFoundError",ENOENT);
  


  fprintf(stderr, "Could not find %s in the error table.\n", et);
  return -1;

}


void repy_perror(char * your_message) {
  char * our_message = "";
  char * error_type = "";
  PyObject* type, * value, *traceback;

  if(repy_errno != 0) {
    our_message = strerror(repy_errno);
    goto show_message;
  }

  PyErr_Fetch(&type, &value, &traceback);

  if (type == NULL) {
    return;
  }
  
  error_type = name_as_string(type);
  our_message = PyString_AsString(PyObject_Str(value));
  
 show_message:
  if (your_message) {
    fprintf(stderr, "%s: %s--%s\n", your_message, error_type ,our_message);
  } else {
    fprintf(stderr, "%s\n", our_message);
  }
}

char * repy_getmyip() {
	PyObject * instnace, * rc;
	CHECK_LIB_STATUS();
	instnace = PyDict_GetItemString(client_dict, REPYC_API_GETMYIP);
	rc = PyObject_CallObject(instnace, NULL);
	if (rc == NULL) {
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
	  repy_errno = EINVAL;
		return NULL;
	}
	param = Py_BuildValue("(s)", name);
	instnace = PyDict_GetItemString(client_dict, REPYC_API_GETHOSTBYNAME);
	rc = PyObject_CallObject(instnace, param);
	REF_WIPE(param);
	if (rc == NULL) {
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




char** repy_listfiles(int* num_entries) {

	PyObject * instnace, * rc;
	CHECK_LIB_STATUS();

	instnace = PyDict_GetItemString(client_dict, REPYC_API_LISTDIR);
	rc = PyObject_CallObject(instnace, NULL);

	if (rc == NULL) {
		return NULL;
	}

	int size = PyList_Size(rc);
	char ** list = (char**) calloc(size, sizeof(char*));
	int i;

	for (i = 0; i < size; i++) {
		PyArg_Parse(PyList_GetItem(rc,i),"s", &(list[i]) );
	}


	*num_entries = size;
	//REF_WIPE(rc);
	return list;

}


#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))



void repy_exitall() {

	PyObject * instnace, * rc;
	CHECK_LIB_STATUS();

	instnace = PyDict_GetItemString(client_dict, REPYC_API_EXITALL);
	rc = PyObject_CallObject(instnace, NULL);

	if (rc == NULL) {
		return;
	}


}


void repy_removefile(char * filename) {
	PyObject * instnace = NULL, * rc = NULL;
	CHECK_LIB_STATUS();
	if (filename == NULL)
	  repy_errno = EINVAL;
	  return;
	instnace = PyDict_GetItemString(client_dict, REPYC_API_REMOVEFILE);
	PyObject * params = Py_BuildValue("(s)", filename);
	rc = PyObject_CallObject(instnace, params);

	if (rc == NULL) {
		return;
	}
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
	printf("repyc: Loading RePy...\n");
	repy_ft_inithandles();
	path_to_repyc_python_binding = getenv("REPY_PATH");
	if (path_to_repyc_python_binding == NULL) {
		fprintf(stderr, "repyc: $REPY_PATH must be set before running recpyc.\n");
		return 1;
	}
	if (chdir(path_to_repyc_python_binding)) {
		fprintf(stderr, "repyc: chdir failed.\n");
		return 2;
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
		fprintf(stderr,"repyc: problem calling RePy init.\n");
		return 3;
	} else {
		printf("repyc: RePy has loaded.\n");
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
		fprintf(stderr,"Failed to get Client Dict.");
		return 4;
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


