#include <stdio.h>
#include "unittest.h"



int run = 0;
int passed = 0;

void run_test(tresult(*func)(void), char * name) {
  run++;
  printf("Running Test %d: %s... ", run, name);
  fflush(stdout);
  int rc = func();
  if (rc == PASS) {
    passed++;
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

int get_runs() {
  return run;
}

int get_passed() {
  return passed;
}


tresult fail(char * message) {
	printf("\nFAILURE: %s\n", message);
	return FAIL;
}
