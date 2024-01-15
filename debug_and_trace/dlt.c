/****************************************************************************
 * Included Files
 ****************************************************************************/

#include "dlt.h"

/****************************************************************************
 * Pre-processor Definitions
 ****************************************************************************/
#define APPLICATION_ID (1)
#define MESSAGE_ID (0x55AA55AA)

typedef struct dlt_log
{
    uint32_t timestamp;
    uint8_t context_id : 4; /*[3:0]*/
    uint8_t level : 4; /*[7:4]*/
} __attribute__((packed)) dlt_log_t;

dlt_log_t log_group[MAX_MODULE_NUM];
static dlt_log_t *log_group_search(uint8_t context_id);

void dlt_register(void)
{
    for (uint8_t i = 0; i < MAX_MODULE_NUM; i++)
    {
        log_group[i].context_id = i;
        log_group[i].level = LOG_LEVEL_DEFA;
    }
}

uint8_t dlt_level_set(uint32_t context_id, uint8_t level)
{
    dlt_log_t *target = log_group_search(context_id);
    target->level = level;
}

typedef void *gdcn_core_handle_t;
__attribute__((weak)) void display_EVENT_DLT(gdcn_core_handle_t gdcn_handle, uint32_t message_id, uint8_t *data, uint16_t len)
{
    (void)gdcn_handle;
    // printf("message_id:%08X, data:%s, len:%d\n", message_id, data, len);
    printf("\n");
    for (uint8_t i = 0; i < len; i++)
    {
        printf("%02X ", data[i]);
    }
    printf("%s\n", &data[5]);
}

static dlt_log_t *log_group_search(uint8_t context_id)
{
    for (uint8_t i = 0; i < MAX_MODULE_NUM; ++i)
    {
        if (log_group[i].context_id == context_id)
        {
            return &log_group[i];
        }
    }
    return NULL;
}

bool logging(uint8_t context_id, uint8_t level, uint8_t *data, uint16_t len)
{
    dlt_log_t log;
    log.timestamp = gbl_mclocker(); //TODO: MSB or LSB?
    log.context_id = context_id;
    log.level = level;

    uint8_t temp[sizeof(dlt_log_t) + len];
    dlt_log_t *target = log_group_search(context_id);
    if (target == NULL)
    {
        return false;
    }

    memcpy(&temp[0], &log, sizeof(log));
    memcpy(&temp[sizeof(log)], data, len);

    if (target->level >= level)
    {
        gdcn_core_handle_t gdcn_handle;
        display_EVENT_DLT(gdcn_handle, MESSAGE_ID, temp, sizeof(dlt_log_t) + len);
    }
    return true;
}

uint8_t dlt_init(void)
{
    printf("dlt_init\n");
    memset(log_group, 0, sizeof(log_group));
    dlt_register();
}
uint8_t dlt_loop(void)
{
    printf("dlt_loop\n");
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
        uint8_t buf[] = "LOG_XXXX";
        memcpy(buf, "LOG_FATA", sizeof(buf));
        LOG_FATA(7, buf, sizeof(buf));
        memcpy(buf, "LOG_ERRO", sizeof(buf));
        LOG_ERRO(7, buf, sizeof(buf));
        memcpy(buf, "LOG_WARN", sizeof(buf));
        LOG_WARN(7, buf, sizeof(buf));
        memcpy(buf, "LOG_INFO", sizeof(buf));
        LOG_INFO(7, buf, sizeof(buf));
        memcpy(buf, "LOG_DEBU", sizeof(buf));
        LOG_DEBU(7, buf, sizeof(buf));
        memcpy(buf, "LOG_VERB", sizeof(buf));
        LOG_VERB(7, buf, sizeof(buf));
    }
    else if (!STRNCMP(argv[1], "level"))
    {
        uint32_t context_id = strtol(argv[2], NULL, 16);
        uint8_t level = strtol(argv[3], NULL, 16);
        dlt_level_set(context_id, level);
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
