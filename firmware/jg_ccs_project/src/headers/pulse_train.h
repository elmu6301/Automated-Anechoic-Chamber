/*
 * app_timer.h
 *
 *  Created on: Oct 25, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_PULSE_TRAIN_H_
#define SRC_HEADERS_PULSE_TRAIN_H_

#include "timer_a.h"

typedef struct
{
    TIMERA_Base_Enum timer;
    uint8_t output;
    TIMERA_ClkDiv_Enum divider;
    uint16_t ticks_on;
    uint16_t ticks_off;
} PULSETRAIN_Configuration_Struct;

void PULSETRAIN_configure(PULSETRAIN_Configuration_Struct * settings);

void PULSETRAIN_start(uint32_t num_pulses, volatile bool * flag);

void PULSETRAIN_stop(void);

#endif /* SRC_HEADERS_PULSE_TRAIN_H_ */
