/** \file   gbl_debounce.h
 *  \brief  do debounce for two states
 *
 *  \n      1. must prepare new input and DEBOUNCE_T structure
 *  \n      2. can set different timeout for state 0 to 1 or state 1 to 0
 *
 *  \todo   None
 *
 *  \author 2023.11.12 (Zhan-Yi Wu) create
 */

#ifndef GBL_DEBOUNCE_H
#define GBL_DEBOUNCE_H

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdint.h>

#include "gbl_time.h"

typedef struct {
    uint8_t state;
    uint8_t edge;
    uint16_t counter;
    uint16_t counter_max;
} DEBOUNCE_T;

typedef enum
{
    STABLE = 0,
    DEBOUNCE,
} DEBOUNCE_STATE_E;

typedef void (*DEBOUNCE_ACTION)(bool state);

typedef struct
{
    DEBOUNCE_STATE_E debounce_state;
    bool state;
    gbl_mclocker_t timer;
    gbl_mclocker_t timeout;
    gbl_mclocker_t timeout_0_1;
    gbl_mclocker_t timeout_1_0;
    DEBOUNCE_ACTION action;
} DEBOUNCE_EXTRA_T;

void gbl_debounce(uint8_t new, DEBOUNCE_T *info);

void gbl_debounce_extra(bool new, DEBOUNCE_EXTRA_T *info);

#ifdef __cplusplus
}
#endif

#endif /* GBL_DEBOUNCE_H */
