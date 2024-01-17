#ifndef DLT_H
#define DLT_H

#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include "gbl_console.h"
#include "gbl_stdio.h"
#include "gbl_string.h"
#include "gbl_time.h"
#include "dlt.h"
#include "dlt_cfg.h"

typedef enum
{
    TEST = 0,
    BTLD = 1,
    OSYS = 2,
    GDCN = 3,
    LINK = 4,
    WARP = 5,
    FLSH = 6,
    TOCH = 7,
    DIBL = 8,
    SAFE = 9,
    PERI = 10,
    MISC = 11,
    MAX_MODULE_NUM,
} CONTEXT_ID_E;

// LOG LEVEL
#define LOG_LEVEL_NONE 0x00
#define LOG_LEVEL_FATA 0x01
#define LOG_LEVEL_ERRO 0x02
#define LOG_LEVEL_WARN 0x03
#define LOG_LEVEL_INFO 0x04
#define LOG_LEVEL_DEBU 0x05
#define LOG_LEVEL_VERB 0x06
#define LOG_LEVEL_DEFA LOG_LEVEL_WARN

#define LOG_FATA(context_id, data, len) logging(context_id, LOG_LEVEL_FATA, data, len)
#define LOG_ERRO(context_id, data, len) logging(context_id, LOG_LEVEL_ERRO, data, len)
#define LOG_WARN(context_id, data, len) logging(context_id, LOG_LEVEL_WARN, data, len)
#define LOG_INFO(context_id, data, len) logging(context_id, LOG_LEVEL_INFO, data, len)
#define LOG_DEBU(context_id, data, len) logging(context_id, LOG_LEVEL_DEBU, data, len)
#define LOG_VERB(context_id, data, len) logging(context_id, LOG_LEVEL_VERB, data, len)


void dlt_register(void);
uint8_t dlt_level_set(uint32_t context_id, uint8_t level);
uint8_t dlt_init(void);
uint8_t dlt_loop(void);
bool dlt_console(int argc, char *argv[]);

#endif /*DLT_H*/
