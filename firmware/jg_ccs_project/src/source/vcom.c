/*
 * vcom.c
 *
 *  Created on: Oct 27, 2020
 *      Author: jgamm
 */

#include "vcom.h"
#include "io.h"
#include "app_assert.h"
#include "interrupts.h"
#include <stdbool.h>

#define TX_BUFFER_SIZE 64
#define RX_BUFFER_SIZE 64

static bool transmitting = false;
static uint8_t tx_buffer[TX_BUFFER_SIZE];
static uint8_t rx_buffer[RX_BUFFER_SIZE];
static uint8_t tx_push_index = 0;
static uint8_t tx_pop_index = 0;
static uint8_t rx_push_index = 0;
static uint8_t rx_pop_index = 0;
static bool * rx_flag = (bool *) 0;

void __attribute__ ((interrupt)) uart_event(void)
{
    if(transmitting && UART_checkTxInterrupt(UCA1))
    {
        ASSERT_temp(tx_push_index != tx_pop_index);
        UART_loadByte(UCA1, tx_buffer[tx_pop_index]);
        tx_pop_index = (tx_pop_index+1)&(TX_BUFFER_SIZE-1);
        if(tx_push_index == tx_pop_index)
        {
            transmitting = false;
            UART_configureTxInterrupt(UCA1, false);
        }
    }
    if(UART_checkRxInterrupt(UCA1))
    {
        rx_buffer[rx_push_index] = UART_readByte(UCA1);
        if(rx_buffer[rx_push_index] == '\n' && rx_flag != 0)
            *rx_flag = true;
        rx_push_index = (rx_push_index+1)&(RX_BUFFER_SIZE-1);
    }
}

void VCOM_initialize(VCOM_Init_Struct * settings, bool * _rx_flag)
{
    if(_rx_flag != 0)
        rx_flag = _rx_flag;
    IO_Configure_Struct txd_settings =
    {
     .direction = ioDirectionOutput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthFull,
     .function = ioFunctionAlt,
     .interrupts = ioInterruptsNone,
     .initial_output = true
    };
    IO_configurePin(ioPort4, 4, &txd_settings);

    IO_Configure_Struct rxd_settings =
    {
     .direction = ioDirectionInput,
     .resistor = ioResistorNone,
     .drive_strength = ioDriveStrengthDontcare,
     .function = ioFunctionAlt,
     .interrupts = ioInterruptsNone,
     .initial_output = true
    };
    IO_configurePin(ioPort4, 5, &rxd_settings);

    UART_Configuration_Struct uart_settings =
    {
     .parity = settings->parity,
     .order = settings->order,
     .data_bits = settings->data_bits,
     .stop_bits = settings->stop_bits,
     .clock_source = uartClkSrcSMCLK,
     .baud_rate = settings->baud_rate
    };
    UART_configure(UCA1, &uart_settings);
    UART_configureRxInterrupt(UCA1, true);

    INT_configureHandler(intSourceUSCI_A1, &uart_event);
}

void VCOM_transmitString(char * string, uint8_t n)
{
    for(; n>0; --n)
    {
        tx_buffer[tx_push_index] = *string;
        tx_push_index = (tx_push_index+1)&(TX_BUFFER_SIZE-1);
        ++string;
    }
    transmitting = true;
    UART_configureTxInterrupt(UCA1, true);
}

void VCOM_getString(char * dest, char end, uint8_t n)
{
    ASSERT_temp(VCOM_stringAvailable(end));
    ASSERT_temp(n >= VCOM_rxAvailable());
    for(; rx_buffer[rx_pop_index]!=end; rx_pop_index=(rx_pop_index+1)&(RX_BUFFER_SIZE-1))
    {
        *dest = rx_buffer[rx_pop_index];
        ++dest;
    }
    rx_pop_index = (rx_pop_index+1)&(RX_BUFFER_SIZE-1);
}

bool VCOM_isTransmitting(void)
{
    return transmitting;
}

uint16_t VCOM_rxAvailable(void)
{
    return rx_push_index > rx_pop_index? rx_push_index-rx_pop_index \
                : rx_push_index+(RX_BUFFER_SIZE-rx_pop_index);
}

bool VCOM_stringAvailable(char end)
{
    for(uint8_t i=rx_pop_index; i!=rx_push_index; i=(i+1)&(RX_BUFFER_SIZE-1))
        if(rx_buffer[i] == end)
            return true;
    return false;
}
