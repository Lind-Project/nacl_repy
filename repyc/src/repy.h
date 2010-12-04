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


/* Start the library and python bindings */
int repy_init();


/* Have RePy Shutdown tidy. */
int repy_shutdown();


///////////////////////////////////////////////////////////////////////////////


/** Returns the localhost's "Internet facing" IP address. It may raise an
 * exception on hosts that are not connected to the Internet. */
char * getmyip();


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


/** Returns a float containing the number of seconds the program has
 * been running. Note that in very rare circumstances (like the user
 * resetting their clock), this will not produce increasing values. */
double * getruntime();


/** Returns a random floating point number between 0.0 (inclusive)
 * and 1.0 (exclusive).
 */
double * randomfloat();


/** Sleeps the current thread for some time (waits for a specific time before
 * executing any further instructions). This thread will not consume CPU cycles
 * during this time. Timing issues that confuse getruntime() may also cause
 * sleep to behave in undefined ways. */
void repy_sleep(double);


///////////////////////////////////////////////////////////////////////////////


typedef struct repy_lock_s {
	void * python_lock;
} repy_lock;


/** Returns a lock object that can be used for mutual exclusion and critical
 * section protection.
 */
repy_lock* repy_getlock();


/** Blocks until the lock is available, then takes it (lock is an object
 * obtained by calling getlock()).
 */
int repy_lock_blocking_acquire(repy_lock*);


/** Blocks until the lock is available, then takes it (lock is an object
 * obtained by calling getlock()).
 *
 * If the lock is already taken, method returns False immediately instead of
 * waiting to acquire the lock; if the lock is available it takes it and
 * returns True.
 */
int repy_lock_nonblocking_acquire(repy_lock*);


/** Releases the lock. Do not call it if the lock is unlocked. */
void repy_lock_release(repy_lock*);

void free_repy_lock(repy_lock *);

char ** listdir(int* num_entries);



typedef struct repy_file_s {
	void * repy_python_file;
} repy_file;


repy_file * repy_open(char * filename, char * mode);

void repy_close(repy_file *);

void repy_flush(repy_file *);

void repy_next(repy_file *);

int repy_read(char * loc, int size, repy_file *);

int repy_readline(char * location, int size, repy_file *);

void repy_readlines(repy_file *, int size);

void repy_seek(repy_file *, int offset, int whence);

void repy_write(repy_file *, char * data);

void repy_writelines(repy_file *, char ** lines);

void repy_exitall();

void repy_removefile(char * filename);
