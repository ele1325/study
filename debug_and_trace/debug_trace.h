#ifndef DEBUG_TRACE_H
#define DEBUG_TRACE_H

#include "debug_trace_cfg.h"
#include <stdint.h>
#include <stdbool.h>

#define LOG_BUF_SIZE 256
#define DEBUG_PLAYLOAD 1024

// GDCN command id
#define EVENT_DLT 0x20
#define Set_Log_Level 0x00
#define GET_DLT_LOG_LEVEL 0x02

// header type define
#define CNTI_MASK (0x3)
#define WEDI_MASK (0x1 << 2)
#define WACID_MASK (0x1 << 3)
#define WSID_MASK (0x1 << 4)
#define VERS_MASK (0x7 << 5)
#define WSFLN_MASK (0x1 << 8)
#define WTGS_MASK (0x1 << 9)
#define WPVL_MASK (0x1 << 10)
#define WSGM_MASK (0x1 << 11)

// CNTI part
#define Verbose_Mode_Data_Message 0x0
#define Non_Verbose_Mode_Data_Message 0x1
#define Control_Message 0x2
// #define reserved; 0x3

// messgae info define
#define MSTP_SHITF 1
#define MTIN_SHIFT 4
#define MSTP_MASK (0x7 << MSTP_SHITF)
#define MTIN_MASK (0xF << MTIN_SHIFT)

// MSTP bit set
#define DLT_TYPE_LOG (0x0 << MSTP_SHITF).
#define DLT_TYPE_APP_TRACE (0x1 << MSTP_SHITF)
#define DLT_TYPE_NW_TRACE (0x2 << MSTP_SHITF)
#define DLT_TYPE_CONTROL (0x3 << MSTP_SHITF)

// log level, MSTP is set as 0x0
#define DLT_LOG_FATAL 0x01
#define DLT_LOG_ERROR 0x02
#define DLT_LOG_WARNING 0x03
#define DLT_LOG_INFO 0x04
#define DLT_LOG_DEBUG 0x05
#define DLT_LOG_VERBOSE 0x06
#define DLT_LOG_DEFAULT_LEVEL DLT_LOG_INFO

// trace message
#define DLT_TRACE_VARIABLE 0x1
#define DLT_TRACE_FUNCTION_IN 0x2
#define DLT_TRACE_FUNCTION_OUT 0x3
#define DLT_TRACE_STATE 0x4
#define DLT_TRACE_VFB 0x5

// MSTP setting field
#define DLT_NW_TRACE_IPC 0x1
#define DLT_NW_TRACE_CAN 0x2
#define DLT_NW_TRACE_FLEXRAY 0x3
#define DLT_NW_TRACE_MOST 0x4
#define DLT_NW_TRACE_ETHERNET 0x5
#define DLT_NW_TRACE_SOMEIP 0x6
// #deinfe User_Defined 0x7-0xF

#define DLT_CONTROL_REQUEST 0x1
#define DLT_CONTROL_RESPONSE 0x2
// #define 0x3-0xF: Reserved

// log level, MSTP is set as 0x0
#define LOG_FATAL(APP_ID, CONTEXT_ID, buffer, len) sys_log(DLT_LOG_FATAL, APP_ID, CONTEXT_ID, buffer, len)
#define LOG_ERROR(APP_ID, CONTEXT_ID, buffer, len) sys_log(DLT_LOG_ERROR, APP_ID, CONTEXT_ID, buffer, len)
#define LOG_WARNING(APP_ID, CONTEXT_ID, buffer, len) sys_log(DLT_LOG_WARNING, APP_ID, CONTEXT_ID, buffer, len)
#define LOG_INFO(APP_ID, CONTEXT_ID, buffer, len) sys_log(DLT_LOG_INFO, APP_ID, CONTEXT_ID, buffer, len)
#define LOG_DEBUG(APP_ID, CONTEXT_ID, buffer, len) sys_log(DLT_LOG_DEBUG, APP_ID, CONTEXT_ID, buffer, len)
#define LOG_VERBOSE(APP_ID, CONTEXT_ID, buffer, len) sys_log(DLT_LOG_VERBOSE, APP_ID, CONTEXT_ID, buffer, len)

#define DLT_LOG_FATAL 0x01
#define DLT_LOG_ERROR 0x02
#define DLT_LOG_WARNING 0x03
#define DLT_LOG_INFO 0x04
#define DLT_LOG_DEBUG 0x05
#define DLT_LOG_VERBOSE 0x06

typedef bool (*DEBUG_AND_TRACE_HANDLER)(api_message_t *, api_message_t *);

struct debug_and_trace_channel_s {
	uint8_t command;
	DEBUG_AND_TRACE_HANDLER handler;
};
typedef struct debug_and_trace_channel_s debug_and_trace_channel_t;

// open api
void register_debug_and_trace(uint8_t app_id, uint8_t context_id);
void debug_and_trace_init(void);
bool sys_log(uint8_t log_level, uint8_t app_id, uint8_t context_id, const char *input_buf, const uint16_t len);
bool tx_set_log_level(uint32_t app_id, uint32_t context_id, uint8_t new_log_level);
bool tx_event_dlt(uint32_t time_stamp, uint8_t log_level, uint8_t *msg, uint16_t size);
bool tx_get_dlt_log_level(uint8_t app_id, uint8_t context_id);
bool tx_set_enable_event_trace(void);
bool tx_set_disable_event_trace(void);
bool tx_get_event_trace(void);
bool rx_send_event_dlt(void);
DEBUG_AND_TRACE_HANDLER search_debug_handler(uint8_t command);
uint8_t debug_trace_init(void);
uint8_t debug_trace_loop(void);
bool debug_trace_console(int argc, char *argv[]);

#endif /*DEBUG_TRACE_H*/
