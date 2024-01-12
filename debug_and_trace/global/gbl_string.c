/** \file   gbl_string.c
 *  \brief  function prototypes for the global string
 * 
 *  \todo   None
 *
 *  \author 2021.06.22 (XZ Hong) gbl_strseg V0.2
 *  \author 2021.06.19 (XZ Hong) refactor
 *  \author 2020.09.24 (XZ Hong) create
 */

#include "gbl_string.h"

int16_t gbl_strseg(char *string, char *delim, char **segment, int16_t size)
{  
  int16_t i = 0;

  char *token = strtok((char*)string, (char*)delim);

  segment[0] = token;

  while ((token != NULL) && (++i < size))
  {
    token = strtok(NULL, (char*)delim);
    segment[i] = token;
  } 

  return i;
}

