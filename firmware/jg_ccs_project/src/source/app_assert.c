/*
 * assert.c
 *
 *  Created on: Oct 3, 2020
 *      Author: jgamm
 */

#include "app_assert.h"

void _assert_failure(char * _expression, char * _file, int _line)
{
    volatile char * expression = _expression;
    volatile char * file = _file;
    volatile int line = _line;
    (void) expression;
    (void) file;
    (void) line;
    // disable interrupts
    // enable LED
    while(1);
}
