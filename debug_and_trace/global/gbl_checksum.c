/** \file   gbl_checksum.c
 *  \brief  for checksum calculation & check
 *
 *  \todo   None
 *
 *  \author 2023.11.12 (Jimmy Lee) create
 */

#include "gbl_checksum.h"

uint8_t gbl_checksum_calculate(const uint8_t data[], uint16_t size)
{
    uint8_t cs = 0U;

    for (uint16_t idx = 0U; idx < size; idx++)
    {
        cs += data[idx];
    }

    return (uint8_t)(~cs + 1U);
}

uint8_t gbl_checksum_check(const uint8_t data[], uint16_t size)
{
    uint8_t ret = 0U;

    uint8_t cs = 0U;

    for (uint16_t idx = 0U; idx < size; idx++)
    {
        cs += data[idx];
    }

    /* cs is wrong */
    if (cs != 0U)
    {
        ret = 1U;
    }

    return ret;
}
