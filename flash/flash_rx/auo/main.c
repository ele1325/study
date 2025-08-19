#include "auo.h"
#include "extra.h"

int main()
{
    print_hello();
    print_extra();
    auo_init();
    while(1)
    {
        auo_loop();
    }
    return 0;
}
