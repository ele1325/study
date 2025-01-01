#include "utils.h"
#include "extra.h"
#include <stdio.h>
#include <time.h>
#include "c_main.h"

__attribute__((visibility("default"))) int c_main_api(void)
{
    print_hello();
    print_extra();

    int counter = 0;
    time_t start_time = time(NULL);

    while (1)
    {
        time_t current_time = time(NULL);

        if (current_time - start_time >= 1)
        {
            printf("counter: %d\n", counter++);
            start_time = current_time;
        }
    }

    return 0;
}
