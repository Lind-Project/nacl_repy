

/* Run the repy test suite in user mode without NaCl integration.
 */
#include "repy_test_headers.h"


int main(int argc, char** argv) {

  int handle_rc = 0;
  int repy_tests_rc = 0;
  handle_rc = handle_main();
  repy_tests_rc = repy_main(argc, argv);

  return handle_rc + repy_tests_rc;

}
