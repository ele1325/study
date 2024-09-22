/*
 * @lc app=leetcode id=55 lang=c
 *
 * [55] Jump Game
 */

// @lc code=start
#include <stdbool.h>

bool canJump(int* nums, int numsSize) {
    int i;
    int L = numsSize - 1;
    for (i = (numsSize - 2); i >= 0 ; i--)
    {
        if(i + nums[i] >= L)
        {
            L = i;
        }
    }

    return L==0;
}
// @lc code=end

