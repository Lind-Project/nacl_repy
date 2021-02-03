#include <Python.h>
#include <pthread.h> 
#include <stdio.h> 
#include <unistd.h> 
#include <string.h>
#include <stdlib.h>
#include "structmember.h"
#include "lfq.h"
#include "cross-platform.h"
#include "gperftools/tcmalloc.h"

#define pipeEOF -1
 

typedef struct {
    char* data;
    int length;
    int index;
    int eof;
    
} LFQueueEntry;

typedef struct {
    PyObject_HEAD
    struct lfq_ctx ctx;
    LFQueueEntry* CurrEntry;
    
} LindPipe;

LFQueueEntry* LFQEntry_new(char* data, int length) { 
  LFQueueEntry* entry = tc_malloc(sizeof(LFQueueEntry));
  entry->data = tc_malloc(sizeof(char) * length);
  memcpy(entry->data, data, length);
  entry->length = length;
  entry->index = 0;

  return entry;
}

int getEntryRemainder(LFQueueEntry* entry) {
    return entry->length - entry->index;
}

static void
LindPipe_dealloc(LindPipe* self)
{
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
LindPipe_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    LindPipe *self;

    self = (LindPipe *)type->tp_alloc(type, 0);
    if (self != NULL) {
    
    }

    return (PyObject *)self;
}


static int
LindPipe_init(LindPipe *self, PyObject *args, PyObject *kwds)
{
    lfq_init(&(self->ctx), 1);
    self->CurrEntry = NULL;

    return 0;
}


static PyObject *LindPipe_seteof(LindPipe *self) {

    /** Create EOF entry **/

    int ret = 0;
   
    Py_BEGIN_ALLOW_THREADS
    if (( ret = lfq_enqueue(&(self->ctx), LFQEntry_new(NULL, pipeEOF))) != 0) {
        printf("lfq_enqueue failed, reason:%s\n", strerror(-ret));
        return NULL;
    }
    Py_END_ALLOW_THREADS

    Py_RETURN_NONE;
}

// void updateCurrentEntry(LindPipe *self) {

//     while ((self->CurrEntry = (LFQueueEntry*)lfq_dequeue(&(self->ctx))) == 0);

// }



static PyObject *LindPipe_pipewrite(LindPipe *self, PyObject *args) {

    char* data;
    long buf_addr;
    int datalen;
    int ret;

    Py_BEGIN_ALLOW_THREADS

    // printf("writing\n");


    if (!PyArg_ParseTuple(args, "li", &buf_addr, &datalen)) {
        return NULL;
    }

    data = (char*)buf_addr;

    

    if (( ret = lfq_enqueue(&(self->ctx), LFQEntry_new(data, datalen))) != 0) {
        printf("lfq_enqueue failed, reason:%s\n", strerror(-ret));
        return NULL;
    }

   
    Py_END_ALLOW_THREADS

    return Py_BuildValue("i", datalen);

}

static PyObject *LindPipe_piperead(LindPipe *self, PyObject *args) {
   
    int count;
    long buf_addr;
    char* buf;
    int bytes_read = 0;
    int bytes_remaining = 0;

    Py_BEGIN_ALLOW_THREADS
    
    // printf("reading\n");

    if (!PyArg_ParseTuple(args, "li", &buf_addr, &count)) {
        return NULL;
    }

    buf = (char*)buf_addr;

    while (bytes_read < count) {
        
        /*update entry and check for EOF */
        if (self->CurrEntry == NULL) {

            while ((self->CurrEntry = (LFQueueEntry*)lfq_dequeue(&(self->ctx))) == 0) {
                Py_END_ALLOW_THREADS
                Py_BEGIN_ALLOW_THREADS
            }

        }
        
        // updateCurrentEntry(self);
        if (self->CurrEntry->length == pipeEOF) break;

        int entry_remainder = getEntryRemainder(self->CurrEntry);
        bytes_remaining = count - bytes_read;

        if (bytes_remaining <= entry_remainder) {
            memcpy(buf + bytes_read, self->CurrEntry->data + self->CurrEntry->index, bytes_remaining);
            self->CurrEntry->index = self->CurrEntry->index + bytes_remaining;
            bytes_read = bytes_read + bytes_remaining;
        }
        else {
            memcpy(buf + bytes_read, self->CurrEntry->data + self->CurrEntry->index, entry_remainder);
            self->CurrEntry->index = self->CurrEntry->length;
            bytes_read = bytes_read + entry_remainder;
        }


        if (self->CurrEntry->index == self->CurrEntry->length){
            tc_free(self->CurrEntry->data);
            tc_free(self->CurrEntry);
            self->CurrEntry = NULL;
        }

    }

    Py_END_ALLOW_THREADS
    return Py_BuildValue("i", bytes_read);
}

static PyMemberDef LindPipe_members[] = {
    {NULL}  /* Sentinel */
};

static PyMethodDef LindPipe_methods[] = {
    {"pipewrite", (PyCFunction)LindPipe_pipewrite, METH_VARARGS,
     "Take a python string and write it to the pipe."
    },
    {"piperead", (PyCFunction)LindPipe_piperead, METH_VARARGS,
     "Read count chars from the pipe and return them as a python string."
    },
    {"seteof", (PyCFunction)LindPipe_seteof, METH_NOARGS,
     "Set the pipes eof flag."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject LindPipeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "lindpipe.LindPipe",       /* tp_name */
    sizeof(LindPipe),          /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)LindPipe_dealloc,                         /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_compare */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /* tp_flags */
    "LindPipe objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    LindPipe_methods,             /* tp_methods */
    LindPipe_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)LindPipe_init,      /* tp_init */
    0,                         /* tp_alloc */
    LindPipe_new,                 /* tp_new */
};


#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initlindpipe(void) 
{
    PyObject* m;

    if (PyType_Ready(&LindPipeType) < 0)
        return;

    m = Py_InitModule3("lindpipe", LindPipe_methods,
                       "Pipe module that creates a pipe extension type for Lind.");

    Py_INCREF(&LindPipeType);
    PyModule_AddObject(m, "LindPipe", (PyObject *)&LindPipeType);
}
