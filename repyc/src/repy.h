/*
 * repy.h
 *
 *  Created on: 2010-12-27
 *      Author: cmatthew
 */

#ifndef REPY_H_
#define REPY_H_


#ifdef __cplusplus
	extern "C" {
#endif


/*
* This file is part of RePyC.
*
*    RePyC is free software: you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    RePyC is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
*/


/* Start the library and python bindings.
 * returns 0 on sucessful start, otherwise a positive error code.
*/
int repy_init();


/* Have RePy Shutdown tidy. */
int repy_shutdown();


/*----------------System Services----------------*/


/** Returns a float containing the number of seconds the program has
 * been running. Note that in very rare circumstances (like the user
 * resetting their clock), this will not produce increasing values. */
double repy_getruntime();


/** Returns a random floating point number between 0.0 (inclusive)
 * and 1.0 (exclusive).
 */
void * repy_randombytes();


/*----------------Control Flow----------------*/


/** Sleeps the current thread for some time (waits for a specific time before
 * executing any further instructions). This thread will not consume CPU cycles
 * during this time. Timing issues that confuse getruntime() may also cause
 * sleep to behave in undefined ways. */
void repy_sleep(double);

typedef struct repy_lock_s {
	void * python_lock;
} repy_lock;


/** Returns a lock object that can be used for mutual exclusion and critical
 * section protection.
 */
repy_lock* repy_createlock();


/**  Blocks until the lock is available, then takes it (lock is an object
 * obtained by calling getlock()).
 */
int repy_lock_blocking_acquire(repy_lock*);


/**  Blocks until the lock is available, then takes it (lock is an object
 * obtained by calling getlock()).
 *
 * If the lock is already taken, method returns False immediately instead of
 * waiting to acquire the lock; if the lock is available it takes it and
 * returns True.
 */
int repy_lock_nonblocking_acquire(repy_lock*);


/**  Releases the lock. Do not call it if the lock is unlocked. */
void repy_lock_release(repy_lock*);

/**  Used to release and free a lock. */
void free_repy_lock(repy_lock *);

/**  Terminates the program immediately. The program will not execute the "exit" callfunc or finally blocks. */
void repy_exitall();

/*----------------FileSytem----------------*/

/*  Returns a list of file names for the files in the vessel. */
char ** repy_listfiles(int* num_entries);

typedef struct repy_file_s {
	void * repy_python_file;
} repy_file;

typedef int repy_handle;


/**  Open a file, returning an object of the file type.
 *
 * FILENAMEs may only be in the current directory and may only contain lowercase letters,
 * numbers, the hyphen, underscore, and period characters. Also, filenames cannot be '.',
 * '..', the blank string or start with a period. There is no concept of a directory or a
 * folder in repy. Filenames must be no more than 120 characters long.
 *
 * Every file object is capable of both reading and writing.
 *
 * If CREATE is 1, the file is created if it does not exist. Neither mode truncates the file on open. */
repy_handle  repy_openfile(char * filename, int create);

/** Close the file. A closed file cannot be read or written any more. Any operation which requires
 * that the file be open will raise a FileClosedError? after the file has been closed. */
void repy_close(repy_handle);

/**  Seek to a location in a file and reads up to SIZELIMIT bytes from the file, returning what is read.
 * If SIZELIMIT is None, the file is read to EOF. */
int repy_readat(char* buffer, int sizelimit, int offset, repy_handle);

/**  Seek to the OFFET in the FILE and then write some DATA to a file. */
void repy_writeat(char * data, int size, repy_handle);

/**  Deletes a file named FILENAME in the vessel. If FILENAME does not exist, an exception is raised. */
void repy_removefile(char * filename);


/*----------------Network----------------*/


/** Returns the localhost's "Internet facing" IP address. It may raise an
 * exception on hosts that are not connected to the Internet. */
char * repy_getmyip();


typedef struct host_s {
	char * hostname;
	char ** aliaslist;
	int aliaslistsize;
	int ipaddrlistsize;
	char ** ipaddrlist;
} host;


/**  Translate a host name to IPv4 address format, extended interface. Return a
 * triple (hostname, aliaslist, ipaddrlist) where hostname is the primary host
 * name responding to the given ip_address, aliaslist is a (possibly empty)
 * list of alternative host names for the same address, and ipaddrlist is a list
 *  of IPv4 addresses for the same interface on the same host (often but not
 *  always a single address). gethostbyname_ex() does not support IPv6 name
 *  resolution, and getaddrinfo() should be used instead for IPv4/v6 dual stack
 *  support. */
char * repy_gethostbyname(char * name);


/*----------------TCP----------------*/


typedef struct repy_socket_s {
	void * repy_python_socket;
} repy_socket;

typedef int repy_socket_handle;

repy_socket_handle repy_openconnection(char * destip, int destport, char * localip, int localport, double timeout);
long int repy_socket_send(char* message, repy_socket_handle sp);

void repy_closesocket(repy_socket_handle tofree);

typedef struct repy_tcpserversocket_s {
	void * repy_python_socket;
} repy_tcpserversocket;
typedef int repy_tcpserver_handle;

repy_tcpserver_handle repy_listenforconnection(char * localip, int localport);

void repy_closesocketserver(repy_tcpserver_handle  tofree);

repy_socket_handle repy_tcpserver_getconnection(repy_tcpserver_handle  server);

char * repy_socket_recv(int size, repy_socket_handle sp);

/*----------------UDP----------------*/

typedef struct repy_udpserver_s {
	void * repy_python_udpserver;
} repy_udpserver;

typedef int repy_udpserver_handle;

repy_udpserver_handle repy_listenformessage(char * localip, int localport);

void repy_close_udpserver(repy_udpserver_handle );

typedef struct repy_message_s {
  char * ip;
  int port;
  char * message;
  int message_size;
} repy_message;

  repy_message * repy_udpserver_getmessage(char * message_buffer, int size,  repy_udpserver_handle h);

/**  Sends a UDP message to a destination host / port using a specified localip and localport.
 * Returns the number of bytes sent. This may not be the entire message.
 **/
long int repy_sendmessage(char * destip, int destport, char * message, char * localip, int localport );

/* If an error occured in the last call, tell us what it was. */  
void repy_perror(char* message);

int repy_get_errno();


#define MIN(x,y) (x<y)?x:y


#ifdef __cplusplus
} /* closing brace for extern "C" */
#endif

#endif /* repy_h */
