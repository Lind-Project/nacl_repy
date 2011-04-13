/** Storage table for repy file handles.
 * Allocates a table, then allows storage and removal of file handles.
 */

#include <stdio.h>
#include <stdlib.h>
#ifdef __native_client__
#include <repy.h>
#else
#include "../src/repy.h"
#endif

#include <assert.h>
#include "../src/handle_storage.h"
#include "repy_test_headers.h"

int main() {
  int handle_rc = 0;
  handle_rc = handle_main();
  return handle_rc;
}

int handle_main() {
  int i;
  //check all numbers map correctly and back
  for(i=0; i<2050; i++) {
    assert(handle_to_index(index_to_handle(i)) == i);
  }

  //make sure a null missing or invalid handle does not work
  assert (handle_to_index(0) == -1);
  assert(handle_to_index(5) == -1);
  assert(handle_to_index(1024) == -1);

  repy_ft_inithandles();
  assert(repy_ft_size() == 0);

  /* fill */
  const int NUM_SPOTS = 1023;
  int spots[NUM_SPOTS];
  for(i=0; i<NUM_SPOTS; i++) {
    void * fake_ptr = (void *) 1000000 + i;
    spots[i] = repy_ft_set_handle((repy_handle*)fake_ptr);
    assert(spots[i] != -1);
   
  }  

  /* now check */
  for (i=0; i<NUM_SPOTS; i++) {
    void * fake_ptr = (void *) 1000000 + i;
    assert(repy_ft_get_handle(spots[i])==fake_ptr);
  }
  /* table should be full now */
  assert(repy_ft_set_handle((repy_handle*)100) == -1);
  repy_ft_clear(spots[10]);
  /* not full anymore */
  assert(-1 != repy_ft_set_handle((repy_handle*)500));
  /* full again */
  assert(repy_ft_set_handle((repy_handle*)100) == -1);

  repy_ft_teardown();

  return 0;

}
