/** \file   gbl_stdio.h
 *  \brief  function prototypes for the global stdio
 * 
 *  \todo   None
 *
 *  \author 2023.11.12 (Kris Su) include <stdarg.h> and use va_list
 *  \author 2021.06.22 (XZ Hong) create
 */

#ifndef GBL_STDIO_H
#define GBL_STDIO_H

/* The value returned by fgetc and similar functions to indicate the
   end of the file.  */
#define EOF (-1)

/* Write a character to stdout.
   This function is a possible cancellation point and therefore not
   marked with __THROW.  */
extern int putchar(int input_c);

/* Read a character from stdin.
   This function is a possible cancellation point and therefore not
   marked with __THROW.  */
extern int getchar(void);

#ifdef DEBUG_ENABLE
#define printf gbl_printf
#else
#define printf(...)
#endif

// #define printf gbl_printf
int gbl_printf(const char *format, ...);

#define sprintf gbl_sprintf
int gbl_sprintf(char *out, const char *format, ...);

#endif /* GBL_STDIO_H */
