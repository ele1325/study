/** \file   gbl_rb.h
 *  \brief  ring-buffer module
 *
 *  \todo   None
 * 
 *  \author 2021.06.22 (XZ Hong) create
 */

/*   1. easy way to determine ring buffer empty & full
 *      a. empty       R=W
 *      b. full        R=(W+1)%SIZE
 *      c. read/wirte  increase index
 *
 *   2. max bytes can be wirte in is "SIZE-1"
 *
 *   3. example @ size = 4
 *
 *      stage0
 *        addr     0  1  2  3
 *        index   R W            empty : R=W
 *
 *      stage1:    write 1st byte
 *        addr     0  1  2  3
 *        index    R  W          next write addr is 1
 *        data     D             data at addr 0
 *
 *      stage2     write 2nd byte
 *        addr     0  1  2  3
 *        index    R     W       next write addr is 2
 *        data     D  D          data at addr 0~1
 *
 *      stage3     write 3rd byte
 *        addr     0  1  2  3
 *        index    R        W    next write addr is 3
 *        data     D  D  D       data at addr 0~2
 *
 *      stage4     write 4th byte, CAN NOT write, because full "R=(W+1)%SIZE"
 *        addr     0  1  2  3
 *        index    R        W    full  : R=(W+1)%SIZE
 *        data     D  D  D       rb size is 4, but only 3 bytes can be write in
 *
 *      stage5     read 1st
 *        addr     0  1  2  3
 *        index       R     W
 *        data        D  D
 *
 *      stage6     read 2nd
 *        addr     0  1  2  3
 *        index          R  W
 *        data           D
 *
 *     stage7     read 3rd
 *        addr    0  1  2  3
 *        index           R W
 *        data
 *
 *      stage8     write again
 *        addr     0  1  2  3
 *        index    W        R
 *        data              D
 *
 *      stage8     write serval times, same as stage 4, only 3 bytes can be write
 *        addr     0  1  2  3
 *        index          W  R
 *        data     D  D     D
 *
 *   4. W+1==R     data is full
 *      R==W       data is empty
 */

#ifndef GBL_RB_H
#define GBL_RB_H

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>
#include <stdbool.h>

#include "error_no.h"

typedef struct gbl_rb
{
    uint8_t *buff; // buff addr

    uint16_t size; // buff size = row * col
                    // buff size = unit amount * unit size

    uint16_t row; // row = unit amount
                    // ring buffer unit amount
                    // used for ring buffer index maintainers

    uint16_t col; // col = unit size
                    // bytes per unit
                    // equal to ring buffer unit size

    uint16_t r; // read  index
    uint16_t w; // write index

} gbl_rb_t;

/*
* func     gbl_rb_init
*
* brief    initial ring buffer with buff addr, unit amount and size
*
* param    rb      gbl_rb_t pointer
*          buff    buffer address
*          size    buffer size = row * col
*                              = unit amount * unit_size
*
*          row     row = unit amount
*          col     col = unit size
*
* return   >= 0    ring buffer size
*          <  0    error
*                  -EINVAL  buff     == NULL
*                           size     != row * col
*                           row *col >= 65536
*
* limit    1. ring buffer max size is 64KB
*          2. ring buffer effective size
*
* version  v0.1 2021.12.07 (xz)
*          refactor from MACRO to function
*/
uint16_t gbl_rb_init(gbl_rb_t *rb, void *buff, uint16_t size, uint16_t row, uint16_t col);

/*
* func     gbl_rb_is_empty
*
* brief    check if ring buffer is empty
*
* param    rb      gbl_rb_t pointer
*
* return   true    IS  empty
*          false   NOT empty
*
* version  v0.1 2021.12.07 (xz)
*          refactor from MACRO to function
*/
bool gbl_rb_is_empty(gbl_rb_t *rb);

/*
* func     gbl_rb_is_full
*
* brief    check if ring buffer is full
*
* param    rb      gbl_rb_t pointer
*
* return   true    IS  full
*          false   NOT full
*
* version  v0.1 2021.12.07 (xz)
*          refactor from MACRO to function
*/
bool gbl_rb_is_full(gbl_rb_t *rb);

/*
* func     gbl_rb_remain
*
* brief    get ring buffer remain ROW size
*
* param    rb      gbl_rb_t pointer
*
* return   >= 0    remain row size
*
* version  v0.1 2021.12.07 (xz)
*          refactor from MACRO to function
*/
uint16_t gbl_rb_remain(gbl_rb_t *rb);

/*
* func     gbl_rb_used
*
* brief    get ring buffer used ROW size
*
* param    rb      gbl_rb_t pointer
*
* return   >= 0    used row size
*
* version  v0.1 2021.12.07 (xz)
*          refactor from MACRO to function
*/
uint16_t gbl_rb_used(gbl_rb_t *rb);

/* func     gbl_rb_write
*
* brief    write amount of ROW to ring buffer
*
* param    rb      ring buffer structure pointier
*
*          data    data address
*
*          row     row = unit amount, so, it means
*                  data size = row * rb->col
*
*          done    true  DO     increase w index
*                  false DO NOT increase w index
*
* return   >= 0    amount of ROW written
*          <  0    error
*                  -EINVAL  rb       == NLL
*                           data     == NULL
*                           row      >= rb->row
*
*                           rb->buff == NULL
*
*                  -ENOBUFS rb remain size not enough
*                           skip write process
*
* version  V0.2 2021.12.15 (xz)
*            add parameter "done" to decide if increase rb->w
*          v0.1 2021.12.07 (xz)
*            refactor from MACRO to function
*/
int32_t gbl_rb_write(gbl_rb_t *rb, void *data, uint16_t row, bool done);

/* func     gbl_rb_read
*
* brief    fetch a mount of data from ring buffer to *buff
*          it almost same as gbl_rb_read, but it will not increase index rb->r
*
* param    rb      ring buffer structure pointier
*
*          buff    buff address
*
*          row     row = unit amount, so, it means
*                  buff size = row * rb->col
*
*          done    true  DO     increase r index
*                  false DO NOT increase r index
*
* return   size    amount of ROW read
*          <  0    error
*                  -EINVAL  rb    == NLL
*                           buff  == NULL
*
*                           rb->buff == NULL
*
* version  V0.2 2021.12.15 (xz)
*            add parameter "done" to decide if increase rb->r
*
*          v0.1 2021.12.07 (xz)
*            refactor from MACRO to function
*/
int32_t gbl_rb_read(gbl_rb_t *rb, void *buff, uint16_t row, bool done);

/* func     gbl_rb_ptr_r_get
*
* brief
*
* param    rb      ring buffer structure pointier
*
* return   >  0    pointer of the read unit
*          NULL    rb       == NLL
*                  rb->buff == NULL
*                  rb       is empty
*
* version  v0.1 2021.12.15 (xz)
*          create
*/
uint8_t *gbl_rb_ptr_r_get(gbl_rb_t *rb);

/* func     gbl_rb_ptr_w_get
*
* brief
*
* param    rb      ring buffer structure pointier
*
* return   >  0    pointer of the read unit
*          NULL    rb       == NLL
*                  rb->buff == NULL
*                  rb       is full
*
* version  v0.1 2021.12.15 (xz)
*          create
*/
uint8_t *gbl_rb_ptr_w_get(gbl_rb_t *rb);

/* func     gbl_rb_idx_r_inc
*
* brief
*
* param    rb      ring buffer structure pointier
*
* return   >= 0    current read index
*          <  0    error
*                  -EINVAL  rb       == NLL
*                  -ENOBUFS rb       is empty
*
* version  v0.1 2021.12.15 (xz)
*          create
*/
int32_t gbl_rb_idx_r_inc(gbl_rb_t *rb);

/* func     gbl_rb_idx_w_inc
*
* brief
*
* param    rb      ring buffer structure pointier
*
* return   >= 0    current write index
*          <  0    error
*                  -EINVAL  rb       == NLL
*                  -ENOBUFS rb       is full
*
* version  v0.1 2021.12.15 (xz)
*          create
*/
int32_t gbl_rb_idx_w_inc(gbl_rb_t *rb);

/* func     gbl_rb_unit_write
*
* brief    write amount of data to current ROW
*
* param    rb      ring buffer structure pointier
*
*          data    data address
*
*          size    data size
*
*          seek    skip bytes at start of unit
*
*          done    true  DO     increase w index
*                  false DO NOT increase w index
*
* return   >= 0    amount of data size written
*          <  0    error
*                  -EINVAL  rb       == NLL
*                           data     == NULL
*                           size     >= rb->col
*
*                           rb->buff == NULL
*
*                  -ENOBUFS rb is full
*                           skip write process
*
* version  v0.1 2021.12.07 (xz)
*          refactor from MACRO to function
*/
int32_t gbl_rb_unit_write(gbl_rb_t *rb, void *data, uint16_t size, uint16_t seek, bool done);

#ifdef __cplusplus
}
#endif

#endif /* GBL_RB_H */
