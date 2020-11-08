/*
 * delay.h
 *
 *  Created on: Nov 1, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_DELAY_H_
#define SRC_HEADERS_DELAY_H_

#include <stdint.h>

void DELAY_setDelay(uint16_t time_ms, void (*handler)(void));

#endif /* SRC_HEADERS_DELAY_H_ */
