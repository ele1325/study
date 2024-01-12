/** \file   gbl_debounce.c
 *  \brief  do debounce for two states
 *
 *  \n      1. must prepare new input and DEBOUNCE_T structure
 *  \n      2. can set different timeout for state 0 to 1 or state 1 to 0
 *
 *  \todo   None
 *
 *  \author 2023.11.12 (Zhan-Yi Wu) create
 */

#include <stddef.h>

#include "gbl_debounce.h"
#include "gbl_time.h"

void gbl_debounce(uint8_t new, DEBOUNCE_T *info)
{
    if (new != info->state)
    {
        info->counter++;

        if (info->counter >= info->counter_max)
        {
            info->state = !(info->state);
            info->edge = 1;
            info->counter = 0;
        }
    }
    else
    {
        /* no change, initial the counter to 0 */
        info->counter = 0;
    }
}

void gbl_debounce_extra(bool new, DEBOUNCE_EXTRA_T *info)
{
    switch (info->debounce_state)
    {
    /* because old = new, so stay in STABLE state */
    case STABLE:
        if (info->state != new)
        {
            /* record the current time of transition */
            info->timer = gbl_mclocker();

            /* set timeout according to different state */
            /* old_state == false represnets old state is 0 */
            if (info->state == false)
            {
                info->timeout = info->timeout_0_1;
            }
            else
            {
                info->timeout = info->timeout_1_0;
            }

            /* transition to DEBOUCE */
            info->debounce_state = DEBOUNCE;
        }
        break;

    case DEBOUNCE:
        /* because old = new, transition to STABLE */
        if (info->state == new)
        {
            info->debounce_state = STABLE;
        }
        else
        {
            if ((gbl_mclocker() - info->timer) >= info->timeout)
            {
                /* if duration > timeout, copy new to old */
                info->state = new;

                /* do action at the transition moment according to different state */
                if (info->action != NULL)
                {
                    info->action(info->state);
                }

                /* debounce finished, transition to STABLE */
                info->debounce_state = STABLE;
            }
        }
        break;

    default:
        info->debounce_state = STABLE;
        break;
    }
}
