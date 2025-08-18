#include <stdio.h>
#include <stdint.h>
#include "auo.h"
#include "socket_server.h"


void print_hello()
{
    int num = TEST1;
    printf("Hello, World!:%d\n", num);
}

void command_parser(void *data, uint16_t len)
{
    // Example command parser function
    if (data == NULL || len == 0) {
        printf("Invalid data or length\n");
        return;
    }
    else
    {
        printf("Command parser called with data length: %d\n", len);
    }
}

void auo_init()
{
    printf("auo_init\n");
    socket_server_cb_read_register(command_parser);
}