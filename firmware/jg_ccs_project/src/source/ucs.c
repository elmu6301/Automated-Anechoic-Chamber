/*
 * ucs.c
 *
 *  Created on: Oct 28, 2020
 *      Author: jgamm
 */

#include "app_assert.h"
#include "ucs.h"

typedef struct
{
    volatile uint16_t UCSCTL0;
    volatile uint16_t UCSCTL1;
    volatile uint16_t UCSCTL2;
    volatile uint16_t UCSCTL3;
    volatile uint16_t UCSCTL4;
    volatile uint16_t UCSCTL5;
    volatile uint16_t UCSCTL6;
    volatile uint16_t UCSCTL7;
    volatile uint16_t UCSCTL8;
} _Ucs_Struct;

#define UCS ((_Ucs_Struct *) 0x0160)

// Code from https://e2e.ti.com/support/microcontrollers/msp430/f/166/t/145592?MSP430F5529-Clock-Configuration-for-25Mhz
void UCS_initialize(void)
{
    do
    {
        UCS->UCSCTL7 &= ~(1<<0 | 1<<3);
        UCS->UCSCTL6 &= ~(1<<8);
    } while(UCS->UCSCTL7 & (1<<0 | 1<<3));
    UCS->UCSCTL6 &= ~(3<<9 | 1<<13);
    if(UCS_XT1_PRESENT)
    {
        ASSERT_temp(false);
    }
    else
        UCS->UCSCTL6 |= 1<<0;
    if(UCS_XT2_PRESENT)
    {
        UCS->UCSCTL6 |= UCS_XT2_BYPASS<<12;
        UCS->UCSCTL6 &= ~(3<<14);
        switch(UCS_XT2_FREQ_MHZ>>3)
        {
        case 0:
            UCS->UCSCTL6 |= 0<<14;
            break;
        case 1:
            UCS->UCSCTL6 |= 1<<14;
            break;
        case 2:
            UCS->UCSCTL6 |= 2<<14;
            break;
        case 3:
            UCS->UCSCTL6 |= 3<<14;
            break;
        default:
            ASSERT_perm(false);
        }
    }
    else
        UCS->UCSCTL6 |= 1<<8;
    UCS->UCSCTL8 &= ~(0xFFF<<4);
    UCS->UCSCTL8 |= (1<<0);
    UCS->UCSCTL8 |= (1<<1);
    UCS->UCSCTL8 |= (1<<2);
}

void UCS_configureDco(UCS_DcoConfig_Struct * settings)
{
    UCS->UCSCTL1 &= ~(1<<0 | 3<<4);
    UCS->UCSCTL2 &= ~(0x1F<<0 | 7<<12);
    UCS->UCSCTL3 &= ~(3<<0 | 3<<4);
    UCS->UCSCTL3 |= (settings->fll_source_div)<<0;
    UCS->UCSCTL3 |= (settings->fll_source)<<4;
    UCS->UCSCTL2 |= (settings->fll_mult)<<0;
    UCS->UCSCTL2 |= (settings->fll_div)<<12;
    UCS->UCSCTL1 |= (settings->range)<<4;
}

void UCS_configureACLK(UCS_ClockSel_Enum source, UCS_Div_Enum div)
{
    UCS->UCSCTL4 = ((UCS->UCSCTL4&~(7<<8))|(source<<8));
    UCS->UCSCTL5 = ((UCS->UCSCTL5&~(7<<12))|(div<<12));
}

void UCS_configureSMCLK(UCS_ClockSel_Enum source, UCS_Div_Enum div)
{
    UCS->UCSCTL4 = ((UCS->UCSCTL4&~(7<<4))|(source<<4));
    UCS->UCSCTL5 = ((UCS->UCSCTL5&~(7<<4))|(div<<4));
}

void UCS_configureMCLK(UCS_ClockSel_Enum source, UCS_Div_Enum div)
{
    UCS->UCSCTL4 = ((UCS->UCSCTL4&~(7<<0))|(source<<0));
    UCS->UCSCTL5 = ((UCS->UCSCTL5&~(7<<0))|(div<<0));
}

