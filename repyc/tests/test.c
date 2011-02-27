
#include "../src/repy.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

/* #define DEBUG */

typedef enum t_result {
	PASS, FAIL, BROKEN
} tresult;

static tresult fail(char * message) {
	printf("\nFAILURE: %s\n", message);
	return FAIL;
}


tresult test_getmyup() {
	char * myip = NULL;
	myip = repy_getmyip();
	//shortest ip string might be 1.1.1.1 -> len = 6
	if (myip == NULL || strlen(myip) < 6) {
		return fail("address null or too short.");
	} else {
#ifdef DEBUG
		printf("my ip is: %s\n", myip);
#endif
		return PASS;
	}
}


tresult test_gethostbyname() {
	char * myhost = NULL;
	myhost = repy_gethostbyname("sebulba.cs.uvic.ca");
	if (myhost == NULL || strstr(myhost,"142.104") == NULL) {
	  printf("%s",myhost);
	  return fail("returned wrong address.");
	} else {
#ifdef DEBUG
		printf("%s, ", myhost->hostname);
		printf("%s\n", myhost->ipaddrlist[0]);
#endif
		return PASS;
	}
}

tresult test_getruntime() {
	double* time = 0;
	time = repy_getruntime();
	if (time == 0) {
		return fail("did not return time.");
	} else {
#ifdef DEBUG
		printf("Time is: %f\n", time);
#endif
		return PASS;
	}
}

tresult test_getrandombytes() {
	char* rfloat = NULL;
	rfloat = repy_randombytes();
	if (rfloat == NULL) {
		return fail("did not return value.");
	}
	if (rfloat[0]!='\0') {
	  return PASS;
	} else {
	  return fail("I'm not sure if the values are random.");
	}

}


tresult test_sleep() {
	repy_sleep(1.0);
	return PASS;
}


/* tresult test_locking() { */
/* 	repy_lock * l = repy_createlock(); */
/* 	if (l == NULL || l->python_lock == NULL) { */
/* 		return fail("was not able to create lock."); */
/* 	} */
/* 	repy_lock_blocking_acquire(l); */
/* 	int rc = repy_lock_nonblocking_acquire(l); */
/* 	if (rc != 0) { */
/* 		return fail("non-blocking acquire failed."); */
/* 	} */
/* 	repy_lock_release(l); */

/* 	repy_lock * l2 = repy_createlock(); */

/* 	rc = repy_lock_nonblocking_acquire(l2); */
/* 	if (rc != 1) { */
/* 		return fail("non-blocking acquire 2 failed."); */
/* 	} */
/* 	repy_lock_release(l2); */

/* 	return PASS; */
/* } */

#define DEBUG
tresult test_listdir() {
		int size = -1;
		char ** dirents;

		dirents = repy_listfiles(&size);

		if (dirents == NULL || size == -1) {
			return fail("no dir, or no entire returned.");
		}

#ifdef DEBUG
		int i;
		puts("\n");
		for (i = 0; i < size; i++) {
			printf("[%d] %s\n", i, dirents[i]);
		}
#endif
		return PASS;
}


tresult test_open_close() {
	char * test_file_name = "test_file.junk";
	repy_handle fp = repy_openfile(test_file_name, 1);
	if (fp == -1) {
		return fail("no file pointer after open.");
	}
	repy_close(fp);
	return PASS;
}



tresult test_writeat() {
	char * test_file_name = "test_file2.junk";
	repy_handle fp = repy_openfile(test_file_name, 1);
	if (fp == -1) {
		return fail("no file pointer after open.");
	}
	char * a = "Hello\nWorld\n";
	repy_writeat(a, 0, fp) ;
	
	repy_close(fp);

	fp = repy_openfile(test_file_name, 0);

	char * read = repy_readat(50, 0, fp);
	repy_close(fp);
	if (read == NULL) {
		return fail("no data read from file.");
	}
	if(strstr(read, "World")) {
		return PASS;
	} else {
		return fail("could not match written data.");
	}
}


tresult test_readat() {
	char * test_file_name = "readtest.junk";
	repy_handle fp = repy_openfile(test_file_name, 0);
	if (fp == -1) {
		return fail("no file pointer after open.");
	}

	char * space = repy_readat(499, 0 ,fp);
	repy_close(fp);

	if(	strstr(space, "any emotion akin to love for Irene Adler") != NULL &&
			strstr(space, "He ") != NULL) {
		free(space);
		return PASS;
	} else {
		free(space);
		return fail("could not match file data.");
	}

}


tresult test_exitall() {
  printf("repy_api_test: skipping exitall test as it could work too well!  ");
  //repy_exitall(); works!  but stops the testing!
  return PASS;
}


tresult test_removefile() {
	//the side effect of this is that it creates FILENAME
	char * filename = "test_file2.junk";
	repy_handle file;
	test_writeat();
	if ( (file = repy_openfile(filename, 1)) ) {
	  repy_close(file);
	} else {
	  return fail("could not create test file.");
	}
	repy_removefile(filename);
	/* TODO: right now we cant test this worked */
	/* if ( (file = fopen(filename, "r")) ) { */
        /* fclose(file); */
        /* return fail("file still existed after remove."); */
	/* } */

	return PASS;
}


tresult test_open_socket() {
	char * loopback = "127.0.0.1";

	repy_tcpserver_handle server = repy_listenforconnection(loopback,12345);
	if (server == -1) {
		return fail("no socket pointer after server open.");
	}

	repy_socket_handle sp = repy_openconnection(loopback, 12345, loopback, 12346, 1.0);
	if (sp == -1) {
		return fail("no socket pointer after open.");
	}

	int sent = repy_socket_send("a message thorough the socket.", sp);

	if (sent < 1) {
		return fail("sending message through the socket returned no length.");
	}

	repy_socket_handle reciever = repy_tcpserver_getconnection(server);
       
	char * new_message = repy_socket_recv(50, reciever);

	repy_closesocket(sp);
        repy_closesocketserver(server);

	if(strstr(new_message,"a message thorough the socket")) {
		return PASS;
	} else {
		return fail("String was not found in other end of socket");
	}
	return PASS;
}

tresult test_udp_messages() {
	char * loopback = "127.0.0.1";
	int dest = 12345;
	repy_udpserver_handle server = repy_listenformessage(loopback, dest);
	if (server == -1) {
		return fail("no message server pointer after server open.");
	}
	
	long int rc = repy_sendmessage(loopback, dest, "A test UDP message", loopback, 12346);
	if (rc < 1) {
		return fail("failed to send UDP message");
	}
	
	repy_message * new_message = NULL;
	new_message = repy_udpserver_getmessage(server);
	//repy_close_udpserver(server);
	
	if(new_message != NULL &&
	   new_message->message != NULL &&
	   strstr(new_message->message,"A test UDP message")) {
		return PASS;
	} else {
		return fail("String was not found in other end of message.");
	}
	return PASS;

}

void run_test(tresult(*func)(void), char * name) {
	printf("Running Test: %s... ", name);
	fflush(stdout);
	int rc = func();
	if (rc == PASS) {
		printf("Test %s passed.\n", name);
		fflush(stdout);
	} else if (rc == BROKEN) {
		printf("Test %s not done yet.\n", name);
		fflush(stdout);
	} else {
		printf("Test %s failed.\n", name);
		fflush(stdout);
		
	}

}


int main() {
	int rc = 0;
	/* int i = 0; */
	rc = repy_init();
	if (rc) {
		printf("Problem loading repy: %d", rc);
		return rc;
	} else {
	  /* for (i; i<3; i++) { */
		run_test((&test_getmyup), "getmyip");
		run_test((&test_gethostbyname), "test_gethostbyname");
		run_test((&test_getruntime), "getruntime");
		run_test((&test_getrandombytes), "getrandombytes");
		run_test((&test_sleep), "sleep");
		//run_test((&test_locking), "locking");
		run_test((&test_listdir), "listdir");
		run_test((&test_open_close), "Open and Close");
		run_test((&test_open_close), "Open and Close");
	       	run_test((&test_readat), "ReadAt");
		run_test((&test_writeat), "WriteAt");
		run_test((&test_exitall), "Exitall");
		run_test((&test_removefile), "Removefile");
		run_test((&test_open_socket), "OpenSocket");
		run_test((&test_udp_messages), "UDP Message");
		run_test((&test_getmyup), "getmyip");
	  /* } */
		repy_exitall();
		
	}
	return 0;
}

