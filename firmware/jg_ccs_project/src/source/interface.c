/*
 * interface.c
 *
 *  Created on: Oct 28, 2020
 *      Author: jgamm
 */

#include "interface.h"
#include "io.h"
#include "pulse_train.h"
#include "vcom.h"
#include "app_assert.h"
#include "motor_driver.h"

volatile bool command_in_progress = false;

static void indicate_done(void)
{
    ASSERT_perm(command_in_progress);
    command_in_progress = false;
    VCOM_transmitString("D", 1);
}

static void executeTurnCommand(bool dir, uint32_t num_steps, uint32_t frequency)
{
    ASSERT_temp(!command_in_progress);
    command_in_progress = true;
    MD_turnMotor(dir, num_steps, frequency, &indicate_done);
}

static void executeEndSwitchCommand(void)
{
    ASSERT_temp(!command_in_progress);
    command_in_progress = true;
    MD_findEndSwitch(&indicate_done);
}

#define C2D(c) (c-'0')

static uint32_t s2d(char * s, uint8_t n)
{
    uint8_t i;
    uint32_t rv = 0, m;
    for(i=n-1, m=1; i<n; --i, m*=10)
        rv += C2D(s[i])*m;
    return rv;
}

void INTERFACE_parseAndExecuteCommand(void)
{
    ASSERT_temp(VCOM_stringAvailable('\n'));
    static char command[64];
    VCOM_getString(command, '\n', 64);
    if(INTERFACE_inProgress())
    {
        VCOM_transmitString("N", 1);
        return;
    }
    MD_Configuration_Struct configuration_settings;
    bool dir;
    uint32_t num_steps;
    uint32_t frequency;
    switch(command[0])
    {
    case 'c':
        if(MD_inUse())
        {
            VCOM_transmitString("N", 1);
            break;
        }
        VCOM_transmitString("A", 1);
        configuration_settings.timer = (TIMERA_Base_Enum) C2D(command[1]);
        configuration_settings.step_port = (IO_Port_Enum) C2D(command[2]);
        configuration_settings.step_pin = (uint8_t) C2D(command[3]);
        configuration_settings.dir_port = (IO_Port_Enum) C2D(command[4]);
        configuration_settings.dir_pin = (uint8_t) C2D(command[5]);
        configuration_settings.res_port = (IO_Port_Enum) C2D(command[6]);
        configuration_settings.res_pin = (uint8_t) C2D(command[7]);
        configuration_settings.sd_port = (IO_Port_Enum) C2D(command[8]);
        configuration_settings.sd_pin = (uint8_t) C2D(command[9]);
        configuration_settings.es_no_port = (IO_Port_Enum) C2D(command[10]);
        configuration_settings.es_no_pin = (uint8_t) C2D(command[11]);
        MD_configure(&configuration_settings);
        VCOM_transmitString("D", 1);
        break;
    case 't':
        if(MD_inUse())
        {
            VCOM_transmitString("N", 1);
            break;
        }
        VCOM_transmitString("A", 1);
        dir = (bool) C2D(command[1]);
        num_steps = s2d(command+2, 10);
        frequency = s2d(command+12, 10);
        executeTurnCommand(dir, num_steps, frequency);
        break;
    case 'e':
        if(MD_inUse())
        {
            VCOM_transmitString("N", 1);
            break;
        }
        VCOM_transmitString("A", 1);
        executeEndSwitchCommand();
        break;
    case 'q':
        if(INTERFACE_inProgress())
            VCOM_transmitString("N", 1);
        else
            VCOM_transmitString("A", 1);
        break;
    default:
        VCOM_transmitString("N", 1);
        break;
    }
}

bool INTERFACE_inProgress(void)
{
    return command_in_progress;
}


