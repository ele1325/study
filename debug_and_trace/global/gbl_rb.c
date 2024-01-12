/** \file   gbl_rb.c
 *  \brief  ring-buffer module
 *
 *  \todo   None
 * 
 *  \author 2021.06.22 (XZ Hong) create
 */

#include "gbl_stdio.h"
#include <string.h>

#include "gbl_rb.h"

uint16_t gbl_rb_init(gbl_rb_t *rb, void *buff, uint16_t size, uint16_t row, uint16_t col)
{
    if (row * col >= 65535)
        return -EINVAL;

    if (size != row * col)
        return -EINVAL;

    rb->buff = buff;
    rb->size = size;
    rb->row = row;
    rb->col = col;
    rb->r = 0;
    rb->w = 0;

    return 0;
}

bool gbl_rb_is_empty(gbl_rb_t *rb)
{
    return (rb->r == rb->w);
}

bool gbl_rb_is_full(gbl_rb_t *rb)
{
    return ((rb->w + 1) % rb->row == rb->r);
}

uint16_t gbl_rb_remain(gbl_rb_t *rb)
{
    return (rb->r - rb->w + rb->row - 1) % rb->row;
}

uint16_t gbl_rb_used(gbl_rb_t *rb)
{
    return (rb->w - rb->r + rb->row) % rb->row;
}

int32_t gbl_rb_write(gbl_rb_t *rb, void *data, uint16_t row, bool done)
{
    // --------------------------------------------------------------
    //
    // rb->row = 8
    //
    // r   = 2
    // w   = 4
    //
    //     r   w
    // 0 1 2 3 4 5 6 7
    //
    // remain = 5  (2-4+8-1)%8
    // used   = 2  (4-2+8)%8
    //
    // --------------------------------------------------------------

    if ((rb == NULL) || (data == NULL) || (row < 0) || (row >= rb->row))
        return -EINVAL;

    if (rb->buff == NULL)
        return -EINVAL;

    if (gbl_rb_remain(rb) < row)
        return -1;

    if (gbl_rb_is_full(rb))
        return 0;

    uint8_t *c = (uint8_t *)data;

    if ((rb->w + row) < rb->row) // within boundary
    {
        memcpy(&rb->buff[rb->w * rb->col], c, row * rb->col);
    }
    else // out of boundary
    {
        uint16_t row1 = rb->row - rb->w;
        uint16_t row2 = row - row1;

        memcpy(&rb->buff[rb->w * rb->col], &c[0], row1 * rb->col);
        memcpy(&rb->buff[0], &c[row1 * rb->col], row2 * rb->col);
    }

    if (done)
        rb->w = (rb->w + row) % rb->row;

    return row;
}

int32_t gbl_rb_read(gbl_rb_t *rb, void *buff, uint16_t row, bool done)
{
    // --------------------------------------------------------------
    //
    // rb->row = 8
    //
    // r   = 4
    // w   = 2
    //
    //     w   r
    // 0 1 2 3 4 5 6 7
    //
    // remain = 1  (4-2+8-1)%8
    // used   = 6  (2-4+8)%8
    //
    // --------------------------------------------------------------

    if ((rb == NULL) || (buff == NULL))
        return -EINVAL;

    if (rb->buff == NULL)
        return -EINVAL;

    uint16_t used = gbl_rb_used(rb);

    row = (row <= used) ? row : used;

    if (row == 0)
        return 0;

    uint8_t *c = (uint8_t *)buff;

    if ((rb->r + row) < rb->row) // within boundary
    {
        memcpy(c, &rb->buff[rb->r * rb->col], row * rb->col);
    }
    else // out of boundary
    {
        uint16_t row1 = rb->row - rb->r;
        uint16_t row2 = row - row1;

        memcpy(&c[0], &rb->buff[rb->r * rb->col], row1 * rb->col);
        memcpy(&c[row1 * rb->col], &rb->buff[0], row2 * rb->col);
    }

    if (done)
        rb->r = (rb->r + row) % rb->row;

    return row;
}

uint8_t *gbl_rb_ptr_r_get(gbl_rb_t *rb)
{
    if (rb == NULL)
        return NULL;

    if (rb->buff == NULL)
        return NULL;

    if (gbl_rb_is_empty(rb))
        return NULL;

    return &rb->buff[rb->r * rb->col];
}

uint8_t *gbl_rb_ptr_w_get(gbl_rb_t *rb)
{
    if (rb == NULL)
        return NULL;

    if (rb->buff == NULL)
        return NULL;

    if (gbl_rb_is_full(rb))
        return NULL;

    return &rb->buff[rb->w * rb->col];
}

int32_t gbl_rb_idx_r_inc(gbl_rb_t *rb)
{
    if (rb == NULL)
        return -EINVAL;

    if (gbl_rb_is_empty(rb))
        return -ENOBUFS;

    rb->r = (rb->r + 1) % rb->row;

    return rb->r;
}

int32_t gbl_rb_idx_w_inc(gbl_rb_t *rb)
{
    if (rb == NULL)
        return -EINVAL;

    if (gbl_rb_is_full(rb))
        return -ENOBUFS;

    rb->w = (rb->w + 1) % rb->row;

    return rb->w;
}

int32_t gbl_rb_unit_write(gbl_rb_t *rb, void *data, uint16_t size,
                          uint16_t seek, bool done)
{
    if ((rb == NULL) || (data == NULL) || (size > rb->col))
        return -EINVAL;

    if (rb->buff == NULL)
        return -EINVAL;

    if ((size + seek) > rb->col)
        return -ENOBUFS;

    if (gbl_rb_is_full(rb))
        return -ENOBUFS;

    memcpy(&rb->buff[(rb->w * rb->col) + seek], data, size);

    if (done)
    {
        rb->w = (rb->w + 1) % rb->row;
    }

    return size;
}
