/** \file   gbl_checksum.h
 *  \brief  for checksum calculation & check
 *
 *  \todo   None
 *
 *  \author 2023.11.12 (Jimmy Lee) create
 */

#ifndef GBL_CHECKSUM_H
#define GBL_CHECKSUM_H

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>

uint8_t gbl_checksum_calculate(const uint8_t data[], uint16_t size);
uint8_t gbl_checksum_check(const uint8_t data[], uint16_t size);

#ifdef __cplusplus
}
#endif

#endif /* GBL_CHECKSUM_H */
