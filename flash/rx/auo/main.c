#include "auo.h"
#include "extra.h"
#include "sim_flash.h"
int main()
{
    print_hello();
    print_extra();
    auo_init();
    sim_flash_test();
    while(1)
    {
        auo_loop();
    }
    return 0;
}
