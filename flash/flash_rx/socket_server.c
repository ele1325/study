#include <stdio.h>
#include <stdint.h>
#include "socket_server.h"

#ifdef WIN32
#include <conio.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib") // Winsock Library

#define sleep Sleep

#else

#include <string.h> //strlen
#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write

#endif

// -----------------------------------------------------------------------------
//
#define MAX_CLIENT_CNT 4

static int server = -1;
static int client_list[MAX_CLIENT_CNT] = {-1};
static int client_list_cnt = 0;

void socket_server_read(int client_fp);
void socket_client_add(int client_fp);
void socket_client_del(int client_fp);

typedef void (*cb_function_t)(int32_t, void *, int32_t);
cb_function_t server_cb_read = NULL;

void socket_server_cb_read_register(void *cb)
{
    server_cb_read = (cb_function_t)cb;
}

int socket_server_init(void)
{
    int r = -1;

    // Initial Multi client
    for (int i = 0; i < MAX_CLIENT_CNT; i++)
    {
        client_list[i] = -1;
    }
    client_list_cnt = 0;
#ifdef WIN32
    WSADATA wsaData;
    // Initialize Winsock
    r = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (r != 0)
    {
        printf("WSAStartup failed with error: %d\n", r);
        server = -1;
        return -1;
    }
#endif
    // Create socket
    int sock;
    sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == -1)
    {
        printf("Could not create socket");
        server = -1;
        return 0;
    }

#ifdef WIN32
    unsigned long flag = 1;
    if (ioctlsocket(sock, FIONBIO, &flag) == SOCKET_ERROR)
    {
        printf("Unable to set nonblocking mode\n");
        goto exit;
    }
#else
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);
#endif

    // Prepare the sockaddr_in structure
    struct sockaddr_in server_sockaddr;
    server_sockaddr.sin_family = AF_INET;
    server_sockaddr.sin_addr.s_addr = INADDR_ANY;
    server_sockaddr.sin_port = htons(27015);

    // Bind
    if (bind(sock, (struct sockaddr *)&server_sockaddr, sizeof(server_sockaddr)) < 0)
    {
        printf("bind failed\n");
        goto exit;
    }
    else
    {
        printf("bind done\n");
    }

    // Listen
    if (listen(sock, 3) == SOCKET_ERROR)
    {
        printf("listen failed\n");
        goto exit;
    }
    server = sock;

    return sock;

exit:
#ifdef WIN32
    WSACleanup();
#endif
    closesocket(sock);
    server = sock;

    return sock;
}

int socket_server_loop(void)
{
    int r = -1;

    struct sockaddr_in sockaddr;
    int socklen = sizeof(struct sockaddr_in);
    char buff[8];
    int sock_client = -1;

    if (client_list_cnt < MAX_CLIENT_CNT)
    {
        sock_client = accept(server, (struct sockaddr *)&sockaddr, (socklen_t *)&socklen);

        if (sock_client == SOCKET_ERROR)
        {
    #ifdef WIN32
            if (WSAGetLastError() != WSAEWOULDBLOCK)
            {
                //                    printf("accept failed with error: %d\n", WSAGetLastError());
            }
    #else
            if (errno != EWOULDBLOCK)
            {
                //                    printf("accept failed with error: %d\n", errno);
            }
    #endif
        }
        else
        {
            socket_client_add(sock_client);
            printf("Connection accepted\n");
        }
    }

    if (client_list_cnt > 0)
    {
        for (int i = 0; i < client_list_cnt; i++)
        {
            r = recv(client_list[i], buff, 1, MSG_PEEK);
            if (r <= 0)
            {
#ifdef WIN32
                if (r == 0 || WSAGetLastError() == WSAECONNRESET)
#else
                if (r == 0 || errno == ECONNRESET || errno == EWOULDBLOCK)
#endif
                {
                    printf("disconnected:%d\n", errno);
                    closesocket(client_list[i]);
                    socket_client_del(client_list[i]);
                }
            }
            else
            {
                socket_server_read(client_list[i]);
            }
        }
    }

    return sock_client;
}

void socket_server_write(int32_t client_fp, uint8_t *data, uint16_t len)
{
    if (client_fp == -1)
        return;

    send(client_fp, data, len, 0);
}

void socket_server_read(int client_fp)
{
    if (client_fp == -1)
        return;

    int r;
    char buff[4095];
    r = recv(client_fp, buff, sizeof(buff), 0);
    if (r <= 0)
    {
        if (r == 0)
        {
            printf("Client disconnected\n");
        }
        else
        {
#ifdef WIN32
            if (WSAGetLastError() != WSAEWOULDBLOCK)
#else
            if (errno != EWOULDBLOCK)
#endif
            {
                printf("recv failed with error: %d\n", errno);
            }
        }
        closesocket(client_fp);
        socket_client_del(client_fp);
    }
    else
    {
        buff[r] = '\0';
        if (server_cb_read != NULL)
        {
            server_cb_read(client_fp, buff, r+1);
        }
    }
}

void socket_client_add(int client_fp)
{
    if(client_list_cnt < MAX_CLIENT_CNT)
        client_list[client_list_cnt++] = client_fp;
}

void socket_client_del(int client_fp) // 把斷線的client從list中移除，並把list向前排滿
{
    for (int i = 0; i < client_list_cnt; i++)
    {
        if (client_list[i] == client_fp)
        {
            for (int j = i; j < client_list_cnt - 1; j++) // client_list_cnt - 1 預留list中往前移的list index，若條件沒達成，表示預刪除client在最後一個
            {
                client_list[j] = client_list[j + 1];
            }
            client_list[--client_list_cnt] = -1; // 因已將list向前排滿，所以只需將list中最後一個client改回-1，表示未連接
            break;
        }
    }
}

void socket_server_close(void)
{
    for(int i = 0; i < MAX_CLIENT_CNT; i++)
    {
        if (client_list[i] != -1)
        {
            closesocket(client_list[i]);
            client_list[i] = -1;
        }
    }
    
    if (server != -1)
    {
        closesocket(server);
        server = -1;
    }

#ifdef WIN32
    WSACleanup();
#endif

    printf("Server and client sockets closed\n");
}
