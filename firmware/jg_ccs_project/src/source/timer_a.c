/*
 * timer_a.c
 *
 *  Created on: Oct 7, 2020
 *      Author: jgamm
 */

#include "timer_a.h"
#include "app_assert.h"

#define NUM_TIMERS (3)
#define NUM_CCR (7)

typedef struct
{
    volatile uint16_t CTL;
    volatile uint16_t CCTL[NUM_CCR];
    volatile uint16_t R;
    volatile uint16_t CCR[NUM_CCR];
    volatile uint16_t EX0;
    const volatile uint8_t empty0[0xC];
    volatile uint16_t IV;
} _timera_Struct;

#define TA0_BASE ((_timera_Struct *) 0x0340)
#define TA1_BASE ((_timera_Struct *) 0x0380)
#define TA2_BASE ((_timera_Struct *) 0x0400)

static _timera_Struct * timers[NUM_TIMERS] = {TA0_BASE, TA1_BASE, TA2_BASE};

void TIMERA_configure(TIMERA_Base_Enum tax, TIMERA_Configure_Struct * settings)
{
    ASSERT_temp(0<=tax && tax<NUM_TIMERS);
    timers[tax]->CTL = 0;
    timers[tax]->CTL |= (1<<1)*(settings->ien);
    timers[tax]->CTL |= (settings->clock_division)<<6;
    timers[tax]->CTL |= (settings->clock_source)<<8;
}

void TIMERA_configureCcr(TIMERA_Base_Enum tax, uint8_t ccrn, TIMERA_ConfigureCcr_Struct * settings)
{
    timers[tax]->CCTL[ccrn] = 0;
    timers[tax]->CCTL[ccrn] |= (1<<4)*(settings->ien);
    timers[tax]->CCTL[ccrn] |= (settings->output_mode)<<5;
    timers[tax]->CCTL[ccrn] |= (settings->mode)<<8;
    timers[tax]->CCTL[ccrn] |= (settings->capture_sync)<<11;
    timers[tax]->CCTL[ccrn] |= (settings->input)<<12;
    timers[tax]->CCTL[ccrn] |= (settings->capture_mode)<<14;
}

void TIMERA_start(TIMERA_Base_Enum tax, TIMERA_Mode_Enum mode)
{
    timers[tax]->CTL &= ~(3<<4);
    timers[tax]->CTL |= mode<<4;
}

void TIMERA_stop(TIMERA_Base_Enum tax)
{
    timers[tax]->CTL &= ~(3<<4);
}

void TIMERA_setCount(TIMERA_Base_Enum tax, uint16_t val)
{
    timers[tax]->R = val;
}

uint16_t TIMERA_getCount(TIMERA_Base_Enum tax)
{
    return timers[tax]->R;
}

void TIMERA_setCcr(TIMERA_Base_Enum tax, uint8_t ccrn, uint16_t val)
{
    timers[tax]->CCR[ccrn] = val;
}

uint16_t TIMERA_getCcr(TIMERA_Base_Enum tax, uint8_t ccrn)
{
    return timers[tax]->CCR[ccrn];
}

void TIMERA_configureInterrupts(TIMERA_Base_Enum tax, uint8_t ccrn, bool en)
{
    timers[tax]->CCTL[ccrn] &= ~(en<<4);
    timers[tax]->CCTL[ccrn] |= (en<<4);
}

