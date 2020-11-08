/*
 * motor_driver.h
 *
 *  Created on: Nov 1, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_MOTOR_DRIVER_H_
#define SRC_HEADERS_MOTOR_DRIVER_H_

#include <stdint.h>
#include <stdbool.h>
#include "timer_a.h"
#include "io.h"

typedef struct
{
    TIMERA_Base_Enum timer;
    IO_Port_Enum step_port;
    uint8_t step_pin;
    IO_Port_Enum dir_port;
    uint8_t dir_pin;
    IO_Port_Enum res_port;
    uint8_t res_pin;
    IO_Port_Enum sd_port;
    uint8_t sd_pin;
} MD_Configuration_Struct;

void MD_configure(MD_Configuration_Struct * settings);

void MD_turnMotor(bool dir, uint32_t num_steps, uint32_t frequency, void (* done_handler)(void));

bool MD_inUse(void);

void MD_findEndSwitch(void * done_handler);

#endif /* SRC_HEADERS_MOTOR_DRIVER_H_ */
