/** \file   gbl_console.c
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

#include <stdint.h>
#include <string.h>

#include "gbl_stdio.h"
#include "gbl_console.h"

static char *console_process(char c);

// -----------------------------------------------------------------------------
//

#if defined(TOUCHGFX) // TouchGFX Simulator Windows G++

#include <windows.h>

#define KEY_UP  'A'
#define KEY_DN  'B'
#define KEY_RT  'C'
#define KEY_LT  'D'

static void m_putchar(char c)
{
    fputc(c, stdio);
    return;
}

static int m_getchar()
{
    return fgetc(stdio);
}


#define m_printf printf


char *gbl_console_readline(void)
{
  static uint8_t init = 1;

  if (init)
  {
    #define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004

    memset(&m_console, 0x00, sizeof(m_console));

    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    SetConsoleMode(hOut, dwMode);

    printf(CONSOLE_HDR);

    init = 0;
  }

  int   c = EOF;
  char *l = NULL;

  if (_kbhit())
  {
    c = _getch();

    if (c == EOF) 
    {
      return l;
    }

    l = console_process((char)c);

    if ((l != NULL) && (strlen(l) != 0))
    {
      printf(CONSOLE_HDR);
    }
  }

  return l;

}

#elif defined(__MINGW32__) || defined(__MINGW64__) // Visual Studio + MSYS2

#include <conio.h>

#define KEY_UP  0x48
#define KEY_DN  0x50
#define KEY_RT  0x4D
#define KEY_LT  0x4B


static void m_putchar(char c)
{
    putchar(c);
    return;
}

static int m_getchar()
{
    // fflush(stdin);
    return getchar();
}

#define m_printf printf


char *gbl_console_readline(void)
{
    int c = EOF;
    char *l = NULL;

    if (_kbhit())
    {
        c = _getch();

        if (c == EOF)
        {
            return l;
        }

        l = console_process((char)c);

        if ((l != NULL) && (strlen(l) != 0))
        {
            printf(CONSOLE_HDR);
        }
    }

    return l;
}

#elif defined(linux) || defined(unix) || defined(__unix__) || defined(__unix)

#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <termios.h>

#define KEY_UP  'A'
#define KEY_DN  'B'
#define KEY_RT  'C'
#define KEY_LT  'D'


typedef enum
{
    terminal_mode_off,
    terminal_mode_on,
    terminal_mode_max

} terminal_mode_e;

static terminal_mode_e terminal_mode = terminal_mode_off;

static void terminal_recover()
{
    if (terminal_mode == terminal_mode_on)
    {
        fflush(stdout);

        struct termios x;
        tcgetattr(0, &x);
        x.c_lflag |= (ICANON | ECHO | ISIG);

        x.c_cc[VMIN] = 1;
        x.c_cc[VTIME] = 0;

        tcsetattr(0, TCSANOW, &x);

        terminal_mode = terminal_mode_off;
    }
}

static void terminal_setup()
{
    if (terminal_mode == terminal_mode_off)
    {
        fflush(stdout);

        struct termios x;
        tcgetattr(0, &x);

        x.c_lflag &= ~(ICANON | ECHO | ISIG);

        x.c_cc[VMIN] = 0;
        x.c_cc[VTIME] = 0;

        tcsetattr(0, TCSANOW, &x);

        terminal_mode = terminal_mode_on;
    }
}

static void m_putchar(char c)
{
    putchar(c);
}

static int m_getchar()
{
    return getchar();
}

#define m_printf printf


char *gbl_console_readline(void)
{
    // ---------------------------------------------------------------------------
    //

    static uint8_t init = 1;

    if (init)
    {
        memset(&m_console, 0x00, sizeof(m_console));

        printf(CONSOLE_HDR);

        // register cleanup handler
        atexit(terminal_recover);

        init = 0;
    }

    if (getpgrp() != tcgetpgrp(STDOUT_FILENO))
    {
        return NULL;
    }

    terminal_setup();

    // ---------------------------------------------------------------------------
    //

    uint8_t c = EOF;
    char *l = NULL;

    c = m_getchar();

    if ((c == (uint8_t)EOF) || (c == 0x00))
    {
        return l;
    }

    l = console_process((char)c);

    // if ((l != NULL) && (strlen(l) != 0))
    // {
    //   printf(CONSOLE_HDR);
    // }

    return l;
}

#elif defined(__XC32)
// MPLAB XC32 C/C++ Compiler User's Guide
// https://ww1.microchip.com/downloads/en/DeviceDoc/50001686J.pdf
// __XC32 : Always defined to indicate this the XC32 compiler.

#pragma GCC diagnostic ignored "-Wformat-zero-length"

#define KEY_UP  'A'
#define KEY_DN  'B'
#define KEY_RT  'C'
#define KEY_LT  'D'


static void m_putchar(char c)
{
    putchar(c);
}

static int m_getchar(void)
{
    return getchar();
}

#define m_printf(fm, ...)          \
    do                             \
    {                              \
        printf(fm, ##__VA_ARGS__); \
    } while (0);


char *gbl_console_readline(void)
{
  uint8_t c = EOF;
  char *l = NULL;

  c = m_getchar();

  if (c == (uint8_t)EOF)
  {
    return l;
  }

  l = console_process((char)c);


   if ((l != NULL) || (strlen(l) == 0))
   {
     m_printf(CONSOLE_HDR);
   }

  return l;
}

#elif defined(__GNUC__)   //STM32

#pragma GCC diagnostic ignored "-Wformat-zero-length"

#define KEY_UP  'A'
#define KEY_DN  'B'
#define KEY_RT  'C'
#define KEY_LT  'D'

static void m_putchar(char c)
{
    extern int putchar(int ch);
    putchar(c);
}

static int m_getchar()
{
    extern int getchar(void);
    return getchar();
}

#define m_printf(fm, ...)          \
    do                             \
    {                              \
        printf(fm, ##__VA_ARGS__); \
    } while (0);

char *gbl_console_readline(void)
{
    int c = EOF;
    char *l = NULL;

    c = m_getchar();
    
    if ((c == EOF) || (c == 0x00))
    {
        return l;
    }

    l = console_process((char)c);

    return l;
}

#endif


/* -----------------------------------------------------------------------------
 * Structure
 *--------------------------------------------------------------------------- */
typedef struct
{
    char st;
    uint16_t length;
    uint16_t cursor;

    char line[BUF_UNIT];

    struct
    {
        char item[BUF_ITEM][BUF_UNIT];
        unsigned char curr;
        unsigned char seek;
    } log;

} m_console_t;

/* -----------------------------------------------------------------------------
 * Variable
 *--------------------------------------------------------------------------- */
static m_console_t m_console;


static char *console_process(char c)
{
    /* -----------------------------------------------------------
     *  \033[<L>;<C>H     Puts the cursor at line L and length C.
     *  \033[<L>;<C>f     Puts the cursor at line L and length C.
     *  \033[<N>A         Move the cursor up N lines:
     *  \033[<N>B         Move the cursor down N lines:
     *  \033[<N>C         Move the cursor forward N lengths:
     *  \033[<N>D         Move the cursor backward N lengths:
     *  \033[2J           Clear the screen, move to (0,0):
     *  \033[K            Erase to end of line:
     *  \033[s            Save cursor position:
     *  \033[u            Restore cursor position:
     * ----------------------------------------------------------*/

    // printf("c: 0x%02X\n", c);

    switch (m_console.st)
    {
    case 0:
        if (c == (char)EOF)
        {
            // do nothing!
        }

        /* -----------------------------------------------------------
         * linux = esc + [ + arrow
         * UP ^[[A
         * DN ^[[B
         * RT ^[[C
         * LT ^[[D
        * ----------------------------------------------------------*/
        else if (c == 0x1B) // arrow keys, if the first value is esc
        {                   
            m_console.st = 1;
        }
        /* -----------------------------------------------------------
         * Windows = 0x00 + arrow
        * ----------------------------------------------------------*/
#ifdef __MINGW32__
        else if (c == 0x00 || c == (char)0xE0) // arrow keys
        {
            m_console.st = 2;
        }
#endif

#ifdef TOUCHGFX // TouchGFX Simulator Windows G++
        else if (c == (char)0xE0)
        {
            m_console.st = 2;
        }
#endif

#if (defined(__unix__) || defined(__unix))

        else if (c == 0x03) // ctrl+c
        {
            printf("\n");
            raise(SIGINT);
        }
        else if (c == 0x1A) // ctrl+z
        {
            printf("ctrl+z again to stop process\n");
            terminal_recover();
            raise(SIGTSTP);
        }
#endif

        else if ((c == 0x7F) || (c == 0x08)) // delete & backspace
        {
            if (m_console.length > 0)
            {
                memcpy(&m_console.line[m_console.cursor - 1],
                       &m_console.line[m_console.cursor],
                       (m_console.length - m_console.cursor) + 1);
                m_console.line[m_console.length] = 0x00;
                m_printf("\033[s\033[1D\033[K%s\033[u\033[1D",
                         &m_console.line[m_console.cursor - 1]);

                m_console.length--;
                m_console.cursor--;
            }
        }
        else if ((c == '\n') || (c == '\r'))
        {
            m_printf("\r\n");

            if (strlen(m_console.line) != 0)
            {
                m_console.line[m_console.length] = 0x00;
                m_console.length = 0;
                m_console.cursor = 0;
                m_console.log.seek = 0;
                strcpy(m_console.log.item[m_console.log.curr], m_console.line);
                m_console.log.curr = (m_console.log.curr + 1) % BUF_ITEM;
                return m_console.line;
            }
            else
            {
                return NULL;
            }
        }
        else // gerneral key
        {
            if ((m_console.length + 1) >= BUF_UNIT)
            {
                break;
            }

            if (m_console.cursor >= m_console.length)
            {
                m_putchar(c);

                m_console.cursor++;
                m_console.line[m_console.length++] = c;
            }
            else
            {
                memmove(&m_console.line[m_console.cursor + 1],
                        &m_console.line[m_console.cursor],
                        (m_console.length - m_console.cursor) + 1);
                m_console.line[m_console.cursor] = c;
                m_console.line[m_console.length + 1] = 0x00;
                m_printf("\033[s\033[K%s\033[u\033[1C",
                         &m_console.line[m_console.cursor]);

                m_console.cursor++;
                m_console.length++;
            }
        }
        break;

    case 1:
        // skip the [
        m_console.st = 2;
        break;

    case 2:
        switch (c) // the real value
        {
        case KEY_UP: // up
        case KEY_DN: // down
        {
            char op = (c == KEY_UP) ? -1 : 1;

            unsigned char curr, next;

            curr = (m_console.log.curr + (m_console.log.seek + 0) + BUF_ITEM) % BUF_ITEM;
            next = (m_console.log.curr + (m_console.log.seek + op) + BUF_ITEM) % BUF_ITEM;

            if (strlen(m_console.log.item[next]) != 0)
            {
                m_console.log.seek = (m_console.log.seek + BUF_ITEM + op) % BUF_ITEM;
                strcpy(m_console.line, m_console.log.item[next]);
            }
            else
            {
                strcpy(m_console.line, m_console.log.item[curr]);
            }
            m_console.cursor = m_console.length = strlen(m_console.line);

            m_printf("\033[128D\033[K%s%s", CONSOLE_HDR, m_console.line);

            break;
        }
        case KEY_RT: // right
            if (m_console.cursor <= m_console.length)
            {
                m_console.cursor++;
                m_printf("\033[1C");
            }
            break;
        case KEY_LT: // left
        {
            if (m_console.cursor > 0)
            {
                m_console.cursor--;
                m_printf("\033[1D");
            }
            break;
        }
        default:
            break;
        }

        m_console.st = 0;
        break;

    default:
        break;
    }

    return NULL;
}
