#include <repy.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

//#define DEBUG

typedef enum t_result {
	PASS, FAIL, BROKEN
} tresult;


tresult test_getmyup() {
	char * myip = NULL;
	myip = getmyip();
	//shortest ip string might be 1.1.1.1 -> len = 6
	if (myip == NULL || strlen(myip) < 6) {
		return FAIL;
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
		return FAIL;
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
		return FAIL;
	} else {
#ifdef DEBUG
		printf("Time is: %f\n", *time);
#endif
		return PASS;
	}
}

tresult test_getrandomfloat() {
	double* rfloat = NULL;
	rfloat = randomfloat();
	if (rfloat == NULL) {
		return FAIL;
	} else {
#ifdef DEBUG
		printf("Random is: %f\n", *rfloat);
#endif
		return PASS;
	}
}


tresult test_sleep() {
	repy_sleep(1.0);
	return PASS;
}


tresult test_locking() {
	repy_lock * l = repy_getlock();
	if (l == NULL || l->python_lock == NULL) {
		return FAIL;
	}
	repy_lock_blocking_acquire(l);
	int rc = repy_lock_nonblocking_acquire(l);
	if (rc != 0) {
		return FAIL;
	}
	repy_lock_release(l);

	repy_lock * l2 = repy_getlock();

	rc = repy_lock_nonblocking_acquire(l2);
	if (rc != 1) {
		return FAIL;
	}
	repy_lock_release(l2);

	return PASS;
}


tresult test_listdir() {
		int size = -1;
		char ** dirents;

		dirents = listdir(&size);

		if (dirents == NULL || size == -1) {
			return FAIL;
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
	repy_file* fp = repy_open(test_file_name, "w");
	if (fp == NULL) {
		return FAIL;
	}
	repy_close(fp);
	return PASS;
}



tresult test_write_flush() {
	char * test_file_name = "test_file2.junk";
	repy_file* fp = repy_open(test_file_name, "w");
	if (fp == NULL) {
		return FAIL;
	}

	repy_write(fp, "This is something to write into a file...\n");
	repy_flush(fp);

	repy_close(fp);
	return PASS;
}

tresult test_writelines() {
	char * test_file_name = "test_file2.junk";
	repy_file* fp = repy_open(test_file_name, "w");
	if (fp == NULL) {
		return FAIL;
	}
	char * a = "Hello\n";
	char * b = "World\n";
	char ** lines = malloc(sizeof(char *)*3);
	lines[0] = a;
	lines[1] = b;
	lines[2] = NULL;
	repy_writelines(fp,lines) ;
	repy_flush(fp);

	repy_close(fp);
	free(lines);
	return PASS;
}

tresult test_seek() {
	char * test_file_name = "test_file2.junk";
	repy_file* fp = repy_open(test_file_name, "w");
	if (fp == NULL) {
		return FAIL;
	}
	repy_seek(fp, 0, 0);

	repy_close(fp);
	return PASS;
}


tresult test_read() {
	char * test_file_name = "readtest.junk";
	repy_file* fp = repy_open(test_file_name, "r");
	if (fp == NULL) {
		return FAIL;
	}

	char * space = malloc(500);
	int size = repy_read(space, 499, fp);
	if (size == -1) {
		return FAIL;
	}

	repy_close(fp);

	if(size == 499 &&
			strstr(space, "any emotion akin to love for Irene Adler") != NULL &&
			strstr(space, "He ") != NULL) {
		return PASS;
	} else {
		return FAIL;
	}

}

tresult test_readline() {
	char * test_file_name = "readtest.junk";
	repy_file* fp = repy_open(test_file_name, "r");

	if (fp == NULL) {
		return FAIL;
	}

	char * space = malloc(500);
	int size = repy_readline(space, 499, fp);
	repy_close(fp);
	if (size < 1) {
		return FAIL;
	}


	if(
			strstr(space, "To Sherlock Holmes she is always THE woman. I have seldom heard") != NULL &&
			strstr(space, "him mention her under any other name ") == NULL) {
		return PASS;
	} else {
		return FAIL;
	}

}


tresult test_exitall() {
	//repy_exitall(); works!
	return PASS;
}


tresult test_removefile() {
	//the sideeffect of this is that it creates FILENAME
	char * filename = "test_file2.junk";
	FILE * file;
	test_writelines();
	if ( (file = fopen(filename, "r")) ) {
        fclose(file);
	} else {
		fclose(file);
		return FAIL;
	}
	repy_removefile(filename);

	if ( (file = fopen(filename, "r")) ) {
        fclose(file);
        return FAIL;
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
	//for some reason repy launches 2 process,
	//this kills the second.
	rc = repy_init();
	if (rc) {
		printf("Problem loading repy: %d", rc);
		return rc;
	} else {
		run_test((&test_getmyup), "getmyip");
		run_test((&test_gethostbyname), "test_gethostbyname");
		run_test((&test_getruntime), "getruntime");
		run_test((&test_getrandomfloat), "getrandomfloat");
		run_test((&test_sleep), "sleep");
		run_test((&test_locking), "locking");
		run_test((&test_listdir), "listdir");
		run_test((&test_open_close), "Open and Close");
		run_test((&test_write_flush), "Write and Flush");
		run_test((&test_writelines), "Writelines");
		run_test((&test_seek), "Seek");
		run_test((&test_read), "Read");
		run_test((&test_readline), "Readline");
		run_test((&test_exitall), "Exitall");
		run_test((&test_removefile), "Removefile");
		repy_shutdown();
	}
	return 0;
}

