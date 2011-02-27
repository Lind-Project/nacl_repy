#include <repy.h>

#define REPY_FTABLE_MAX_SIZ 1024



typedef struct filehandles_s {
  /* The file handles themselves */
  void ** file_handles;
  
  /* Hint so we know where to start searching for free table spots */
  int last_allocated;
  
  /* Current number of entires in the table */
  int ftable_siz;
} fhandle_t;


/* Setup a table to store the repy file handles
 */
void repy_ft_inithandles();

int repy_ft_size();

int repy_ft_set_handle(void * handle);

void * repy_ft_get_handle(int handle_no);

void repy_ft_clear(int handle_no);

/* Only exposed for testing. */
int handle_to_index(int handle);
int index_to_handle(int index);
