#ifndef SOCKET_SERVER_H
#define SOCKET_SERVER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif

int socket_server_init(void);
int socket_server_loop(void);
void socket_server_cb_read_register(void *cb);
void socket_server_write(int32_t client_fp, uint8_t *data, uint16_t len);
void socket_server_close(void);

#ifdef __cplusplus
}
#endif

#endif /* SOCKET_SERVER_H */