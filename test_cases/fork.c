#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <wait.h>

int main(void)
{
	int ppid = -1, cpid = -1, pret = 0, cret = 0;
	static const char c1[] = "child waiting\n", c2[] = "child succeeded\n";
	static const char p1[] = "parent waiting\n", p2[] =  "parent succeeded\n";

	puts("parent forking");
	fflush(0);

	/*
	 * printf("%d\n", getpid());
	 * fork();
	 * puts("hi");
	 * fflush(0);
	 * exit(EXIT_SUCCESS);
	 */

	switch ((ppid = fork())) {
	case -1:
		perror("fork() failed");
		fflush(0);
		/* _exit(EXIT_FAILURE); */
		exit(EXIT_FAILURE);

	case 0:
		puts("child forking");
		fflush(0);
		switch ((cpid = fork())) {
		case -1:
			perror("fork() failed");
			fflush(0);
			exit(EXIT_FAILURE);
		case 0:
			/* printf("child %d succeeded\n", getpid()); */
			printf("child %d succeeded\n", 3);
			fflush(0);
			write(STDOUT_FILENO, c2, sizeof c2 - 1);
			exit(EXIT_SUCCESS);
		}

		write(STDOUT_FILENO, c1, sizeof c1 - 1);
		if (waitpid(cpid, &cret, 0) == -1)
			perror("child");
		/* printf("child waitpid ret: %d\n", waitpid(cpid, &cret, 0)); */
		fflush(0);
		/* printf("child %d succeeded after waiting on %d\n", getpid(), cpid); */
		printf("child %d succeeded after waiting on %d\n", 2, cpid);
		fflush(0);
		write(STDOUT_FILENO, c2, sizeof c2 - 1);
		exit(EXIT_SUCCESS);
	}

	/* printf("%d\n", getpid()); */
	fflush(0);
	write(STDOUT_FILENO, p1, sizeof p1 - 1);
	if (waitpid(ppid, &pret, 0) == -1)
		perror("parent");
	/* printf("parent wait ret: %d\n", wait(&pret)); */
	fflush(0);
	/* printf("parent %d succeeded after waiting on %d\n", getpid(), ppid); */
	printf("parent %d succeeded after waiting on %d\n", 1, ppid);
	fflush(0);
	write(STDOUT_FILENO, p2, sizeof p2 - 1);

	switch ((ppid = fork())) {
	case -1:
		perror("fork() failed");
		fflush(0);
		exit(EXIT_FAILURE);
	case 0:
		/* printf("child %d succeeded\n", getpid()); */
		printf("child %d succeeded\n", 2);
		fflush(0);
		write(STDOUT_FILENO, c2, sizeof c2 - 1);
		exit(EXIT_SUCCESS);
	}
	write(STDOUT_FILENO, c1, sizeof c1 - 1);
	if (waitpid(ppid, &pret, 0) == -1)
		perror("parent");
	/* printf("parent wait ret: %d\n", wait(&pret)); */
	fflush(0);
	/* printf("parent %d succeeded after waiting on %d\n", getpid(), ppid); */
	printf("parent %d succeeded after waiting on %d\n", 1, ppid);
	fflush(0);
	write(STDOUT_FILENO, c2, sizeof c2 - 1);

	/* _exit(EXIT_SUCCESS); */
	return 0;
}
