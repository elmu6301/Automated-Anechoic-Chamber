/*
 * check_alignment.h
 *
 *  Created on: Mar 2, 2021
 *      Author: jgamm
 */

#ifndef APP_HEADERS_CHECK_ALIGNMENT_H_
#define APP_HEADERS_CHECK_ALIGNMENT_H_

#include <stdint.h>
#include <stdbool.h>
#include "hal.h"

void CA_init(void);

void CA_writeLaser(bool state, void (*handler)(void *, bool), void * handler_args);

void CA_measureSensor(void (*handler)(uint16_t, void *), void * handler_args);

bool CA_idProbe(void);

#endif /* APP_HEADERS_CHECK_ALIGNMENT_H_ */
