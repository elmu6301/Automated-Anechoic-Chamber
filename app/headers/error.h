/*
 * error.h
 *
 *  Created on: Feb 8, 2021
 *      Author: jgamm
 */

#ifndef APP_HEADERS_ERROR_H_
#define APP_HEADERS_ERROR_H_

#include <stdint.h>

typedef struct
{
    char * file;
    char * expression;
    uint8_t file_len;
    uint8_t expression_len;
    uint16_t line;
} ERROR_AssertInfo_Struct;

ERROR_AssertInfo_Struct * ERROR_lastAssertInfo(void);

#define ASSERT(CONDITION) if(!(CONDITION)) _assert_failure(#CONDITION, __FILE__, __LINE__);

void _assert_failure(char * expression, char * file, uint16_t line);

#endif /* APP_HEADERS_ERROR_H_ */
