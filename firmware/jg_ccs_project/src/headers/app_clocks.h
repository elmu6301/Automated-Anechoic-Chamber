/*
 * app_clocks.h
 *
 *  Created on: Oct 28, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_APP_CLOCKS_H_
#define SRC_HEADERS_APP_CLOCKS_H_

#include "ucs.h"

void CLOCKS_initialize(void);

void CLOCKS_cpuSpeedNormal(void);

void CLOCKS_cpuSpeedFast(void);

uint16_t CLOCKS_getAclkFreqKhz(void);

uint16_t CLOCKS_getSmclkFreqKhz(void);

uint16_t CLOCKS_getMclkFreqKhz(void);

#endif /* SRC_HEADERS_APP_CLOCKS_H_ */
