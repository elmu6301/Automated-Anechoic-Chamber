/*
 * io_hal.c
 *
 *  Created on: Feb 13, 2021
 *      Author: jgamm
 */

#include "io_hal.h"

void IO_reset(IO_Registers_Struct * Px)
{
    Px->DIR = IO_DIR_RESET;
    Px->DS  = IO_DS_RESET;
    Px->SEL = IO_SEL_RESET;
    Px->OUT = IO_OUT_RESET;
    Px->REN = IO_REN_RESET;
    Px->IES = IO_IES_RESET;
    Px->IE  = IO_IE_RESET;
    Px->IFG = IO_IFG_RESET;
}

void IO_configurePin(IO_Registers_Struct * Px, uint8_t pin, IO_PinConfig_Struct * config)
{
    Px->OUT &= ~((!config->initial_out)*pin);
    Px->OUT |= config->initial_out*pin;
    Px->DIR &= ~((!config->dir)*pin);
    Px->DIR |= config->dir*pin;
    Px->REN &= ~((!config->ren)*pin);
    Px->REN |= config->ren*pin;
    Px->DS  &= ~((!config->ds)*pin);
    Px->DS  |= config->ds*pin;
    Px->SEL &= ~((!config->sel)*pin);
    Px->SEL |= config->sel*pin;
    Px->IES &= ~((!config->ies)*pin);
    Px->IES |= config->ies*pin;
    Px->IFG &= ~pin;
    Px->IE  &= ~((!config->ie)*pin);
    Px->IE  |= config->ie*pin;
}
