#define HTTP_STATUS_FORBIDDEN 403
#define HTTP_STATUS_INTERNAL_ERROR 500
#define HTTP_STATUS_BAD_REQUEST 400
#define HTTP_STATUS_NOT_FOUND 404

#define SLEEP_DEVICE "sleep"

extern char *allowed_devices[];

/**
 * display a error page with the given status code and the given message
 * as text.
 */
void http_error(int status, char* msg);

/**
 * check if the given character is alphanumeric, i.e. a-zA-Z0-9
 */
int is_alphanumeric(char c);

/**
 * check if a device with the given name exists and is valid
 */
int device_valid(char* name);

/**
 * check if a command is valid.
 */
int command_valid(char *cmd);
