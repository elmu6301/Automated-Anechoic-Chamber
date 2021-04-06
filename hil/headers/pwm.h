/*
 * pwm.h
 *
 *  Created on: Feb 20, 2021
 *      Author: jgamm
 */

#ifndef HIL_HEADERS_PWM_H_
#define HIL_HEADERS_PWM_H_

#include <stdint.h>
#include <stdbool.h>

typedef enum
{
    timerA0 = 0,
    timerA1 = 1,
    timerA2 = 2
} PWM_Sources_Enum;

typedef struct
{
    uint8_t percent_on;
    uint8_t output;
    uint32_t freq_hz;
    bool initial_output;
    bool gradual;
} PWM_Config_Struct;

void PWM_configure(PWM_Sources_Enum source, PWM_Config_Struct * config);

void PWM_start(PWM_Sources_Enum source, uint32_t num_pulses, void (*handler)(void));

void PWM_stop(PWM_Sources_Enum source);



#endif /* HIL_HEADERS_PWM_H_ */
