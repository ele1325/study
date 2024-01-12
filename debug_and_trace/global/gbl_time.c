/** \file   gbl_time.c
 *  \brief  function prototypes for the global time
 *
 *  \todo   OK: Windows10, WFC: Linux & MCU
 *
 *  \author 2021.06.18 (XZ Hong) refactor
 *  \author 2020.10.07 (XZ Hong) create
 */

#include "gbl_stdio.h"
#include "gbl_time.h"

#if (defined(WIN32) || defined(WIN64))
#include <windows.h>

gbl_mclocker_t gbl_mclocker(void)
{
    return clock();
}

gbl_uclocker_t gbl_uclocker(void)
{
#if 1
    /* https://learn.microsoft.com/zh-tw/windows/win32/sysinfo/acquiring-high-resolution-time-stamps */

    LARGE_INTEGER CurrentTime;
    LARGE_INTEGER Frequency;

    QueryPerformanceFrequency(&Frequency);
    QueryPerformanceCounter(&CurrentTime);
    CurrentTime.QuadPart *= 1000000;
    CurrentTime.QuadPart /= Frequency.QuadPart;

    return CurrentTime.QuadPart;
#else
    return clock() * 1000;
#endif
}

void gbl_msleep(uint32_t ms)
{
    Sleep(ms);
}

void gbl_usleep(uint32_t us)
{
#if 0
    /* https://www.c-plusplus.net/forum/topic/109539/usleep-unter-windows */

    HANDLE timer;
    LARGE_INTEGER interval;
    interval.QuadPart = -(10 * usec);

    timer = CreateWaitableTimer(NULL, TRUE, NULL);
    SetWaitableTimer(timer, &interval, 0, NULL, NULL, 0);
    WaitForSingleObject(timer, INFINITE);
    CloseHandle(timer);
#else
    gbl_uclocker_t cur = gbl_uclocker();

    while ((gbl_uclocker() - cur) < us)
    {
    }
#endif
}

#elif (defined(linux) || defined(unix))
#include <unistd.h>

gbl_mclocker_t gbl_mclocker(void)
{
    return clock() * 30; //? TBC
}

gbl_uclocker_t gbl_uclocker(void)
{
    return clock() * 30; //? TBC
}

void gbl_msleep(uint32_t ms)
{
    usleep(ms * 1000);
}

void gbl_usleep(uint32_t us)
{
    usleep(us);
}

#else /* MCU */

#include "mcu_timer.h"

gbl_mclocker_t gbl_mclocker(void)
{
    return mcu_mclocker();
}

gbl_uclocker_t gbl_uclocker(void)
{
    return mcu_uclocker();
}

void gbl_msleep(uint32_t ms)
{
    gbl_mclocker_t cur = gbl_mclocker();

    while ((gbl_mclocker() - cur) < ms)
    {
    }
}

void gbl_usleep(uint32_t us)
{
    gbl_uclocker_t cur = gbl_uclocker();

    while ((gbl_uclocker() - cur) < us)
    {
    }
}

#endif
