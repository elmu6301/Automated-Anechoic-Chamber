/*
 * vcom.h
 *
 *  Created on: Oct 27, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_VCOM_H_
#define SRC_HEADERS_VCOM_H_

#include "uart.h"
#include <stdint.h>

typedef struct
{
    UART_Parity_Enum parity;
    UART_Order_Enum order;
    UART_DataBits_Enum data_bits;
    UART_StopBits_Enum stop_bits;
    UART_BaudRate_Enum baud_rate;
} VCOM_Init_Struct;

void VCOM_initialize(VCOM_Init_Struct * settings, bool * rx_flag);

void VCOM_transmitString(char * string, uint8_t n);

void VCOM_getString(char * dest, char end, uint8_t n);

bool VCOM_isTransmitting(void);

uint16_t VCOM_rxAvailable(void);

bool VCOM_stringAvailable(char end);

#endif /* SRC_HEADERS_VCOM_H_ */
