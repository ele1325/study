/** \file   gbl_cpu_loading.c
 *  \brief  measure cpu loading
 *
 *  \todo   None
 *
 *  \author 2023.11.12 (Jimmy Lee) create
 */

#include "gbl_cpu_loading.h"

static struct cpu_loading *head = NULL;

void cpu_loading_init(struct cpu_loading *cl, char *str, uint32_t expect_period)
{
    struct cpu_loading *temp = head;
    uint8_t exist_flag = 0;
    while (temp)
    {
        if (temp == cl)
        {
            exist_flag = 1;
            break;
        }
        temp = temp->next;
    }

    if (exist_flag == 0)
    {
        uint8_t cpy_len = strlen(str);
        cpy_len = (cpy_len < (NAME_SIZE - 1)) ? cpy_len : (NAME_SIZE - 1);
        memcpy(cl->module_name, str, cpy_len);
        cl->module_name[cpy_len] = 0U; /*end character*/
        cl->expect_period = expect_period;
        cl->next = head;
        head = cl;
    }
}

void cpu_loading_start(struct cpu_loading *cl, uint32_t time)
{
    if (cl != NULL)
    {
        cl->start_new = time;
    }
}

void cpu_loading_end(struct cpu_loading *cl, uint32_t time)
{
    if (cl != NULL)
    {
        cl->end = time;
        cl->now_active = cl->end - cl->start_new;
        cl->now_period = cl->start_new - cl->start_old;
        cl->max_period = (cl->now_period > cl->max_period) ? cl->now_period : cl->max_period;
        cl->min_active = (cl->now_active < cl->min_active) ? cl->now_active : cl->min_active;
        cl->avg_active = (cl->now_active + cl->avg_active) / 2;
        cl->max_active = (cl->now_active > cl->max_active) ? cl->now_active : cl->max_active;
        cl->start_old = cl->start_new;
    }
}

#ifdef DEBUG_ENABLE
static void cpu_loading_reset(void)
{
#if CPU_LOADING_ENABLE
    struct cpu_loading *temp;
    for (temp = head; temp; temp = temp->next)
    {
        temp->now_active = 0;
        temp->min_active = 0xFFFFFFFF;
        temp->avg_active = 0;
        temp->max_active = 0;

        temp->now_period = 0;
        temp->max_period = 0;
    }
#else
    printf("CPU_LOADING_DISABLE\n");
#endif
}

static void cpu_loading_info(uint8_t print_line)
{
#if CPU_LOADING_ENABLE
    uint8_t current_line = 0;
    uint32_t total_now_active = 0;
    uint32_t total_min_active = 0;
    uint32_t total_avg_active = 0;
    uint32_t total_max_active = 0;
    uint32_t total_max_period = 0;
    struct cpu_loading *temp;
    printf("\n");
    printf("module_name expect_period now_period max_period now_active min_active avg_active max_active\n");
    for (temp = head; temp; temp = temp->next)
    {
        total_now_active += temp->now_active;
        total_min_active += temp->min_active;
        total_avg_active += temp->avg_active;
        total_max_active += temp->max_active;
        total_max_period += temp->max_period;
        if (current_line >= print_line)
        {
            printf("%10s %10d %10d %10d %10d %10d %10d %10d\n",
                   temp->module_name, temp->expect_period, temp->now_period, temp->max_period,
                   temp->now_active, temp->min_active, temp->avg_active, temp->max_active);
        }
        current_line++;
    }
    printf("cpu loading(now):%d%%\n", (total_now_active * 100) / CRITICAL_PERIOD);
    printf("cpu loading(min):%d%%\n", (total_min_active * 100) / CRITICAL_PERIOD);
    printf("cpu loading(avg):%d%%\n", (total_avg_active * 100) / CRITICAL_PERIOD);
    printf("cpu loading(max):%d%%\n", (total_max_active * 100) / CRITICAL_PERIOD);
    printf("total_max_period:%d(us)\n", total_max_period);
#else
    printf("CPU_LOADING_DISABLE\n");
#endif
}

bool cpu_loading_console(int argc, char *argv[])
{
    bool ret = true;
    if ((argc < 2) || (STRNCMP(argv[0], "cpu") != 0))
    {
        ret = false;
    }
    else if (STRNCMP(argv[1], "help") == 0)
    {
        printf("cpu help\n");
    }
    else if (STRNCMP(argv[1], "info") == 0)
    {
        uint8_t val = strtoul(argv[2], NULL, 10);
        cpu_loading_info(val);
    }
    else if (STRNCMP(argv[1], "reset") == 0)
    {
        cpu_loading_reset();
        printf("cpu reset\n");
    }
    else
    {
        ret = false;
    }
    return ret;
}
#endif