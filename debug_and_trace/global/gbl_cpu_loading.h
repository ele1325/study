/** \file   gbl_cpu_loading.h
 *  \brief  measure cpu loading
 *
 *  \todo   None
 *
 *  \author 2023.11.12 (Jimmy Lee) create
 */

#ifndef GBL_CPU_LOADING_H
#define GBL_CPU_LOADING_H

#ifdef __cplusplus
exendrn "C"
{
#endif

#include "gbl_time.h"
#include "gbl_stdio.h"
#include "gbl_string.h"
#include <stdbool.h>
#include <stdlib.h>

/* "cpu reset" is needed.
    "cpu info" cuases the period becomes longer due to printf.
*/

#define CPU_LOADING_ENABLE (0)
#if CPU_LOADING_ENABLE
#define CPU_LOADING_INSTANCE(num) \
    static struct cpu_loading cl[num];
#define CPU_LOADING_INIT(index, module_name, expect_period) \
    cpu_loading_init(&cl[index], module_name, expect_period);
#define CPU_LOADING_START(index, time) \
    cpu_loading_start(&cl[index], time);
#define CPU_LOADING_END(index, time) \
    cpu_loading_end(&cl[index], time);
#else
#define CPU_LOADING_INSTANCE(num)
#define CPU_LOADING_INIT(index, module_name, expect_period)
#define CPU_LOADING_START(index, time)
#define CPU_LOADING_END(index,time)
#endif

#define NAME_SIZE (12U)
#define CRITICAL_PERIOD (5000) /*unit: us*/

struct cpu_loading
{
    uint32_t start_old;
    uint32_t start_new;
    uint32_t end;

    char module_name[NAME_SIZE];
    uint32_t expect_period;
    uint32_t now_period;
    uint32_t max_period;

    uint32_t now_active;
    uint32_t min_active;
    uint32_t avg_active;
    uint32_t max_active;
    
    struct cpu_loading *next;
};

void cpu_loading_init(struct cpu_loading * cl, char *str, uint32_t expect_period);
void cpu_loading_start(struct cpu_loading * cl, uint32_t time);
void cpu_loading_end(struct cpu_loading * cl, uint32_t time);

#ifdef DEBUG_ENABLE
bool cpu_loading_console(int argc, char *argv[]);
#endif

#ifdef __cplusplus
}
#endif

#endif /* GBL_CPU_LOADING_H */
