/*
 * led_hil.c
 *
 *  Created on: Feb 20, 2021
 *      Author: jgamm
 */

#include "led_hil.h"
#include "io_hal.h"

#define LED1_PORT (P1)
#define LED2_PORT (P4)
#define LED1_PIN  (IO_PIN0)
#define LED2_PIN  (IO_PIN7)

#define _LED(VAL) ((VAL)==LED1? LED1_PORT : LED2_PORT), ((VAL)==LED1? LED1_PIN : LED2_PIN)

void LEDI_init(void)
{
    IO_PinConfig_Struct led_config =
    {
     .initial_out = ioOutLow,
     .dir = ioDirOutput,
     .ren = false,
     .ds = ioDsReduced,
     .sel = ioSelIo,
     .ies = ioIesFalling,
     .ie = false
    };
    IO_configurePin(_LED(LED1), &led_config);
    IO_configurePin(_LED(LED2), &led_config);
}

void LEDI_setLed(LEDI_Led_Enum led)
{
    IO_writePin(_LED(led), ioOutHigh);
}

void LEDI_clearLed(LEDI_Led_Enum led)
{
    IO_writePin(_LED(led), ioOutLow);
}

void LEDI_toggleLed(LEDI_Led_Enum led)
{
    IO_Out_Enum current_val = IO_readPin(_LED(led));
    IO_writePin(_LED(led), (IO_Out_Enum)!(bool)current_val);
}

