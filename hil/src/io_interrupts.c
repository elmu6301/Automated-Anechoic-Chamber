/*
 * io_interrupts.c
 *
 *  Created on: Feb 21, 2021
 *      Author: jgamm
 */

#include "io_interrupts.h"
#include "error.h"

static void _defaultHandler(void);

static void (*p1_handlers[8])(void) = {[0 ... 7] = _defaultHandler};
static void (*p2_handlers[8])(void) = {[0 ... 7] = _defaultHandler};

void IO_attachInterrupt(IO_Registers_Struct * port, uint8_t pin, void (*handler)(void))
{
    uint8_t pin_bit;
    for(pin_bit=0; (pin&1)==0; pin>>=1, ++pin_bit);
    switch((uintptr_t)port)
    {
    case (uintptr_t)P1:
        p1_handlers[pin_bit] = handler;
        break;
    case (uintptr_t)P2:
        p2_handlers[pin_bit] = handler;
        break;
    default:
        ASSERT(false);
    }
}

static void _defaultHandler(void)
{
    ASSERT(false);
}

#include <msp430.h>
#pragma vector=PORT1_VECTOR
void __attribute__ ((interrupt)) p1_IRQHandler(void)
{
    uint8_t i;
    uint8_t flags = P1->IFG & P1->IE;
    P1->IFG = 0;
    for(i=7; i<8; --i)
        if((flags&(1<<i)) != 0)
            (*p1_handlers[i])();
}

#pragma vector=PORT2_VECTOR
void __attribute__ ((interrupt)) p2_IRQHandler(void)
{
    uint8_t i;
    uint8_t flags = P2->IFG & P2->IE;
    P2->IFG = 0;
    for(i=7; i<8; --i)
        if((flags&(1<<i)) != 0)
            (*p2_handlers[i])();
}
