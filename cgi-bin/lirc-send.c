/*
 * lirc-send.c
 * 
 * Copyright 2013 Nico Boehr <nico@zoff>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 * 
 * 
 */


#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include "lirc.h"
#include "lirc-send.h"

void send_command()
{
	char *qstr = getenv("QUERY_STRING");

	if (qstr == NULL) {
		http_error (HTTP_STATUS_BAD_REQUEST, "Query string is empty!");
	}

	// copy the query string
	char *query_string = strndup (qstr, 200);

	if (query_string == NULL) {
		http_error (HTTP_STATUS_INTERNAL_ERROR, "Memory error");
	}

	// we will allow at most 20 commands in one request
	// i.e. we use a char array with 40 entries, the odd indexes contrain
	// a pointer to the device name, the even entries a pointer to the
	// command name.
	char *commands[41];

	for (int i = 0; i < 41; i++) {
		commands[i] = 0;
	}


	char *saveptr;

	char *token;
	char *query_string_arg = query_string;
	int i;
	for (i = 0; i < 39; i+=2) {
		token = strtok_r (query_string_arg, ";", &saveptr);
		query_string_arg = NULL;

		if (token == NULL) {
			break;
		}

		char *sep = strchr (token, '|');

		if (sep == NULL || (sep + 1) == NULL) {
			http_error (HTTP_STATUS_BAD_REQUEST, "Command was malformed.");
		}

		// skip the pipe
		sep++;

		// copy the device name
		size_t device_id_length = sep - token;
		commands[i] = malloc (device_id_length + 1);

		if (commands[i] == NULL) {
			http_error (HTTP_STATUS_INTERNAL_ERROR, "Memory error");
		}
		
		strncpy (commands[i], token, device_id_length - 1);

		if (!device_valid (commands[i])) {
			http_error (HTTP_STATUS_BAD_REQUEST, "Unknown device");
		}

		// and the command
		size_t cmd_id_length = strlen (sep);
		commands[i + 1] = malloc (cmd_id_length + 1);

		if (commands[i + 1] == NULL) {
			http_error (HTTP_STATUS_INTERNAL_ERROR, "Memory error");
		}
		
		strncpy (commands[i + 1], sep, cmd_id_length);

		if (!command_valid (commands[i + 1])) {
			http_error (HTTP_STATUS_BAD_REQUEST, "Unknown command");
		}
	}

	printf ("Status: 200 OK\r\n\r\n");
	for (char **dev = commands; *dev; dev+=2) {
		char *device = *dev;
		char *cmd = *(dev + 1);

		if (strcmp (device, SLEEP_DEVICE) == 0) {

			char *endptr;
			long sleep_amnt = strtol(cmd, &endptr, 10);

			if (*endptr != 0 || sleep_amnt >= 5000) {
				http_error (HTTP_STATUS_BAD_REQUEST, "Invalid sleep amount!");
			}

			usleep (sleep_amnt * 1000);
			
		} else {
			char *child_argv[] = {
				"irsend",
				"SEND_ONCE",
				device,
				cmd,
				(char *) NULL
			};

			pid_t child = fork ();

			// we are in the child
			if (child == 0) {
				int code = execvp ("irsend", child_argv);

				if (code == -1) {
					exit (1);
				}
			}

			int status;
			waitpid (child, &status, 0);

			// error occured in the child
			if (WEXITSTATUS(status) != 0) {
				http_error (HTTP_STATUS_INTERNAL_ERROR, "LIRC error");
			}
		}
	}

	printf ("Status: 200 OK\r\n");
	printf ("Content-Type: application/json;charset=utf8\r\n\r\n");

	printf ("{\"success\":true}\r\n");
}
