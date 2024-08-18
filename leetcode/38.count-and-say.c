/*
 * @lc app=leetcode id=38 lang=c
 *
 * [38] Count and Say
 */

// @lc code=start
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *countAndSay(int n)
{
    uint8_t i = 0;
    uint8_t j = 0;
    uint8_t cnt = 0;
    char *base = "1";
    char *ret;
    ret = malloc(10);

    for (i = 1; i <= n; i++)
    {
        if (i == 1)
        {
            memcpy(ret, base, strlen(base) + 1);
        }
        else
        {
            uint8_t len = strlen(ret);
            for (j = 0; j < len; j++)
            {
                if(len == 1)
                {
                    cnt = 1;
                }
                else
                {
                    
                }
                printf("i:%d  j:%d\n", i, j);
                printf("1:%s\n", ret);
                printf("2:%d\n", strlen(ret));
                snprintf(ret, 10, "%d%c", cnt, ret[j]);
                printf("3:%s\n", ret);
                printf("4:%d\n", strlen(ret));
                printf("5:%s\n", ret);
            }
        }
    }

    return ret;
}
// @lc code=end
