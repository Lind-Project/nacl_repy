#ifdef __native_client__
#include <repy.h>
#else
#include "../src/repy.h"
#endif

#include <stdio.h>
#include "unittest.h"



int repy_main(int argc, char** argv) {
	int rc = 0;
	
	rc = repy_init();
	
	if (rc) {
	  printf("Problem loading repy: %d", rc);
	  return rc;
	} else {
	  double start = repy_getruntime();
	  run_tests();
	  double end = repy_getruntime();
	  printf("Tests took %f to run. %d/%d tests passed\n",end-start, get_passed(), get_runs());
	  printf("\n");
	  fflush(stdout);
	  repy_exitall();
	  printf("You should never see this message!\n it means exitall did not work.\n");
	}
	return 0;
}

