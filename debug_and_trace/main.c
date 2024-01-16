#include "dlt.h"
#include "gbl_console.h"
#include "gbl_string.h"
#include "gbl_stdio.h"

int main(void)
{
    dlt_init();
    printf("main init\n");
    while (1)
    {			
        char *l = gbl_console_readline();

        if (l != NULL)
        {
            int argc;
            char *argv[16];
            argc = gbl_strseg(l, " ", argv, sizeof(argv) / sizeof(argv[0]));

            dlt_console(argc, argv);
        }
        dlt_loop();
    }
}