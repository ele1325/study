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
    CONTEXT_ID_TEST = 0,
    CONTEXT_ID_BTLD = 1,
    CONTEXT_ID_OSYS = 2,
    CONTEXT_ID_GDCN = 3,
    CONTEXT_ID_LINK = 4,
    CONTEXT_ID_WARP = 5,
    CONTEXT_ID_FLSH = 6,
    CONTEXT_ID_TOCH = 7,
    CONTEXT_ID_DIBL = 8,
    CONTEXT_ID_SAFE = 9,
    CONTEXT_ID_PERI = 10,
    CONTEXT_ID_MISC = 11,
    CONTEXT_ID_NUM,
} CONTEXT_ID_E;

// LOG LEVEL
typedef enum
{
    LOG_LEVEL_NONE = 0,
    LOG_LEVEL_FATA = 1,
    LOG_LEVEL_ERRO = 2,
    LOG_LEVEL_WARN = 3,
    LOG_LEVEL_INFO = 4,
    LOG_LEVEL_DEBU = 5,
    LOG_LEVEL_VERB = 6,
    LOG_LEVEL_DEFA = LOG_LEVEL_WARN,
} LOG_LEVEL_E;

#define PAYLOAD_SIZE (100)
#define LOG_BUFFER_SIZE (10)

#define dlt_gdcn_f(format, ...) LOG(CONTEXT_ID_GDCN, LOG_LEVEL_FATA, format, ##__VA_ARGS__)
#define dlt_gdcn_e(format, ...) LOG(CONTEXT_ID_GDCN, LOG_LEVEL_ERRO, format, ##__VA_ARGS__)
#define dlt_gdcn_w(format, ...) LOG(CONTEXT_ID_GDCN, LOG_LEVEL_WARN, format, ##__VA_ARGS__)
#define dlt_gdcn_i(format, ...) LOG(CONTEXT_ID_GDCN, LOG_LEVEL_INFO, format, ##__VA_ARGS__)
#define dlt_gdcn_d(format, ...) LOG(CONTEXT_ID_GDCN, LOG_LEVEL_DEBU, format, ##__VA_ARGS__)
#define dlt_gdcn_v(format, ...) LOG(CONTEXT_ID_GDCN, LOG_LEVEL_VERB, format, ##__VA_ARGS__)
#define LOG(ID, LEVEL, format, ...)                                         \
    do                                                      \
    {                                                       \
        char buffer[PAYLOAD_SIZE];                          \
        gbl_sprintf(buffer, format, ##__VA_ARGS__); \
        logging(ID, LEVEL, (uint8_t *)buffer, strlen(buffer));         \
    } while (0)

void dlt_register(void);
uint8_t dlt_level_set(uint32_t context_id, uint8_t level);
uint8_t dlt_init(void);
uint8_t dlt_loop(void);
bool dlt_console(int argc, char *argv[]);

#endif /*DLT_H*/
