/*
 * find_reference.c
 *
 *  Created on: Oct 31, 2020
 *      Author: jgamm
 */

#include "find_reference.h"
#include "io.h"
#include "interrupts.h"
#include "pulse_train.h"

static volatile bool is_found = false;

static void __attribute__ ((interrupt)) es_change_handler(void)
{
    is_found = true;
    PULSETRAIN_stop();
    IO_clearIfg(FR_ENDSWITCH_PORT, FR_ENDSWITCH_PIN);
}

void FR_initialize(void)
{
    IO_Configure_Struct input_settings =
    {
     .direction = ioDirectionInput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthDontcare,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsFalling,
     .initial_output = false
    };
    IO_configurePin(FR_ENDSWITCH_PORT, FR_ENDSWITCH_PIN, &input_settings);
    INT_configureHandler(intSourceIOP1, &es_change_handler);
}

void FR_find(void)
{
    IO_disablePin(ioPort2, 0); // DIR
    IO_Configure_Struct dir_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthReduced,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsNone,
     .initial_output = true
    };
    IO_configurePin(ioPort2, 0, &dir_settings);

    IO_disablePin(ioPort2, 2); // RESET
    IO_Configure_Struct reset_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthReduced,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsNone,
     .initial_output = false
    };
    IO_configurePin(ioPort2, 2, &reset_settings);

    IO_disablePin(ioPort2, 4); // SD
    IO_Configure_Struct sd_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthReduced,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsNone,
     .initial_output = false
    };
    IO_configurePin(ioPort2, 4, &sd_settings);

    IO_disablePin(ioPort1, 2); // STEP
    IO_Configure_Struct step_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthReduced,
     .function = ioFunctionAlt,
     .interrupts = ioInterruptsNone,
     .initial_output = false
    };
    IO_configurePin(ioPort1, 2, &step_settings);


    while(1) {
    PULSETRAIN_Configuration_Struct f1_settings =
    {
     .timer = TA0,
     .output = 1,
     .divider = timeraClkDiv1,
     .ticks_on = 90,
     .ticks_off = 90
    };
    PULSETRAIN_configure(&f1_settings);
    PULSETRAIN_start(1000000000, 0);

    while(!is_found); // First falling edge
    is_found = false;
    }
    /*
    for(uint16_t i=0; i<65535; ++i);

    while(IO_readPin(FR_ENDSWITCH_PORT, FR_ENDSWITCH_PIN))
    {
        PULSETRAIN_Configuration_Struct f1_settings =
        {
         .timer = TA0,
         .output = 1,
         .divider = timeraClkDiv1,
         .ticks_on = 60,
         .ticks_off = 60
        };
        PULSETRAIN_configure(&f1_settings);
        PULSETRAIN_start(100, 0);
        for(uint16_t i=0; i<65535; ++i);
    }




    is_found = false;

    IO_Configure_Struct input_settings =
    {
     .direction = ioDirectionInput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthDontcare,
     .function = ioFunctionGpio,
     .interrupts = ioInterruptsRising,
     .initial_output = false
    };
    IO_configurePin(FR_ENDSWITCH_PORT, FR_ENDSWITCH_PIN, &input_settings);
    IO_writePin(ioPort2, 0, false);

    PULSETRAIN_Configuration_Struct r1_settings =
    {
     .timer = TA0,
     .output = 1,
     .divider = timeraClkDiv1,
     .ticks_on = 600,
     .ticks_off = 600
    };
    PULSETRAIN_configure(&r1_settings);
    PULSETRAIN_start(5000000, 0);

    while(!is_found); // first rising edge

    for(uint16_t i=0; i<65535; ++i);

    while(!IO_readPin(FR_ENDSWITCH_PORT, FR_ENDSWITCH_PIN))
    {
        PULSETRAIN_Configuration_Struct f1_settings =
        {
         .timer = TA0,
         .output = 1,
         .divider = timeraClkDiv1,
         .ticks_on = 60,
         .ticks_off = 60
        };
        PULSETRAIN_configure(&f1_settings);
        PULSETRAIN_start(100, 0);
        for(uint16_t i=0; i<65535; ++i);
    }*/


    while(1);
}

