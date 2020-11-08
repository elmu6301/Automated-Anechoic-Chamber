/*
 * uart.c
 *
 *  Created on: Oct 7, 2020
 *      Author: jgamm
 */

#include "uart.h"
#include "app_assert.h"

typedef struct
{
    volatile uint8_t CTL1;
    volatile uint8_t CTL0;
    const volatile uint8_t empty0[4];
    volatile uint8_t BR0;
    volatile uint8_t BR1;
    volatile uint8_t MCTL;
    const volatile uint8_t empty1;
    volatile uint8_t STAT;
    const volatile uint8_t empty2;
    volatile uint8_t RXBUF;
    const volatile uint8_t empty3;
    volatile uint8_t TXBUF;
    const volatile uint8_t empty4;
    volatile uint8_t ABCTL;
    const volatile uint8_t empty5;
    const volatile uint8_t IRDA_registers[2];
    const volatile uint8_t empty6[8];
    volatile uint8_t IE;
    volatile uint8_t IFG;
    const volatile uint8_t IV;
} _usciaUart_Struct;

#define F_DIV128_CLK 31250
#define USCI_A0_BASE ((_usciaUart_Struct *) 0x05C0)
#define USCI_A1_BASE ((_usciaUart_Struct *) 0x0600)

static _usciaUart_Struct * uarts[2] = {USCI_A0_BASE, USCI_A1_BASE};

void UART_configure(UART_Base_Enum base, UART_Configuration_Struct * settings)
{
    uarts[base]->CTL1 |= 1<<0;
    uarts[base]->CTL0 = 0;
    uarts[base]->CTL1 &= 1<<0;
    uarts[base]->CTL0 |= (settings->stop_bits)<<3;
    uarts[base]->CTL0 |= (settings->data_bits)<<4;
    uarts[base]->CTL0 |= (settings->order)<<5;
    uarts[base]->CTL0 |= ((settings->parity)&((settings->parity)!=uartParityNone))<<6;
    uarts[base]->CTL0 |= ((settings->parity)!=uartParityNone)<<7;
    uarts[base]->CTL1 |= (settings->clock_source)<<6;
    switch(settings->baud_rate)
    {
    case uartBaudRate9600:
        uarts[base]->BR0 = 27;
        uarts[base]->BR1 = 0;
        uarts[base]->MCTL = 0;
        uarts[base]->MCTL |= 1<<0;
        uarts[base]->MCTL |= 0<<1;
        uarts[base]->MCTL |= 5<<4;
        break;
    case uartBaudRate115200:
        uarts[base]->BR0 = 2;
        uarts[base]->MCTL = 0;
        uarts[base]->MCTL |= 1<<0;
        uarts[base]->MCTL |= 6<<1;
        uarts[base]->MCTL |= 3<<4;
        break;
    default:
        ASSERT_perm(false);
    }
    uarts[base]->CTL1 &= ~(1<<0);
    uarts[base]->IE = 0;
}

void UART_loadByte(UART_Base_Enum base, uint8_t byte)
{
    uarts[base]->TXBUF = byte;
}

uint8_t UART_readByte(UART_Base_Enum base)
{
    return uarts[base]->RXBUF;
}

void UART_configureTxInterrupt(UART_Base_Enum base, bool enable)
{
    uarts[base]->IE &= ~((!enable)<<1);
    uarts[base]->IE |= enable<<1;
}

void UART_configureRxInterrupt(UART_Base_Enum base, bool enable)
{
    uarts[base]->IE &= ~(enable<<0);
    uarts[base]->IE |= (enable<<0);
}

bool UART_checkTxInterrupt(UART_Base_Enum base)
{
    return (uarts[base]->IFG & (1<<1)) != 0;
}

bool UART_checkRxInterrupt(UART_Base_Enum base)
{
    return (uarts[base]->IFG & (1<<0)) != 0;
}
