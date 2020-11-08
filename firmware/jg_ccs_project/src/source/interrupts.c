/*
 * interrupts.c
 *
 *  Created on: Oct 25, 2020
 *      Author: jgamm
 */

#include "interrupts.h"
#include "app_assert.h"
#include "in430.h"
#include <stdint.h>
#include <string.h>

#define NUM_VECTORS 64
#define TOP_RAM 0x4400
#define SYSCTL_ADDRESS 0x0180

#define GIE_SET() __asm__ __volatile__ ("nop { nop { eint { nop { nop")
#define GIE_CLEAR() __asm__ __volatile__ ("dint { nop { nop")

static uint16_t num_blocks = 0;

void INT_initialize(void)
{
    *((uint16_t *) SYSCTL_ADDRESS) |= 1<<0;
    void * fptr = INT_defaultHandler;
    for(uint16_t i=0; i<NUM_VECTORS; ++i)
        memcpy((void *) TOP_RAM-2*i-2, &(fptr), 2);
}

void INT_configureGie(bool enable)
{
    if(enable)
        GIE_SET();//_enable_interrupts();
    else
        GIE_CLEAR();//_disable_interrupts();
}

void INT_addBlock(void)
{
    if(num_blocks == 0)
        GIE_CLEAR();//_disable_interrupts();
    num_blocks += 1;
}

void INT_removeBlock(void)
{
    num_blocks -= 1;
    if(num_blocks == 0)
        GIE_SET();//_enable_interrupts();
}

void INT_configureHandler(INT_Sources_Enum source, void * handler)
{
    memcpy((void *) TOP_RAM-2*source-2, &(handler), 2);
}

void * INT_getHandler(INT_Sources_Enum source)
{
    return (void *) TOP_RAM-2*source-2;
}

void __attribute__ ((interrupt)) INT_defaultHandler(void)
{
    ASSERT_perm(false);
}
