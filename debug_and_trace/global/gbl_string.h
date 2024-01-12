/** \file   gbl_string.h
 *  \brief  function prototypes for the global string
 *
 *  \todo   None
 * 
 *  \author 2021.06.22 (XZ Hong) gbl_strseg V0.2
 *  \author 2021.06.19 (XZ Hong) refactor
 *  \author 2020.09.24 (XZ Hong) create
 */

#ifndef GBL_STRING_H
#define GBL_STRING_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <string.h>

// -----------------------------------------------------------------------------
//
#define STRNCMP(x, y) strncmp(x, y, strlen(y))
#define STRNCPY(x, y) strncmp(x, y, sizeof(x))

/* -----------------------------------------------------------------------------
name   int16_t gbl_strseg(uint8_t *string, uint8_t *delim, 
                          uint8_t **segment, int16_t size)

vers   2021.06.22 V0.2 XZ
       % parameter chagne from char to uint8_t
       2020.09.24 V0.1 XZ    
       + create

para   *string
       *delim      
       **segment
       size

retu   number of segments which separate by delim
       range is  1 ~ size

usag   uint8_t *seg[32];
       uint8_t *str = "hello world";
       int16_t r    = strseg(str, " ", seg, sizeof(seg)/sizeof(char*));

note   string data will be modified after function execute
       string data will replace by '\0' when data = delim

exam1  string = "hello word"
       delim  = "X"
       return = 1
       seg[0] = "hello word"

exam2  string = "hello word"
       delim  = " "
       return = 2
       seg[0] = "hello"
       seg[1] = "word"

exam3  string = "hello word"
       delim  = "er"
       return = 3
       seg[0] = "h"
       seg[1] = "llo wo"
       seg[2] = "d"

----------------------------------------------------------------------------- */

int16_t gbl_strseg(char *string, char *delim, char **segment, int16_t size);

#ifdef __cplusplus
}
#endif

#endif /* GBL_STRING_H */
