/****************************************************************************
 * Included Files
 ****************************************************************************/

#include "dlt.h"
#include "gbl_rb.h"

#define MESSAGE_ID (0x55AA55AA)
#define PRE_PAYLOAD_SIZE (5) /*timestamp 4byte + context+level 1byte*/
#define BUFFER_FULL_MSG "log buffer is full!!"
gbl_rb_t log_rb;

typedef struct dlt_log
{
    uint32_t timestamp;
    uint8_t context_id : 4; /*[3:0]*/
    uint8_t level : 4;      /*[7:4]*/
    uint8_t payload[PAYLOAD_SIZE];
    uint16_t len;
} __attribute__((packed)) dlt_log_t;

dlt_log_t log_buffer[LOG_BUFFER_SIZE];

uint8_t level_cfg[CONTEXT_ID_NUM];

uint8_t busyflag = 0;

cb_connect_check_t connect_check = NULL;

void dlt_cb_connect_check_register(cb_connect_check_t cb)
{
    connect_check = cb;
}

__attribute__((weak)) bool connect(void)
{
    return busyflag;
}

void dlt_log_level_init(void)
{
    for (uint8_t i = 0; i < CONTEXT_ID_NUM; i++)
    {
        level_cfg[i] = LOG_LEVEL_DEFA;
    }
}

uint8_t dlt_level_set(uint32_t context_id, uint8_t level)
{
    level_cfg[context_id] = level;
}

uint8_t dlt_store(uint8_t *data)
{
    uint8_t ret = 0;
    if (gbl_rb_remain(&log_rb) > 1)
    {
        ret = gbl_rb_write(&log_rb, data, 1, true);
        if (ret != 1)
            printf("gbl_rb_write fail:%d\n", ret);
    }
    else
    {
        dlt_log_t full_log = {
            .timestamp = gbl_mclocker(),
            .context_id = 1,
            .level = 1,
            .payload = BUFFER_FULL_MSG,
            .len = sizeof(BUFFER_FULL_MSG),
        };
        ret = gbl_rb_write(&log_rb, (uint8_t *)&full_log, 1, true);
        if (ret != 1)
            printf("gbl_rb_write fail:%d\n", ret);
    }
    return ret;
}

uint8_t dlt_restore(uint8_t *data)
{
    gbl_rb_read(&log_rb, data, 1, true);
    return 1;
}

typedef void *gdcn_core_handle_t;
__attribute__((weak)) void display_EVENT_DLT(gdcn_core_handle_t gdcn_handle, uint32_t message_id, uint8_t *data, uint16_t len)
{
    (void)gdcn_handle;
    // printf("message_id:%08X, data:%s, len:%d\n", message_id, data, len);
    for (uint8_t i = 0; i < PRE_PAYLOAD_SIZE; i++)
    {
        printf("%02X ", data[i]);
    }
    printf("%s", &data[PRE_PAYLOAD_SIZE]);
}

bool dlt_logging(uint8_t context_id, uint8_t level, uint8_t *data, uint16_t len)
{

    // dlt_log_t *target = log_group_search(context_id);
    if (context_id >= CONTEXT_ID_NUM)
    {
        return false;
    }

    if (level <= level_cfg[context_id])
    {
        dlt_log_t log = {
            .timestamp = gbl_mclocker(), // TODO: 0.1ms
            .context_id = context_id,
            .level = level,
            .len = len,
        };
        memset(log.payload, 0, PAYLOAD_SIZE);
        memcpy(log.payload, data, len);

        if(connect_check == NULL)
        {
            printf("connect_check callback is not registered\n ");
            return false;
        }

        if (connect_check() == 0)
        {
            gdcn_core_handle_t gdcn_handle;
            display_EVENT_DLT(gdcn_handle, MESSAGE_ID, (uint8_t *)&log, log.len + PRE_PAYLOAD_SIZE);
        }
        else
        {
            dlt_store((uint8_t *)&log);
        }
    }
    return true;
}

uint8_t dlt_init(void)
{
    if (gbl_rb_init(&log_rb, log_buffer, LOG_BUFFER_SIZE * sizeof(dlt_log_t), LOG_BUFFER_SIZE, sizeof(dlt_log_t)) != 0)
        printf("gbl_rb_init fail\n");
    dlt_cb_connect_check_register(connect);
    dlt_log_level_init();
}
uint8_t dlt_loop(void)
{
    if (!gbl_rb_is_empty(&log_rb) && connect_check() == 0)
    {
        dlt_log_t log;
        dlt_restore((uint8_t *)&log);
        gdcn_core_handle_t gdcn_handle;
        display_EVENT_DLT(gdcn_handle, MESSAGE_ID, (uint8_t *)&log, log.len + PRE_PAYLOAD_SIZE);
    }
}
bool dlt_console(int argc, char *argv[])
{
    if (argc < 2)
        return false;

    if (STRNCMP(argv[0], "dlt"))
        return false;

    if (!STRNCMP(argv[1], "help"))
    {
        printf("dlt log \n");
        printf("dlt level [context_id] [level]\n");
    }
    else if (!STRNCMP(argv[1], "log"))
    {
        dlt_f(GDCN, "DLT_FATA, val_1:%d, val_2:%d\n", 5, 9);
        dlt_e(GDCN, "DLT_ERRO, val_1:0x%02X\n", 0x50);
        dlt_w(GDCN, "DLT_WARN, string:%s\n", "ssssss");
        dlt_i(GDCN, "DLT_INFO\n");
        dlt_d(GDCN, "DLT_DEBU\n");
        dlt_v(GDCN, "DLT_VERB\n");
    }
    else if (!STRNCMP(argv[1], "level"))
    {
        uint32_t context_id = strtol(argv[2], NULL, 16);
        uint8_t level = strtol(argv[3], NULL, 16);
        dlt_level_set(context_id, level);
    }
    else if (!STRNCMP(argv[1], "busy"))
    {
        uint8_t val = strtol(argv[2], NULL, 16);
        busyflag = val;
        printf("busyflag:%d\n", busyflag);
    }
    else if (!STRNCMP(argv[1], "full"))
    {
        printf("full:%d\n", gbl_rb_is_full(&log_rb));
    }
    else if (!STRNCMP(argv[1], "test"))
    {
        printf("dlt_console test\n");
    }
    else
    {
        return false;
    }

    return true;
}
