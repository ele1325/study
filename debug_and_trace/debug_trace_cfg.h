#ifndef DEBUG_TRACE_CFG_H
#define DEBUG_TRACE_CFG_H

#include <stdint.h>
#include <stdbool.h>
//TODO
#define PLAYLOAD_SIZE (8)
#define DEBUG_AND_TRACE_CHANNEL (0x60)

struct api_message_s {
	char message[PLAYLOAD_SIZE];
	uint16_t length;
};
typedef struct api_message_s api_message_t;

// Timer and retry
#define RETRY_TIMES 2
#define TIMEOUT 100

void gdcn_api_init(void);
bool gdcn_api_send(uint8_t channel, uint8_t command_id, uint8_t *playload, uint8_t size);
void gdcn_api_timer_increment(void);

struct uint8_t  gdcn_connect(struct uint8_t  command);
struct uint8_t  gdcn_echo(struct uint8_t  command);

struct uint8_t  device_management(struct uint8_t  command);
struct uint8_t  firmware_flash(struct uint8_t  command);

#endif /*DEBUG_TRACE_CFG_H*/
