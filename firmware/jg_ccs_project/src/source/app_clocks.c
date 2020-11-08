/*
 * app_clocks.c
 *
 *  Created on: Oct 28, 2020
 *      Author: jgamm
 */

#include "app_clocks.h"
#include "io.h"

static bool fast_mode = false;

void CLOCKS_initialize(void)
{
    IO_Configure_Struct xt2_settings =
    {
     .direction = ioDirectionInput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthDontcare,
     .function = ioFunctionAlt,
     .interrupts = ioInterruptsNone,
     .initial_output = false
    };
    IO_configurePin(ioPort5, 2, &xt2_settings);
    IO_configurePin(ioPort5, 3, &xt2_settings);
    UCS_initialize();
    UCS_configureMCLK(ucsClockSelDCOCLK, ucsDiv1);
    CLOCKS_cpuSpeedNormal();
    UCS_configureACLK(ucsClockSelREFOCLK, ucsDiv1);
    UCS_configureSMCLK(ucsClockSelDCOCLK, ucsDiv1);
}

void CLOCKS_cpuSpeedNormal(void) // a bit over 1MHz
{
    fast_mode = false;
    UCS_DcoConfig_Struct settings =
    {
     .fll_source = ucsClockSelREFOCLK,
     .fll_source_div = ucsDiv1,
     .fll_div = 0,
     .fll_mult = 127,
     .range = ucsDcoRange320to7380kHz
    };
    UCS_configureDco(&settings);
}

void CLOCKS_cpuSpeedFast(void) // 20MHz
{
    fast_mode = true;
    UCS_DcoConfig_Struct settings =
    {
     .fll_source = ucsClockSelXT2CLK,
     .fll_source_div = ucsDiv1,
     .fll_div = 1,
     .fll_mult = 4,
     .range = ucsDcoRange2500to54100kHz
    };
    UCS_configureDco(&settings);
}

uint16_t CLOCKS_getAclkFreqHz(void)
{
    return UCS_REFO_FREQ_HZ;
}

uint16_t CLOCKS_getSmclkFreqKhz(void)
{
    return UCS_XT2_FREQ_MHZ*250;
}

uint16_t CLOCKS_getMclkFreqKhz(void)
{
    if(fast_mode)
        return UCS_XT2_FREQ_MHZ*4000;
    else
        return 32*(UCS_REFO_FREQ_HZ/1000) + (32*UCS_REFO_FREQ_HZ)%1000;
}
