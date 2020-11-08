/*
 * interrupts.h
 *
 *  Created on: Oct 25, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_INTERRUPTS_H_
#define SRC_HEADERS_INTERRUPTS_H_

#include <stdbool.h>

typedef enum
{
    intSourceRTC_A = 22,
    intSourceIOP2 = 21,
    intSourceTA2_CCR1 = 20,
    intSourceTA2_CCR2 = 20,
    intSourceTA2_IFG = 20,
    intSourceTA2_CCR0 = 19,
    intSourceUSCI_B1 = 18,
    intSourceUSCI_A1 = 17,
    intSourceIOP1 = 16,
    intSourceTA1CCR1 = 15,
    intSourceTA1CCR2 = 15,
    intSourceTA1CCR3 = 15,
    intSourceTA1CCR4 = 15,
    intSourceTA1_IFG = 15,
    intSourceTA1_CCR0 = 14,
    intSourceDMA = 13,
    intSourceUSB_UBM = 12,
    intSourceTA0_CCR1 = 11,
    intSourceTA0_CCR2 = 11,
    intSourceTA0_CCR3 = 11,
    intSourceTA0_CCR4 = 11,
    intSourceTA0_IFG = 11,
    intSourceTA0_CCR0 = 10,
    intSourceADC12_A = 9,
    intSourceUSCI_B0 = 8,
    intSourceUSCI_A0 = 7,
    intSourceWDTA = 6,
    intSourceTB0_CCR1 = 5,
    intSourceTB0_CCR2 = 5,
    intSourceTB0_CCR3 = 5,
    intSourceTB0_CCR4 = 5,
    intSourceTB0_CCR5 = 5,
    intSourceTB0_CCR6 = 5,
    intSourceTB0_IFG = 5,
    intSourceTB0_CCR0 = 4,
    intSourceCOMP_B = 3,
    intSourceUserNMI = 2,
    intSourceSystemNMI = 1,
    intSourceSystemReset = 0
} INT_Sources_Enum;

void INT_initialize(void);

void INT_configureGie(bool enable);

void INT_addBlock(void);

void INT_removeBlock(void);

void INT_configureHandler(INT_Sources_Enum source, void * handler);

void * INT_getHandler(INT_Sources_Enum source);

void INT_defaultHandler(void);

#endif /* SRC_HEADERS_INTERRUPTS_H_ */
