/*
 * lirc.c
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


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdbool.h>
#include "lirc.h"
#include "lirc-send.h"

char *allowed_devices[] = {
	"rgb",
	"dvd"
};

int device_valid(char* name)
{
	if (name == NULL) {
		return false;
	}
	
	if (strlen (name) <= 1) {
		return false;
	}

	// special device "sleep"
	if (strcmp (name, SLEEP_DEVICE) == 0) {
		return true;
	}
	
	for (char **dev = allowed_devices; *dev; dev++) {
		if (strcmp (*dev, name) == 0) {
			return true;
		}
	}

	return 0;
}

int is_alphanumeric(char c)
{
	return (c >= 'a' && c <= 'z') ||
		(c >= 'A' && c <= 'Z') ||
		(c >= '0'&& c <= '9');
}

int command_valid(char *name)
{
	if (name == NULL) {
		return false;
	}
	
	if (strlen (name) <= 1) {
		return false;
	}

	int cmd_len = strlen (name);

	// CMDs have to have at least 2 characters.
	if (cmd_len <= 1) {
		return true;
	}

	// check that the command is alphanumeric/underscores only.
	for (char *i = name; *i ; i++) {
		if (!is_alphanumeric(*i) && *i != '_') {
			return false;
		}
	}

	return true;
}

void http_error(int status, char* msg)
{
	int status_code = status;
	char *status_message;

	switch (status) {
		case HTTP_STATUS_BAD_REQUEST:
			status_message = "Bad Request";
		break;
		case HTTP_STATUS_FORBIDDEN:
			status_message = "Forbidden";
		break;
		case HTTP_STATUS_NOT_FOUND:
			status_message = "Not Found";
		break;
		default:
		case HTTP_STATUS_INTERNAL_ERROR:
			status_code = 500;
			status_message = "Internal Error";
		break;
	}
	
	printf ("Status: %d %s\r\n", status_code, status_message);
	printf ("Content-type: text/html;charset=utf8\r\n");
	printf ("\r\n");
	printf ("<h1>Ein Fehler ist aufgetreten!</h1><p>%s</p>", msg);
	exit (0);
}

int main(int argc, char **argv)
{
	char* path_info = getenv("PATH_INFO");

	if (path_info == NULL) {
		http_error (HTTP_STATUS_NOT_FOUND, "The requested action could not be found.");
	}

	// PATH_INFO always starts with a slash, and that is not a valid
	// device.
	if (strlen (path_info) <= 1) {
		http_error (HTTP_STATUS_NOT_FOUND, "The requested action could not be found.");
	}

	// strip the first char from PATH_INFO, that is the device.
	char* action_candidate = path_info + 1;
	
	if (strcmp(action_candidate, "devlist") == 0) {
		//list_devices();
	} else if (strcmp(action_candidate, "sendcmd") == 0) {
		send_command();
	} else {
		http_error (HTTP_STATUS_NOT_FOUND, "The requested action could not be found.");
	}
}

