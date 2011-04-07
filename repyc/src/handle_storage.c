#include <stdio.h>
#include <stdlib.h>
#include <repy.h>
#include <assert.h>
#include "handle_storage.h"


int handle_to_index(int handle) {
  /* if we have a remainder, some one screwed up! */
  if((handle%1025) != 0) {
    return -1;
  }
  return (handle/1025) -1;

}

int index_to_handle(int index) {
  return (index + 1) * 1025;
}

static fhandle_t* file_storage = NULL;

/* Setup a table to store the repy file handles
 */
void repy_ft_inithandles() {
  file_storage = (fhandle_t*) calloc(1,sizeof(struct filehandles_s));
  file_storage->file_handles = calloc(1,sizeof(void*) * REPY_FTABLE_MAX_SIZ);
  file_storage->last_allocated = 0;
  file_storage->ftable_siz = 0;
}

void repy_ft_teardown(){
  free(file_storage->file_handles);
  free(file_storage);
}

int repy_ft_size() {
  return file_storage->ftable_siz;
}

int repy_ft_set_handle(void * handle) {
  if (file_storage->last_allocated == -1 ||
      file_storage->ftable_siz >= REPY_FTABLE_MAX_SIZ -1 ) {
    fprintf(stderr, "handle_storage: handle table is full.\n");
    return -1;
  }
  
  int curr = file_storage->last_allocated + 1;
  while(1){
    if (file_storage->file_handles[curr] == NULL) {
      file_storage->file_handles[curr] = handle;
      break;
    } else {
      curr = (curr + 1) % REPY_FTABLE_MAX_SIZ;
    }
  }

  file_storage->ftable_siz++;
  file_storage->last_allocated = curr;
  return index_to_handle(curr);
}

void * repy_ft_get_handle(int handle_no) {
  int position = handle_to_index(handle_no);
  if (position >= REPY_FTABLE_MAX_SIZ || position < 0) {
    goto bad_index;
  }
  if (file_storage->file_handles != NULL && file_storage->file_handles[position] != NULL) {
    return file_storage->file_handles[position];
  } else {
    goto bad_index;
  }
bad_index:
  fprintf(stderr, "repy_filetable: attempting to access invalid index. %d->%d\n", handle_no, position);
   return NULL;
}

void repy_ft_clear(int handle_no) {

  file_storage->file_handles[handle_to_index(handle_no)] = NULL;
  file_storage->ftable_siz--;

}
