

/* Run the repy test suite in user mode without NaCl integration.
 */
#include "repy_test_headers.h"

extern void run_tests();


int main(int argc, char** argv) {

  int repy_tests_rc = 0;
  repy_tests_rc = repy_main(argc, argv);

  return repy_tests_rc;

}


