/*
 * @lc app=leetcode id=89 lang=c
 *
 * [89] Gray Code
 */

// @lc code=start
/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int *grayCode(int n, int *returnSize)
{
    int s = pow(2, n);
    int *res = calloc(s, sizeof(int));
    for (int i = 1; i < s; i++)
        res[i] = i ^ (i >> 1);
    *returnSize = s;
    return res;
}
// @lc code=end

