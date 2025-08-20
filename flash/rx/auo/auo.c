#include <stdio.h>
#include <stdint.h>
#include "auo.h"
#include "socket_server.h"


void print_hello()
{
    int num = TEST1;
    printf("Hello, World!:%d\n", num);
}

void command_parser(int32_t client_fp, void *data, int32_t len)
{
    printf("Command parser called with client %d, data length %d\n", client_fp, len);
    uint8_t a[5] = "aacc"; // Example modification
    socket_server_write(client_fp, a, len-1);
}

void auo_init()
{
    printf("auo_init\n");
    socket_server_init();
    socket_server_cb_read_register(command_parser);
}

void auo_loop()
{
    // printf("auo_loop\n");
    socket_server_loop();
}