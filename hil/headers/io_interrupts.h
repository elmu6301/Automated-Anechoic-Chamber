/*
 * io_interrupts.h
 *
 *  Created on: Feb 21, 2021
 *      Author: jgamm
 */

#ifndef HIL_HEADERS_IO_INTERRUPTS_H_
#define HIL_HEADERS_IO_INTERRUPTS_H_

#include "io_hal.h"

void IO_attachInterrupt(IO_Registers_Struct * port, uint8_t pin, void (*handler)(void));


#endif /* HIL_HEADERS_IO_INTERRUPTS_H_ */
