/*
 * app_timer.c
 *
 *  Created on: Oct 25, 2020
 *      Author: jgamm
 */

#include "pulse_train.h"
#include "interrupts.h"

static TIMERA_Base_Enum timer;
static uint32_t current_ticks = 0;
static volatile bool * done_flag = (bool *) 0;

uint32_t stop_points[64];
uint8_t stop_points_index = 0;

static void __attribute__ ((interrupt)) process_tick(void)
{
    current_ticks -= 1;
    if(current_ticks == 0)
    {
        TIMERA_stop(timer);
        *done_flag = true;
        done_flag = (bool *) 0;
    }
}

void PULSETRAIN_configure(PULSETRAIN_Configuration_Struct * settings)
{
    timer = settings->timer;

    TIMERA_Configure_Struct timer_settings =
    {
     .clock_source = timeraClkSrcSMCLK,
     .clock_division = settings->divider,
     .ien = false
    };
    TIMERA_configure(settings->timer, &timer_settings);

    TIMERA_ConfigureCcr_Struct ccr0_settings =
    {
     .mode = timeraCcrCcModeCompare,
     .input = timeraCcrCcInputGND,
     .capture_mode = timeraCcrCaptureModeNoCapture,
     .capture_sync = timeraCcrCaptureSyncAsynchronous,
     .output_mode = timeraCcrOutputModeOutput,
     .ien = true
    };
    TIMERA_configureCcr(settings->timer, 0, &ccr0_settings);
    TIMERA_setCcr(settings->timer, 0, settings->ticks_on+settings->ticks_off);

    TIMERA_ConfigureCcr_Struct ccr1_settings =
    {
     .mode = timeraCcrCcModeCompare,
     .input = timeraCcrCcInputGND,
     .capture_mode = timeraCcrCaptureModeNoCapture,
     .capture_sync = timeraCcrCaptureSyncAsynchronous,
     .output_mode = timeraCcrOutputModeSetReset,
     .ien = false
    };
    TIMERA_configureCcr(settings->timer, settings->output, &ccr1_settings);
    TIMERA_setCcr(settings->timer, settings->output, settings->ticks_on);

    INT_configureHandler(intSourceTA0_CCR0, &process_tick);
}

void PULSETRAIN_start(uint32_t num_ticks, volatile bool * flag)
{
    current_ticks = num_ticks;
    TIMERA_start(timer, timeraModeUp);
    done_flag = flag;
}

void PULSETRAIN_stop(void)
{
    TIMERA_stop(timer);
    stop_points[stop_points_index] = current_ticks;
    stop_points_index += 1;
    current_ticks = 0;
}
