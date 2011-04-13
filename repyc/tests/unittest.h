

typedef enum t_result {
	PASS, FAIL, BROKEN
} tresult;

tresult fail(char * message);
	


void run_test(tresult(*func)(void), char * name);
int get_runs();
int get_passed();
