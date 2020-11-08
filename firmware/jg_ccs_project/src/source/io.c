/*
 * io.c
 *
 *  Created on: Oct 7, 2020
 *      Author: jgamm
 */

#include "io.h"
#include "app_assert.h"

typedef struct
{
    const volatile uint8_t IN;
    const volatile uint8_t empty0;
    volatile       uint8_t OUT;
    const volatile uint8_t empty1;
    volatile       uint8_t DIR;
    const volatile uint8_t empty2;
    volatile       uint8_t RES;
    const volatile uint8_t empty3;
    volatile       uint8_t DS;
    const volatile uint8_t empty4;
    volatile       uint8_t SEL;
    const volatile uint8_t empty5[13];
    volatile       uint8_t IES;
    const volatile uint8_t empty6;
    volatile       uint8_t IEN;
    const volatile uint8_t empty7;
    volatile       uint8_t IFG;
    const volatile uint8_t empty8;
} _Io_Struct;

#define NUM_PORTS (9)
#define NUM_INT_PORTS (2)
#define PORT1 ((_Io_Struct *) 0x0200)
#define PORT2 ((_Io_Struct *) 0x0201)
#define PORT3 ((_Io_Struct *) 0x0220)
#define PORT4 ((_Io_Struct *) 0x0221)
#define PORT5 ((_Io_Struct *) 0x0240)
#define PORT6 ((_Io_Struct *) 0x0241)
#define PORT7 ((_Io_Struct *) 0x0260)
#define PORT8 ((_Io_Struct *) 0x0261)
#define PORTJ ((_Io_Struct *) 0x0320)

static _Io_Struct * ports[NUM_PORTS] = {PORT1, PORT2, PORT3, PORT4, PORT5, PORT6, PORT7, PORT8, PORTJ};

void IO_disableAllPins(void)
{
    // Reset fields common to all pins
    for(int i=0; i<NUM_PORTS; ++i)
    {
        ports[i]->OUT = 0xFF;
        ports[i]->DIR = 0xFF;
        ports[i]->RES = 0xFF;
        ports[i]->DS  = 0x00;
        ports[i]->SEL = 0x00;
    }

    // Reset interrupt fields for appropriate pins
    for(int i=0; i<NUM_INT_PORTS; ++i)
    {
        ports[i]->IES = 0x00;
        ports[i]->IEN = 0x00;
        ports[i]->IFG = 0x00;
    }
}

void IO_disablePin(IO_Port_Enum port, uint8_t pin)
{
    // Ensure that input is valid
    ASSERT_temp(0<=port && port<NUM_PORTS);
    ASSERT_temp(pin<=7);

    // Configure pin as active low output
    ports[port]->OUT &= ~(1<<pin);
    ports[port]->DIR |=   1<<pin;
    ports[port]->RES &= ~(1<<pin);
    ports[port]->DS  &= ~(1<<pin);
    ports[port]->SEL &= ~(1<<pin);
    ports[port]->IES &= ~((port<NUM_INT_PORTS)<<(pin));
    ports[port]->IEN &= ~((port<NUM_INT_PORTS)<<(pin));
    ports[port]->IFG &= ~((port<NUM_INT_PORTS)<<(pin));
}

void IO_configurePin(IO_Port_Enum port, uint8_t pin, IO_Configure_Struct * settings)
{
    // Ensure that input is valid
    ASSERT_temp(0<=port && port<NUM_PORTS);
    ASSERT_temp(pin<=7);

    // Clear all pin fields
    ports[port]->OUT &= ~(1<<pin);
    ports[port]->DIR &= ~(1<<pin);
    ports[port]->RES &= ~(1<<pin);
    ports[port]->DS  &= ~(1<<pin);
    ports[port]->SEL &= ~(1<<pin);
    ports[port]->IES &= ~((port<NUM_INT_PORTS)<<(pin));
    ports[port]->IEN &= ~((port<NUM_INT_PORTS)<<(pin));
    ports[port]->IFG &= ~((port<NUM_INT_PORTS)<<(pin));

    // Set appropriate pin fields
    ports[port]->OUT |= (settings->direction == ioDirectionOutput? settings->initial_output \
                           : settings->resistor != ioResistorNone? settings->resistor \
                           : 0)<<(pin);
    ports[port]->DIR |= (settings->direction)<<(pin);
    ports[port]->RES |= (settings->resistor != ioResistorNone)<<(pin);
    ports[port]->DS  |= (settings->drive_strength)<<(pin);
    ports[port]->SEL |= (settings->function)<<(pin);
    ports[port]->IES |= (settings->interrupts)<<(pin);
    ports[port]->IEN |= (settings->interrupts != ioInterruptsNone)<<(pin);
}

void IO_writePin(IO_Port_Enum port, uint8_t pin, bool val)
{
    // Ensure that input is valid
    ASSERT_temp(0<=port && port<NUM_PORTS);
    ASSERT_temp(pin<=7);
    ASSERT_temp(((ports[port]->DIR)&(1<<pin)) != 0);

    // Clear output if appropriate
    ports[port]->OUT &= ~((1<<pin)*(!val));

    // Set output if appropriate
    ports[port]->OUT |= (1<<pin)*val;
}

bool IO_readPin(IO_Port_Enum port, uint8_t pin)
{
    // Ensure that input is valid
    ASSERT_temp(0<=port && port<NUM_PORTS);
    ASSERT_temp(pin<=7);
    ASSERT_temp(((ports[port]->DIR)&(1<<pin)) == 0);

    // Return logical value of appropriate input
    return ((ports[port]->IN)&(1<<pin)) != 0;
}

void IO_configureInterrupts(IO_Port_Enum port, uint8_t pin, IO_Interrupts_Enum interrupts)
{
    switch(interrupts)
    {
    case ioInterruptsNone:
        ports[port]->IEN &= ~(1<<pin);
        break;
    case ioInterruptsRising:
        ports[port]->IEN |= (1<<pin);
        ports[port]->IES &= ~(1<<pin);
        break;
    case ioInterruptsFalling:
        ports[port]->IEN |= (1<<pin);
        ports[port]->IES |= (1<<pin);
        break;
    default:
        ASSERT_perm(false);
    }
}

void IO_clearIfg(IO_Port_Enum port, uint8_t pin)
{
    ports[port]->IFG &= ~(1<<pin);
}

