/*
 * led_hil.h
 *
 *  Created on: Feb 20, 2021
 *      Author: jgamm
 */

#ifndef HIL_HEADERS_LED_HIL_H_
#define HIL_HEADERS_LED_HIL_H_

typedef enum
{
    LED1,
    LED2
} LEDI_Led_Enum;

void LEDI_init(void);

void LEDI_setLed(LEDI_Led_Enum led);

void LEDI_clearLed(LEDI_Led_Enum led);

void LEDI_toggleLed(LEDI_Led_Enum led);



#endif /* HIL_HEADERS_LED_HIL_H_ */
