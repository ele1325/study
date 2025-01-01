#include <stdio.h>
#include <windows.h>
#include "../../c_code/auo/c_main.h"

int main()
{
    // 加載 DLL
    HMODULE handle = LoadLibrary("../c_code/c_main_api.dll");
    if (!handle)
    {
        printf("Error loading DLL: %ld\n", GetLastError());
        return 1;
    }

    // 查找 c_main 函數並轉換為函數指針aaaa
    int (*aaaa)(void) = (int (*)(void))GetProcAddress(handle, "c_main_api");
    if (!aaaa)
    {
        printf("Error loading function: %ld\n", GetLastError());
        FreeLibrary(handle);
        return 1;
    }

    // 使用 aaaa 函數
    aaaa();
    printf("you should not see this\n");

    // 釋放 DLL
    // FreeLibrary(handle);
    return 0;
}
