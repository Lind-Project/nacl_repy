/* is this a stnadalone test, or running in nacl? */
#ifdef __native_client__
#include <repy.h>
#else
#include "../src/repy.h"
#endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>
#include "unittest.h"


tresult test_udp_messages() {
  int i;
  for(i = 0; i < 1000; i++) {
    if ((i % 10) == 0) {
      printf(".");
      fflush(stdout);
    }
    char * loopback = "127.0.0.1";
    int dest = 12345;
    char * m = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()\n";
    int message_size = 500;
    char * buffer = (char *) calloc(1, message_size);
    repy_udpserver_handle server = repy_listenformessage(loopback, dest);
    if (server == -1) {
      repy_perror("UDP Test");
      return fail("no message server pointer after server open.");
    }
  
    long int rc = repy_sendmessage(loopback, dest, m, loopback, 12346);
    if (rc < 1) {
      repy_perror("UDP Test");
      return fail("failed to send UDP message");
    }
    repy_message * new_message = repy_udpserver_getmessage(buffer,message_size, server);
    repy_close_udpserver(server);
  
    if(new_message == NULL) {
      repy_perror("UDP Test");
      return fail("new message was null");
    }
  
    if ( new_message->message == NULL) {
      repy_perror("UDP Test");
      return fail("new_message message was null");
    }
  
    if (strstr(new_message->message, m)==NULL) {
      repy_perror("UDP Test");
      return fail("message did not match expected");
    }
  }
  return PASS;
  
}


void run_tests() {
	  run_test((&test_udp_messages), "UDP Hammer Test");
	 

}

