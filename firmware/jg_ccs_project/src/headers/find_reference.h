/*
 * find_reference.h
 *
 *  Created on: Oct 31, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_FIND_REFERENCE_H_
#define SRC_HEADERS_FIND_REFERENCE_H_

#include <stdbool.h>
#include "io.h"

#define FR_ENDSWITCH_PORT ioPort1
#define FR_ENDSWITCH_PIN  4

void FR_initialize(void);

void FR_find(void);

bool FR_atReference(void);


#endif /* SRC_HEADERS_FIND_REFERENCE_H_ */
