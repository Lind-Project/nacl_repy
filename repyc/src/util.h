/*
 * util.h
 *
 *  Created on: 2010-12-07
 *      Author: cmatthew
 */

#ifndef UTIL_H_
#define UTIL_H_

/** Destry a reference to a python object which we OWN. */
#define REF_WIPE(name) Py_XDECREF(name); name = NULL

/** Since debugging does not work, a flushed debug printer.  */
#define MARK(X) 	printf(X);fflush(stdout);

/** Print the type of a python object. */
#define PRINT_TYPE(X) PyObject_Print(PyObject_Type(X),stdout,0)

#endif /* UTIL_H_ */
