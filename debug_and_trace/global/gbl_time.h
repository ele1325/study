/** \file   gbl_time.h
 *  \brief  function prototypes for the global time
 *
 *  \todo   OK: Windows10, WFC: Linux & MCU
 *
 *  \author 2021.06.18 (XZ Hong) refactor
 *  \author 2020.10.07 (XZ Hong) create
 */

#ifndef GBL_TIME_H
#define GBL_TIME_H

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>

#if (defined(WIN32) || defined(WIN64)) || (defined(linux) || defined(unix))

#include <time.h>

typedef clock_t gbl_mclocker_t; /*!< unit: ms */
typedef clock_t gbl_uclocker_t; /*!< unit: us */

#else /* MCU */

typedef uint32_t gbl_mclocker_t; /*!< unit: ms */
typedef uint32_t gbl_uclocker_t; /*!< unit: us */

#endif

/** \brief  system current time unit is millisecond
 *  \return ms (milliseconds)
 */
gbl_mclocker_t gbl_mclocker(void);

/** \brief  system current time unit is microsecond
 *  \return us (microseconds)
 */
gbl_uclocker_t gbl_uclocker(void);

/** \brief  delay milliseconds
 *
 *  Sleep relinquishes the CPU for specified amount ,
 *  so that other process can execute.
 *  While Delay is just busy waiting for the amount to expire
 *  and then continue once expires,
 *  it do not execute any other process during this period.
 *
 *  \n with OS, this function is sleep
 *  \n non-OS, this function is delay
 */
void gbl_msleep(uint32_t ms);
void gbl_usleep(uint32_t us);

#ifdef __cplusplus
}
#endif

#endif /* GBL_TIME_H */
