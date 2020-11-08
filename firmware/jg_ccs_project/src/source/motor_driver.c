/*
 * motor_driver.c
 *
 *  Created on: Nov 1, 2020
 *      Author: jgamm
 */

#include "motor_driver.h"
#include "interrupts.h"
#include "app_assert.h"
#include "delay.h"

#define MD_CWBUTTON_PIN    1
#define MD_CWBUTTON_PORT   ioPort2
#define MD_CCWBUTTON_PIN   1
#define MD_CCWBUTTON_PORT  ioPort1
#define MD_CW_DIR          false
#define MD_CCW_DIR         true
#define MD_BUTTONSPEED_KHZ 80
#define MD_TIMERSPEED_KHZ  4000
#define MD_CCWLED_PORT     ioPort4
#define MD_CCWLED_PIN      7
#define MD_CWLED_PORT      ioPort1
#define MD_CWLED_PIN       0

typedef struct
{
    TIMERA_Base_Enum timer;
    uint8_t timer_output_ccr;
    IO_Port_Enum step_port;
    uint8_t step_pin;
    IO_Port_Enum dir_port;
    uint8_t dir_pin;
    IO_Port_Enum res_port;
    uint8_t res_pin;
    IO_Port_Enum sd_port;
    uint8_t sd_pin;
    bool in_use;
    bool direction;
    void (* done_handler)(void);
} _State_Struct;

_State_Struct state;
bool configured = false;
uint32_t num_pulses;

static void enable_cw_button(void)
{
    IO_clearIfg(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN);
    if(IO_readPin(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN))
        IO_configureInterrupts(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN, ioInterruptsFalling);
    else
        IO_configureInterrupts(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN, ioInterruptsRising);
}

static void disable_cw_button(void)
{
    IO_configureInterrupts(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN, ioInterruptsNone);
}

static void enable_ccw_button(void)
{
    IO_clearIfg(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN);
    if(IO_readPin(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN))
        IO_configureInterrupts(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN, ioInterruptsFalling);
    else
        IO_configureInterrupts(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN, ioInterruptsRising);
}

static void disable_ccw_button(void)
{
    IO_configureInterrupts(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN, ioInterruptsNone);
}

static void __attribute__ ((interrupt)) count_timer_pulses(void)
{
    num_pulses -= 1;
    if(num_pulses == 0)
    {
        TIMERA_stop(state.timer);
        TIMERA_configureInterrupts(state.timer, 0, false);
        state.in_use = false;
        switch(state.direction)
        {
        case MD_CW_DIR:
            IO_writePin(MD_CWLED_PORT, MD_CWLED_PIN, false);
        case MD_CCW_DIR:
            IO_writePin(MD_CCWLED_PORT, MD_CCWLED_PIN, false);
        }
        (*state.done_handler)();
        enable_cw_button();
        enable_ccw_button();
    }
}

static void __attribute__ ((interrupt)) cw_button_pressed(void)
{
    ASSERT_temp(configured);
    disable_ccw_button();
    IO_clearIfg(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN);
    IO_writePin(state.dir_port, state.dir_pin, MD_CW_DIR);
    bool button_state = IO_readPin(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN);
    if(!button_state)
    {
        disable_cw_button();
        DELAY_setDelay(25, &enable_cw_button);
        TIMERA_setCcr(state.timer, 0, MD_TIMERSPEED_KHZ/MD_BUTTONSPEED_KHZ);
        TIMERA_setCcr(state.timer, state.timer_output_ccr, MD_TIMERSPEED_KHZ/(2*MD_BUTTONSPEED_KHZ));
        TIMERA_start(state.timer, timeraModeUp);
        IO_writePin(MD_CWLED_PORT, MD_CWLED_PIN, true);
        state.in_use = true;
    }
    else
    {
        disable_cw_button();
        DELAY_setDelay(25, &enable_cw_button);
        TIMERA_stop(state.timer);
        IO_writePin(MD_CWLED_PORT, MD_CWLED_PIN, false);
        state.in_use = false;
        enable_ccw_button();
    }
}

static void __attribute__ ((interrupt)) ccw_button_pressed(void)
{
    ASSERT_temp(configured);
    disable_cw_button();
    IO_clearIfg(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN);
    IO_writePin(state.dir_port, state.dir_pin, MD_CCW_DIR);
    bool button_state = IO_readPin(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN);
    if(!button_state)
    {
        disable_ccw_button();
        DELAY_setDelay(25, &enable_ccw_button);
        TIMERA_setCcr(state.timer, 0, MD_TIMERSPEED_KHZ/MD_BUTTONSPEED_KHZ);
        TIMERA_setCcr(state.timer, state.timer_output_ccr, MD_TIMERSPEED_KHZ/(2*MD_BUTTONSPEED_KHZ));
        TIMERA_start(state.timer, timeraModeUp);
        IO_writePin(MD_CCWLED_PORT, MD_CCWLED_PIN, true);
        state.in_use = true;
    }
    else
    {
        disable_ccw_button();
        DELAY_setDelay(25, &enable_ccw_button);
        TIMERA_stop(state.timer);
        IO_writePin(MD_CCWLED_PORT, MD_CCWLED_PIN, false);
        state.in_use = false;
        enable_cw_button();
    }
}

void MD_configure(MD_Configuration_Struct * settings)
{
    if(configured)
        return;
    state.timer = settings->timer;
    state.step_port = settings->step_port;
    state.step_pin = settings->step_pin;
    state.dir_port = settings->dir_port;
    state.dir_pin = settings->dir_pin;
    state.res_port = settings->res_port;
    state.res_pin = settings->res_pin;
    state.sd_port = settings->sd_port;
    state.sd_pin = settings->sd_pin;
    state.in_use = false;
    num_pulses = 0;
    configured = true;

    switch(state.timer)
    {
    case TA0:
        ASSERT_temp(state.step_port == ioPort1);
        ASSERT_temp(2<=state.step_pin && state.step_pin<=5);
        state.timer_output_ccr = state.step_pin-1;
        break;
    case TA1:
        ASSERT_temp(state.step_port == ioPort2);
        ASSERT_temp(0<=state.step_pin && state.step_pin<=1);
        state.timer_output_ccr = state.step_pin+1;
        break;
    case TA2:
        ASSERT_temp(state.step_port == ioPort2);
        ASSERT_temp(4<=state.step_pin && state.step_pin<=5);
        state.timer_output_ccr = state.step_pin-3;
        break;
    default:
        ASSERT_perm(false);
    }
    TIMERA_Configure_Struct timer_settings =
    {
     .clock_source = timeraClkSrcSMCLK,
     .clock_division = timeraClkDiv1,
     .ien = false
    };
    TIMERA_configure(state.timer, &timer_settings);
    TIMERA_ConfigureCcr_Struct ccr0_settings =
    {
     .mode = timeraCcrCcModeCompare,
     .input = timeraCcrCcInputGND,
     .capture_mode = timeraCcrCaptureModeNoCapture,
     .capture_sync = timeraCcrCaptureSyncAsynchronous,
     .output_mode = timeraCcrOutputModeOutput,
     .ien = false
    };
    TIMERA_configureCcr(state.timer, 0, &ccr0_settings);
    TIMERA_ConfigureCcr_Struct ccrx_settings =
    {
     .mode = timeraCcrCcModeCompare,
     .input = timeraCcrCcInputGND,
     .capture_mode = timeraCcrCaptureModeNoCapture,
     .capture_sync = timeraCcrCaptureSyncAsynchronous,
     .output_mode = timeraCcrOutputModeSetReset,
     .ien = false
    };
    TIMERA_configureCcr(state.timer, state.timer_output_ccr, &ccrx_settings);

    IO_Configure_Struct step_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthReduced,
     .function = ioFunctionAlt,
     .interrupts = ioInterruptsNone,
     .initial_output = false
    };
    IO_configurePin(state.step_port, state.step_pin, &step_settings);

    IO_Configure_Struct gpio_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthReduced,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsNone,
     .initial_output = false
    };
    IO_configurePin(state.dir_port, state.dir_pin, &gpio_settings);
    IO_configurePin(state.res_port, state.res_pin, &gpio_settings);
    IO_configurePin(state.sd_port, state.sd_pin, &gpio_settings);
    IO_configurePin(MD_CWLED_PORT, MD_CWLED_PIN, &gpio_settings);
    IO_configurePin(MD_CCWLED_PORT, MD_CCWLED_PIN, &gpio_settings);

    IO_Configure_Struct button_settings =
    {
     .direction = ioDirectionInput,
     .resistor = ioResistorPullup,
     .drive_strength = ioDriveStrengthDontcare,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsFalling,
     .initial_output = true
    };
    IO_configurePin(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN, &button_settings);
    IO_configurePin(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN, &button_settings);
    IO_clearIfg(MD_CWBUTTON_PORT, MD_CWBUTTON_PIN);
    IO_clearIfg(MD_CCWBUTTON_PORT, MD_CCWBUTTON_PIN);
    INT_configureHandler(intSourceIOP1, &ccw_button_pressed);
    INT_configureHandler(intSourceIOP2, &cw_button_pressed);
}

void MD_turnMotor(bool dir, uint32_t num_steps, uint32_t frequency, void (* done_handler)(void))
{
    ASSERT_temp(configured);
    ASSERT_perm(state.in_use == false);
    disable_cw_button();
    disable_ccw_button();
    num_pulses = num_steps;
    state.done_handler = done_handler;
    state.in_use = true;
    state.direction = dir;
    IO_writePin(state.dir_port, state.dir_pin, dir);
    if(dir == MD_CW_DIR)
        IO_writePin(MD_CWLED_PORT, MD_CWLED_PIN, true);
    else if(dir == MD_CCW_DIR)
        IO_writePin(MD_CCWLED_PORT, MD_CCWLED_PIN, true);
    else
        ASSERT_perm(false);
    INT_configureHandler(intSourceTA0_CCR0, &count_timer_pulses);
    TIMERA_setCcr(state.timer, 0, (1000*(uint32_t)MD_TIMERSPEED_KHZ)/frequency);
    TIMERA_setCcr(state.timer, state.timer_output_ccr, (1000*(uint32_t)MD_TIMERSPEED_KHZ)/(2*frequency));
    TIMERA_configureInterrupts(state.timer, 0, true);
    TIMERA_start(state.timer, timeraModeUp);
}

bool MD_inUse(void)
{
    ASSERT_temp(configured);
    return state.in_use;
}

void MD_findEndSwitch(void * done_handler)
{
    ASSERT_perm(false);
}
