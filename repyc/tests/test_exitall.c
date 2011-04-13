#ifdef __native_client__
#include <repy.h>
#else
#include "../src/repy.h"
#endif

#include <stdio.h>


int repy_main(int argc, char** argv) {
	int rc = 0;
	
	rc = repy_init();
	
	if (rc) {
	  printf("Problem loading repy: %d", rc);
	  return rc;
	} else {
	  repy_exitall();
	  printf("Error: You should never see this message!\n it means exitall did not work.\n");
	}
	return 0;
}





