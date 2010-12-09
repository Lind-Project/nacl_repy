/*
 * hello.c
 *
 *  Created on: 2010-12-07
 *      Author: cmatthew
 */

#include <repy.h>
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) {
	int rc = 0;

	rc = repy_init();
	if (rc) {
		printf("Problem loading repy: %d", rc);
		return rc;
	} else {
		printf("Repy Says: %s", repy_getmyip());
		return repy_shutdown();
	}

}

