#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <repy.h>
#include <linux/limits.h>
#include <assert.h>

#include "util.h"
#include "repy_private.h"


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
	PyObject * lock = (PyObject*)l->python_lock;
	REF_WIPE(lock);
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

