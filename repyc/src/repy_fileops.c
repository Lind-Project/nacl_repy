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



repy_handle repy_openfile(char * filename, int create)  {
	CHECK_LIB_STATUS();
	if (filename == NULL) {
	  repy_errno = EINVAL;
	  return -1;
	}
	repy_file * fp = NULL;
	PyObject* instance, * params, *rc = NULL;
	instance = PyDict_GetItemString(client_dict, REPYC_API_OPEN);
	PyObject * bool = (create)?Py_True:Py_False;
	params = Py_BuildValue("(sO)", filename, bool);
	rc = PyObject_Call(instance, params, NULL);
	REF_WIPE(params);

	if (rc == NULL) {
	  return -1;
	}

	fp = (repy_file *) malloc(sizeof(struct repy_file_s));

	fp->repy_python_file = rc;

	return repy_ft_set_handle(fp);
}



void repy_close(repy_handle hp)  {
	CHECK_LIB_STATUS();
	repy_file* fp = repy_ft_get_handle(hp);
	repy_ft_clear(hp);
	if (fp == NULL || fp->repy_python_file == NULL) {
	  repy_errno = EINVAL;
	  return;
	}

	PyObject * params = NULL, *rc = NULL;

	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_CLOSE, NULL);
	if (rc == NULL) {
	   return;
	}

	REF_WIPE(params);
	REF_WIPE(rc);
	PyObject * lock = (PyObject *) fp->repy_python_file;
	REF_WIPE(lock);
       
	return;

}


char * repy_readat( int size_to_read, int offset, repy_handle hp)  {
	CHECK_LIB_STATUS();
	repy_file* fp = repy_ft_get_handle(hp);
	if (fp == NULL || fp->repy_python_file == NULL) {
	  repy_errno = EINVAL;
	  return NULL;
	}

	PyObject *rc = NULL;
	rc = PyObject_CallMethod(fp->repy_python_file,REPYC_API_READ,"ii", size_to_read, offset);
	if (rc == NULL) {
	  return NULL;
	}
	char * python_string = PyString_AsString(rc);
	python_string = strdup(python_string);
	REF_WIPE(rc);
	return python_string;
}



void repy_writeat(char * data, int offset, repy_handle hp)  {
	CHECK_LIB_STATUS();
	repy_file* fp = repy_ft_get_handle(hp);
	if (fp == NULL || fp->repy_python_file == NULL || data == NULL) {
	  repy_errno = EINVAL;
	  return;
	}

	PyObject * rc = NULL;
	rc = PyObject_CallMethod(fp->repy_python_file, REPYC_API_WRITEAT, "(si)", data, offset);
	if (rc == NULL) {
	  return;
	}

	REF_WIPE(rc);

	return;
}
