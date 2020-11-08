/*
 * delay.c
 *
 *  Created on: Nov 1, 2020
 *      Author: jgamm
 */

#include "delay.h"
#include "timer_a.h"
#include "interrupts.h"

static void (*handler)(void);

static void __attribute__ ((interrupt)) delay_done(void)
{
    TIMERA_stop(TA2);
    TIMERA_setCount(TA2, 0);
    (*handler)();
}

void DELAY_setDelay(uint16_t time_ms, void (*done_handler)(void))
{
    handler = done_handler;
    TIMERA_Configure_Struct timer_settings =
    {
     .clock_source = timeraClkSrcACLK,
     .clock_division = timeraClkDiv8,
     .ien = false
    };
    TIMERA_configure(TA2, &timer_settings);
    TIMERA_ConfigureCcr_Struct ccr0_settings =
    {
     .mode = timeraCcrCcModeCompare,
     .input = timeraCcrCcInputGND,
     .capture_mode = timeraCcrCaptureModeNoCapture,
     .capture_sync = timeraCcrCaptureSyncAsynchronous,
     .output_mode = timeraCcrOutputModeOutput,
     .ien = true
    };
    TIMERA_configureCcr(TA2, 0, &ccr0_settings);
    TIMERA_setCcr(TA2, 0, time_ms*4);
    TIMERA_setCount(TA2, 0);
    INT_configureHandler(intSourceTA2_CCR0, &delay_done);
    TIMERA_start(TA2, timeraModeUp);
}
