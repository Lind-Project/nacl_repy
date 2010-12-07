#include <repy.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include "../src/util.h"
//#define DEBUG

typedef enum t_result {
	PASS, FAIL, BROKEN
} tresult;

static tresult fail(char * message) {
	printf("\nFAILURE: %s\n", message);
	return FAIL;
}


tresult test_getmyup() {
	char * myip = NULL;
	myip = getmyip();
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
	double* time = NULL;
	time = getruntime();
	if (time == NULL) {
		return fail("did not return time.");
	} else {
#ifdef DEBUG
		printf("Time is: %f\n", *time);
#endif
		return PASS;
	}
}

tresult test_getrandombytes() {
	void* rfloat = NULL;
	rfloat = repy_randombytes();
	if (rfloat == NULL) {
		return fail("did not return value.");
	} else {
		return PASS;
	}
}


tresult test_sleep() {
	repy_sleep(1.0);
	return PASS;
}


tresult test_locking() {
	repy_lock * l = repy_createlock();
	if (l == NULL || l->python_lock == NULL) {
		return fail("was not able to create lock.");
	}
	repy_lock_blocking_acquire(l);
	int rc = repy_lock_nonblocking_acquire(l);
	if (rc != 0) {
		return fail("non-blocking acquire failed.");
	}
	repy_lock_release(l);

	repy_lock * l2 = repy_createlock();

	rc = repy_lock_nonblocking_acquire(l2);
	if (rc != 1) {
		return fail("non-blocking acquire 2 failed.");
	}
	repy_lock_release(l2);

	return PASS;
}


tresult test_listdir() {
		int size = -1;
		char ** dirents;

		dirents = repy_listfiles(&size);

		if (dirents == NULL || size == -1) {
			return fail("no dir, or no entires returned.");
		}

#ifdef DEBUG
		int i;
		puts("\n");
		for (i = 0; i < size; i++) {
			printf("%d: %s\n", i, dirents[i]);
		}
#endif
		return PASS;
}


tresult test_open_close() {
	char * test_file_name = "test_file.junk";
	repy_file* fp = repy_openfile(test_file_name, 1);
	if (fp == NULL) {
		return fail("no file pointer after open.");
	}
	repy_close(fp);
	return PASS;
}



tresult test_writeat() {
	char * test_file_name = "test_file2.junk";
	repy_file* fp = repy_openfile(test_file_name, 1);
	if (fp == NULL) {
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
	repy_file* fp = repy_openfile(test_file_name, 0);
	if (fp == NULL) {
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
	//repy_exitall(); works!  but stops the testing!
	return PASS;
}


tresult test_removefile() {
	//the sideeffect of this is that it creates FILENAME
	char * filename = "test_file2.junk";
	FILE * file;
	test_writeat();
	if ( (file = fopen(filename, "r")) ) {
        fclose(file);
	} else {
		fclose(file);
		return fail("could not create test file.");
	}
	repy_removefile(filename);

	if ( (file = fopen(filename, "r")) ) {
        fclose(file);
        return fail("file still existed after remove.");
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
		exit(1);
	}

}


int main(int argc, char** argv) {
	int rc = 0;

	rc = repy_init();
	if (rc) {
		printf("Problem loading repy: %d", rc);
		return rc;
	} else {
		run_test((&test_getmyup), "getmyip");
		run_test((&test_gethostbyname), "test_gethostbyname");
		run_test((&test_getruntime), "getruntime");
		run_test((&test_getrandombytes), "getrandombytes");
		run_test((&test_sleep), "sleep");
		run_test((&test_locking), "locking");
		run_test((&test_listdir), "listdir");
		run_test((&test_open_close), "Open and Close");
		run_test((&test_writeat), "WriteAt");
		run_test((&test_readat), "ReadAt");
		run_test((&test_exitall), "Exitall");
		run_test((&test_removefile), "Removefile");
		repy_shutdown();
	}
	return 0;
}

