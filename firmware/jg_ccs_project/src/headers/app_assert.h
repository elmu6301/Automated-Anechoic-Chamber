/*
 * assert.h
 *
 *  Created on: Oct 3, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_APP_ASSERT_H_
#define SRC_HEADERS_APP_ASSERT_H_

#include "global_settings.h"
#include <stdbool.h>

void _assert_failure(char * expression, char * file, int line);

#define ASSERT_perm(condition) \
    if((condition) != 0); \
    else _assert_failure(#condition, __FILE__, __LINE__)

#if ASSERT_DEBUG == 1
#define ASSERT_temp(condition) ASSERT_perm(condition)
#else
#define ASSERT_temp(condition)
#endif


#endif /* SRC_HEADERS_APP_ASSERT_H_ */
