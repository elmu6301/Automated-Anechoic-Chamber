/*
 * io.h
 *
 *  Created on: Oct 7, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_IO_H_
#define SRC_HEADERS_IO_H_

// P1.3 is dead.

#include <stdint.h>
#include <stdbool.h>

typedef enum
{
    ioPort1 = 0,
    ioPort2 = 1,
    ioPort3 = 2,
    ioPort4 = 3,
    ioPort5 = 4,
    ioPort6 = 5,
    ioPort7 = 6,
    ioPort8 = 7,
    ioPortJ = 8
} IO_Port_Enum;

typedef enum
{
    ioDriveStrengthDontcare = 0,
    ioDriveStrengthReduced = 0,
    ioDriveStrengthFull = 1
} IO_DriveStrength_Enum;

typedef enum
{
    ioResistorNone = 2,
    ioResistorPulldown = 0,
    ioResistorPullup = 1
} IO_Resistor_Enum;


typedef enum
{
    ioInterruptsNone = 2,
    ioInterruptsRising = 0,
    ioInterruptsFalling = 1
} IO_Interrupts_Enum;

typedef enum
{
    ioDirectionInput = 0,
    ioDirectionOutput = 1
} IO_Direction_Enum;

typedef enum
{
    ioFunctionGpio = 0,
    ioFunctionAlt = 1
} IO_Function_Enum;

typedef struct
{
    IO_Direction_Enum direction;
    IO_Resistor_Enum resistor;
    IO_DriveStrength_Enum drive_strength;
    IO_Function_Enum function;
    IO_Interrupts_Enum interrupts;
    bool initial_output;
}IO_Configure_Struct;

void IO_disableAllPins(void);

void IO_disablePin(IO_Port_Enum port, uint8_t pin);

void IO_configurePin(IO_Port_Enum port, uint8_t pin, IO_Configure_Struct * settings);

void IO_writePin(IO_Port_Enum port, uint8_t pin, bool val);

bool IO_readPin(IO_Port_Enum port, uint8_t pin);

void IO_configureInterrupts(IO_Port_Enum port, uint8_t pin, IO_Interrupts_Enum interrupts);

void IO_clearIfg(IO_Port_Enum port, uint8_t pin);

#endif /* SRC_HEADERS_IO_H_ */
