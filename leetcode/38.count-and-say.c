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

char * rle(char* input)
{
    uint8_t i = 0;
    uint8_t cnt = 1;

    // for (i = 0; i < strlen(input);i++)
    {
        printf("0:%c\n", input[0]);
        snprintf(input, 10, "%d%c", cnt, input[i]);
        printf("1:%s\n", input);
        printf("2:%d\n", strlen(input));
        
    }
    return input;
}

char *countAndSay(int n)
{
    uint8_t i = 0;
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
            ret = rle(ret);
            printf("5:%s\n", ret);
        }
    }

    return ret;
}
// @lc code=end
