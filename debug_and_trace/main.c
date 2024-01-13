#include "debug_trace.h"
#include "gbl_console.h"
#include "gbl_string.h"
#include "gbl_stdio.h"

int main(void)
{
    debug_trace_init();
    printf("main init\n");
    while (1)
    {			
        char *l = gbl_console_readline();

        if (l != NULL)
        {
            int argc;
            char *argv[16];
            argc = gbl_strseg(l, " ", argv, sizeof(argv) / sizeof(argv[0]));

            debug_trace_console(argc, argv);
        }
        // debug_trace_loop();
    }
}