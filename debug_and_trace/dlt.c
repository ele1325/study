/****************************************************************************
 * Included Files
 ****************************************************************************/

#include <string.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdbool.h>
#include "dlt.h"
#include "gbl_console.h"
#include "gbl_stdio.h"
#include "gbl_string.h"


/****************************************************************************
 * Pre-processor Definitions
 ****************************************************************************/

#define UNUSED(a) ((void)(1 || &(a)))

#define ARRAY_SIZE(x) (sizeof(x) / sizeof(x[0]))
#define BYTE_OFFSET(ptr, offset) (((char *)ptr) + offset)
#define MAX_MODULE_NUM 10

#define DEBUG_VERSION 0
#define EXTENSION_HEADER_SIZE 1024
#define MAX_SCHEMA 16
#define BUFFER_SIZE 1024

/****************************************************************************
 * Private Types
 ****************************************************************************/

struct time_stamp_s {
	uint32_t time;
};

struct header_type { // HTYP2
	char CNIT : 2;
	char WEID : 1;
	char WACID : 1;
	char WSID : 1;
	char VERS : 3;
	char WSFLN : 1;
	char WTGS : 1;
	char WPVL : 1;
	char WSGM : 1;
	int reserve : 20;
};

struct msg_info_s // MSIN
{
	uint8_t reserved : 1;
	uint8_t MSTP : 3;
	uint8_t MSIN : 4;
};

struct condition_header_s {
	struct msg_info_s msg_info; // MSIN
	uint8_t num_of_argsp;
	struct time_stamp_s time;
	uint32_t msg_id; // only in non-verbose mode and data mode
};

struct base_header_s {
	struct header_type type; // HTYP2
	uint8_t message_counter; // MCNT
	uint16_t message_len; // LEN
	struct condition_header_s cond;
};

// extension_header_s must be add when bits are set
// exclude CNTI and VERS
struct extension_header_s {
	uint8_t nbyte;
	char field[EXTENSION_HEADER_SIZE];
};

struct dlt_log_s {
	struct base_header_s base;
	uint8_t playload[DEBUG_PLAYLOAD];
};

struct log_manager_s {
	struct dlt_log_s dlt_log[LOG_BUF_SIZE];
	uint8_t curr_log_idx;
	uint8_t app_id;
	uint8_t context_id;
	uint8_t msg_counter; // only one channnel currently
	bool verbose;
	uint8_t log_level;
};

struct log_level_cmd_s {
	uint8_t app_id;
	uint8_t context_id;
	uint8_t level;
};

/****************************************************************************
 * Private Function Prototypes (declarations)
 ****************************************************************************/

static bool dlt_filter(struct dlt_log_s *dlt_header_ptr, uint8_t filer_log_level);
static bool rx_set_log_level(api_message_t *in, api_message_t *out);
static bool rx_event_dlt(api_message_t *in, api_message_t *out);
static bool rx_get_dlt_log_level(api_message_t *in, api_message_t *out);

/****************************************************************************
 * Private Data (definitions)
 ****************************************************************************/

static struct log_manager_s log_manager[MAX_MODULE_NUM];

/****************************************************************************
 * Publoc Data (definitions)
 ****************************************************************************/

debug_and_trace_channel_t debug_and_trace_handler[] = { { Set_Log_Level, rx_set_log_level },
							{ EVENT_DLT, rx_event_dlt },
							{ GET_DLT_LOG_LEVEL, rx_get_dlt_log_level } };

/****************************************************************************
 * Private Functions (definitions)
 ****************************************************************************/

static struct log_manager_s *search_manager(uint8_t app_id, uint8_t context_id)
{
	for (uint8_t i = 0; i < MAX_MODULE_NUM; ++i) {
		if (log_manager[i].app_id == app_id && log_manager[i].context_id == context_id) {
			return &log_manager[i];
		}
	}
	return NULL;
}

static bool dlt_filter(struct dlt_log_s *dlt_header_ptr, uint8_t filter_log_level)
{
	if (dlt_header_ptr->base.cond.msg_info.MSTP >= filter_log_level) {
		return true;
	}
	return false;
}

static bool rx_set_log_level(api_message_t *in, api_message_t *out)
{
	uint8_t app_id = *(uint8_t *)in->message;
	uint8_t context_id = *(uint8_t *)BYTE_OFFSET(in->message, 1);
	uint8_t new_log_level = *(uint8_t *)BYTE_OFFSET(in->message, 2);

	struct log_manager_s *target = search_manager(app_id, context_id);
	target->log_level = new_log_level;

	out->length = 0;

	return true;
}

static bool rx_event_dlt(api_message_t *in, api_message_t *out)
{
#if 0
	UNUSED(in);

	uint16_t idx;

	for (uint32_t i = log.read_idx; i != log.write_idx; i = (i + 1) % LOG_BUF_SIZE) {
		if (dlt_filter(&log.dlt_log[i])) {
			memcpy(out->message, &log.dlt_log[i], sizeof(log.dlt_log[i]));
			idx += sizeof(log.dlt_log[i]);
		}
	}

	// clear log
	log.read_idx = log.write_idx;

	return true;
#endif
	return false;
}

static bool rx_get_dlt_log_level(api_message_t *in, api_message_t *out)
{
	uint8_t app_id = *(uint8_t *)in->message;
	uint8_t context_id = *(uint8_t *)BYTE_OFFSET(in->message, 1);

	struct log_manager_s *target = search_manager(app_id, context_id);
	out->message[0] = (uint8_t)target->app_id;
	out->message[1] = (uint8_t)target->context_id;
	out->message[2] = (uint8_t)target->log_level;
	out->length = 3;

	return true;
}

/****************************************************************************
 * Public Functions (definitions)
 ****************************************************************************/
void debug_and_trace_init(void)
{
	memset(log_manager, 0, sizeof(log_manager));

	for (uint8_t i = 0; i < MAX_MODULE_NUM; ++i) {
		log_manager[i].log_level = DLT_LOG_DEFAULT_LEVEL;
	}
}

void register_debug_and_trace(uint8_t app_id, uint8_t context_id)
{
	static uint8_t i = 0;
	// assert(i < MAX_MODULE_NUM);

	log_manager[i].app_id = app_id;
	log_manager[i].context_id = context_id;
	i += 1;
}

DEBUG_AND_TRACE_HANDLER search_debug_handler(uint8_t command)
{
	for (uint8_t i = 0; i < ARRAY_SIZE(debug_and_trace_handler); ++i) {
		if (debug_and_trace_handler[i].command == command) {
			return debug_and_trace_handler[i].handler;
		}
	}
	// assert(0);
	return NULL;
}

bool sys_log(uint8_t log_level, uint8_t app_id, uint8_t context_id, const char *input_buf, const uint16_t len)
{
	char *buf, *content_start;
	struct base_header_s *base_header_ptr;
	struct extension_header_s *extension_header_ptr;

	struct log_manager_s *target = search_manager(app_id, context_id);
	if (target == NULL) {
		return false;
	}

	buf = (char *)&target->dlt_log[0].base;

	// fill base header
	base_header_ptr = (struct base_header_s *)buf;
	base_header_ptr->message_counter = target->msg_counter;
	target->msg_counter += 1;
	base_header_ptr->type.WACID = 1;
	if (target->verbose == 1) {
		base_header_ptr->type.CNIT = 1;
	} else {
		base_header_ptr->type.CNIT = 0;
	}
	base_header_ptr->cond.msg_info.MSTP = log_level;

	// fill with extension header
	extension_header_ptr = (struct extension_header_s *)BYTE_OFFSET(buf, sizeof(struct base_header_s));
	extension_header_ptr->nbyte = 2;
	extension_header_ptr->field[0] = app_id;
	extension_header_ptr->field[1] = context_id;

	content_start = BYTE_OFFSET(buf, sizeof(struct base_header_s) + extension_header_ptr->nbyte);
	memcpy(content_start, input_buf, len);

	// post process
	base_header_ptr->message_len = sizeof(struct extension_header_s) + extension_header_ptr->nbyte + len;
	// target->curr_log_idx = (target->curr_log_idx + 1) % LOG_BUF_SIZE;

	if (log_level >= target->log_level) {
		return gdcn_api_send(DEBUG_AND_TRACE_CHANNEL, EVENT_DLT, extension_header_ptr->field,
				     extension_header_ptr->nbyte + len);
	}

	return true;
// Use buffer
#if 0
	for (uint8_t i = 0; i < MAX_MODULE_NUM; ++i) {
		if (app_id == log_manager[i].app_id && context_id == log_manager[i].context_id) {
			uint8_t curr_log_idx = log_manager->curr_log_idx;
			buf = (char *)&log_manager[i].dlt_log[curr_log_idx].base;

			// fill base header
			base_header_ptr = (struct base_header_s *)buf;
			base_header_ptr->message_counter = log_manager[i].msg_counter;
			base_header_ptr->type.WACID = 1;
			if (log_manager[i].verbose == 1) {
				base_header_ptr->type.CNIT = 1;
			} else {
				base_header_ptr->type.CNIT = 0;
			}
			base_header_ptr->cond.msg_info = log_level;

			// fill with extension header
			extension_header_ptr =
				(struct extension_header_s *)BYTE_OFFSET(buf, sizeof(struct base_header_s));
			extension_header_ptr->nbyte = 2;
			extension_header_ptr->field[0] = app_id;
			extension_header_ptr->field[1] = context_id;

			// format string
			va_list ap;

			content_start = BYTE_OFFSET(buf, sizeof(struct base_header_s) + extension_header_ptr->nbyte);

			// FIXME: Replace with callback function
			va_start(ap, fmt);
			vsprintf(content_start, fmt, ap);
			va_end(ap);

			// post process
			base_header_ptr->message_len =
				sizeof(struct extension_header_s) + extension_header_ptr->nbyte + strlen(content_start);
			log_manager[i].curr_log_idx = (log_manager[i].curr_log_idx + 1) % LOG_BUF_SIZE;

			return true;
		}
	}
	return false;
#endif
}

bool tx_set_log_level(uint32_t app_id, uint32_t context_id, uint8_t new_log_level)
{
	uint8_t playload[BUFFER_SIZE];
	struct base_header_s *base_header_ptr = (struct base_header_s *)playload;
	struct extension_header_s *extension_header_ptr =
		(struct extension_header_s *)BYTE_OFFSET(base_header_ptr, sizeof(struct base_header_s));
	base_header_ptr->type.CNIT = 2;
	base_header_ptr->type.WACID = 1;

	extension_header_ptr->nbyte = 3;
	extension_header_ptr->field[0] = app_id;
	extension_header_ptr->field[1] = context_id;
	extension_header_ptr->field[2] = new_log_level;

	base_header_ptr->message_len = extension_header_ptr->nbyte;

	return gdcn_api_send(DEBUG_AND_TRACE_CHANNEL, Set_Log_Level, extension_header_ptr->field,
			     extension_header_ptr->nbyte);
#if 0
	uint16_t idx = 0;
	memset(playload, 0, BUFFER_SIZE * sizeof(uint8_t));

	memcpy(playload, &app_id, sizeof(app_id));
	idx += sizeof(app_id);

	memcpy(playload, &context_id, sizeof(context_id));
	idx += sizeof(context_id);

	playload[idx] = new_log_level;
	idx += 1;

	return gdcn_api_send(DEBUG_AND_TRACE_CHANNEL, Set_Log_Level, playload, idx);
#endif
}

bool tx_event_dlt(uint32_t time_stamp, uint8_t log_level, uint8_t *msg, uint16_t size)
{
#if 0
	struct base_header_s *header;
	struct log_level_cmd_s *cmd;

	uint8_t playload[BUFFER_SIZE];
	memset(playload, 0, BUFFER_SIZE * sizeof(uint8_t));
	uint16_t idx = 0;

	header = (struct base_header_s *)&playload[idx];
	header->type.CNIT = Control_Message;
	header->num_of_argsp = 1; // only sent one command
	header->message_counter = msg_counter++;
	memcpy(&header->time, &time_stamp, sizeof(time_stamp)); // FIXME: spec size diff
	idx += sizeof(struct base_header_s);

	cmd = (struct log_level_cmd_s *)&playload[idx];
	cmd->level = log_level;
	idx += sizeof(struct log_level_cmd_s);

	if (verbose) {
		memcpy(&playload[idx], msg, size);
		idx += size;
	}

	return gdcn_api_send(DEBUG_AND_TRACE_CHANNEL, EVENT_DLT, playload, idx);
#endif
	return false;
}

bool rx_send_event_dlt(void)
{
	return false;
#if 0
	uint8_t buf[4096];
	uint16_t offset=0;

	for(uint8_t i = 0; i < MAX_MODULE_NUM; ++i){
		for(uint8_t j = 0; j < LOG_BUF_SIZE; ++j){
			if(dlt_filter(log_manager[i].dlt_log[j], log_manager[i].log_level)){
				memcpy(buf,buf + offset, sizeof(LOG_BUF_SIZE));
				offset += LOG_BUF_SIZE;
			}
		}
	}

	return gdcn_api_send(DEBUG_AND_TRACE_CHANNEL, EVENT_DLT, buf, offset);
#endif
}

bool tx_get_dlt_log_level(uint8_t app_id, uint8_t context_id)
{
	uint8_t playload[BUFFER_SIZE];

	struct log_manager_s *target = search_manager(app_id, context_id);

	if (target == NULL) {
		return false;
	}

	struct base_header_s *base_header_ptr = (struct base_header_s *)playload;
	struct extension_header_s *extension_header_ptr =
		(struct extension_header_s *)BYTE_OFFSET(base_header_ptr, sizeof(struct base_header_s));
	base_header_ptr->type.CNIT = 2;
	base_header_ptr->type.WACID = 1;

	extension_header_ptr->nbyte = 2;
	extension_header_ptr->field[0] = app_id;
	extension_header_ptr->field[1] = context_id;

	base_header_ptr->message_len = extension_header_ptr->nbyte;
	return gdcn_api_send(DEBUG_AND_TRACE_CHANNEL, GET_DLT_LOG_LEVEL, extension_header_ptr->field,
			     extension_header_ptr->nbyte);
}

bool tx_set_enable_event_trace(void)
{
	return false;
}

bool tx_set_disable_event_trace(void)
{
	return true;
}

bool tx_get_event_trace(void)
{
	return false;
}

bool gdcn_api_send(uint8_t channel, uint8_t command_id, uint8_t *playload, uint8_t size)
{
    printf("channel:%d, command_id:%d, buf:%s, size:%d\n", channel, command_id, playload, size);
    return true;
}

uint8_t dlt_init(void)
{
    debug_and_trace_init();
    printf("dlt_init\n");
    register_debug_and_trace(1, 2);
    uint8_t buf[] = "12345";
    printf("size :%d\n", sizeof(buf));
    LOG_INFO(1, 2, buf, sizeof(buf));
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
        printf("dlt r [page] [addr]\n");
        printf("dlt w [page] [addr] [val]\n");
        printf("dlt link\n");
        printf("dlt rssi\n");
    }
    // else if (!STRNCMP(argv[1], "r") && (argc == 4))
    // {
    //     uint8_t page = strtol(argv[2], NULL, 16);
    //     uint16_t addr = strtol(argv[3], NULL, 16);
    //     uint32_t abs_addr = APIX3_BASEADDR | (page << 9) | (addr);
    //     uint8_t ret = reg_rd(page, addr, false);
    //     printf("reg_rd page 0x%02X, addr 0x%04X, abs_addr 0x%08X, value: 0x%02X\n", page, addr, abs_addr, ret);
    // }
    // else if (!STRNCMP(argv[1], "w") && (argc == 5))
    // {
    //     uint8_t page = strtol(argv[2], NULL, 16);
    //     uint16_t addr = strtol(argv[3], NULL, 16);
    //     uint8_t val = strtol(argv[4], NULL, 16);
    //     uint32_t abs_addr = APIX3_BASEADDR | (page << 9) | (addr);
    //     reg_wr(page, addr, val);
    //     printf("reg_wr page 0x%02X, addr 0x%04X, abs_addr 0x%08X, value: 0x%02X\n", page, addr, abs_addr, val);
    // }
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

