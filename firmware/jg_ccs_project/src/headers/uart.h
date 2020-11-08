/*
 * uart.h
 *
 *  Created on: Oct 7, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_UART_H_
#define SRC_HEADERS_UART_H_

#include <stdint.h>
#include <stdbool.h>

typedef enum
{
    UCA0 = 0,
    UCA1 = 1
} UART_Base_Enum;

typedef enum
{
    uartParityNone = 2,
    uartParityOdd = 0,
    uartParityEven = 1
} UART_Parity_Enum;

typedef enum
{
    uartLsbFirst = 0,
    uartMsbFirst = 1
} UART_Order_Enum;

typedef enum
{
    uartDataBits8 = 0,
    uartDataBits7 = 1
} UART_DataBits_Enum;

typedef enum
{
    uartStopBits1 = 0,
    uartStopBits2 = 1
} UART_StopBits_Enum;

typedef enum
{
    uartClkSrcUCAxCLK = 0,
    uartClkSrcACLK = 1,
    uartClkSrcSMCLK = 2
} UART_ClkSrc_Enum;

typedef enum
{
    uartBaudRate9600,
    uartBaudRate115200
} UART_BaudRate_Enum;

typedef struct
{
    UART_Parity_Enum parity;
    UART_Order_Enum order;
    UART_DataBits_Enum data_bits;
    UART_StopBits_Enum stop_bits;
    UART_ClkSrc_Enum clock_source;
    uint16_t baud_rate;
} UART_Configuration_Struct;

void UART_configure(UART_Base_Enum base, UART_Configuration_Struct * settings);

void UART_loadByte(UART_Base_Enum base, uint8_t byte);

uint8_t UART_readByte(UART_Base_Enum base);

void UART_configureTxInterrupt(UART_Base_Enum base, bool enable);

void UART_configureRxInterrupt(UART_Base_Enum base, bool enable);

bool UART_checkTxInterrupt(UART_Base_Enum base);

bool UART_checkRxInterrupt(UART_Base_Enum base);

#endif /* SRC_HEADERS_UART_H_ */
