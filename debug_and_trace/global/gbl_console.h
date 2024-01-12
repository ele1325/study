/** \file   gbl_console.h
 *  \brief  for checksum calculation & check
 *
 *  \todo   None
 * 
 *  \author 2022.10.04 (XZ Hone) % refctor for multi-platform
 *                                 OK  : Windows + Visual Studio + MSYS2
 *                                 WFC : Linux, STM32, TouchGFX  
 *  \author 2020.10.07 (XZ Hone) + support TouchGFX Simulator Windows G++
 *  \author 2020.10.02 (XZ Hone) - getchar, putchar to stm32_stdio
 *                               + __MINGW32__ for Visual Studio Code @ Windows
 *  \author 2019.04.19 (XZ Hone) create
 */

#ifndef GBL_CONSOLE_H
#define GBL_CONSOLE_H

#ifdef __cplusplus
extern "C" {
#endif

// -----------------------------------------------------------------------------
// declaration

#define CONSOLE_HDR     "$ "
#define BUF_ITEM        4
#define BUF_UNIT        64

/* -----------------------------------------------------------------------------
name  char *gbl_console_readline(void)

vers  2021.06.22 V0.1 XZ
      + create
       
desc  LINE      supprot max char is UNIT:128
                if key in line char over UNIT
                the function will abnormal

      HISTORY   History[ITEM]{UNIT]
                ITEM    8
                UNIT    128
                 
      SUPPORT   Windows10   __MINGW32__
                Linux       __unix__ || __unix
                STM32       __GNUC__
      
      USAGE     UP/DWON     history
                LEET/RIGHT  move coursor
                Backspace   
                Delete      
                ctrl+c      Linux Only
                ctrl+z      Linux Only

para  n/a

retu  'NULL     line is empty or not finish
      Others    line pointer

usag  while(1)
      {
          char *l = gbl_console_readline();

          if (l != NULL)
          {
            printf("%s\n", l);

            char b[128];
            char *seg[16];
            int16_t r;

            strncpy(b, l, sizeof(b));
            r = strseg(l, " ", seg, sizeof(seg) / sizeof(seg[0]));
            xxx_console(l, seg, r);
          }
      }

----------------------------------------------------------------------------- */
char *gbl_console_readline(void);

#ifdef __cplusplus
}
#endif

#endif /* GBL_CONSOLE_H */
