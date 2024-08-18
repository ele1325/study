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
    int j = 0, c = 1;
    char *ans = malloc(5000 * sizeof(char));
    char *temp = malloc(5000 * sizeof(char));
    ans[0] = '1';
    ans[1] = '\0';
    for (int i = 1; i < n; i++)
    {
        int k = 0;
        while (ans[j] != '\0')
        {
            if (ans[j] == ans[j + 1])
            {
                c++;
            }
            else
            {
                temp[k] = c + '0';
                temp[k + 1] = ans[j];
                k = k + 2;
                c = 1;
            }
            j++;
        }
        
        temp[k] = '\0';
        strcpy(ans, temp);
        j = 0;
    }
    return (ans);
}
// @lc code=end
