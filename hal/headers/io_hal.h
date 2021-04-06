/*
 * io_hal.h
 *
 *  Created on: Feb 13, 2021
 *      Author: jgamm
 */

#ifndef HAL_HEADERS_IO_HAL_H_
#define HAL_HEADERS_IO_HAL_H_

#include <stdint.h>
#include <stdbool.h>

#undef OUT
#undef DIR


typedef struct
{
    volatile const uint8_t IN;
    volatile const uint8_t RESERVED0;
    volatile uint8_t OUT;
    volatile const uint8_t RESERVED1;
    volatile uint8_t DIR;
    volatile const uint8_t RESERVED2;
    volatile uint8_t REN;
    volatile const uint8_t RESERVED3;
    volatile uint8_t DS;
    volatile const uint8_t RESERVED4;
    volatile uint8_t SEL;
    volatile const uint8_t RESERVED5[13];
    volatile uint8_t IES;
    volatile const uint8_t RESERVED6;
    volatile uint8_t IE;
    volatile const uint8_t RESERVED7;
    volatile uint8_t IFG;
    volatile const uint8_t RESERVED8;
} IO_Registers_Struct;

#define P1 ((IO_Registers_Struct *) 0x0200U)
#define P2 ((IO_Registers_Struct *) 0x0201U)
#define P3 ((IO_Registers_Struct *) 0x0220U)
#define P4 ((IO_Registers_Struct *) 0x0221U)
#define P5 ((IO_Registers_Struct *) 0x0240U)
#define P6 ((IO_Registers_Struct *) 0x0241U)
#define P7 ((IO_Registers_Struct *) 0x0260U)
#define P8 ((IO_Registers_Struct *) 0x0261U)
#define PJ ((IO_Registers_Struct *) 0x0320U)

#define IO_PIN0_SHIFT (0U)
#define IO_PIN1_SHIFT (1U)
#define IO_PIN2_SHIFT (2U)
#define IO_PIN3_SHIFT (3U)
#define IO_PIN4_SHIFT (4U)
#define IO_PIN5_SHIFT (5U)
#define IO_PIN6_SHIFT (6U)
#define IO_PIN7_SHIFT (7U)

#define IO_PIN0_MASK (1U)
#define IO_PIN1_MASK (1U)
#define IO_PIN2_MASK (1U)
#define IO_PIN3_MASK (1U)
#define IO_PIN4_MASK (1U)
#define IO_PIN5_MASK (1U)
#define IO_PIN6_MASK (1U)
#define IO_PIN7_MASK (1U)

#define IO_PIN0 (IO_PIN0_MASK<<IO_PIN0_SHIFT)
#define IO_PIN1 (IO_PIN1_MASK<<IO_PIN1_SHIFT)
#define IO_PIN2 (IO_PIN2_MASK<<IO_PIN2_SHIFT)
#define IO_PIN3 (IO_PIN3_MASK<<IO_PIN3_SHIFT)
#define IO_PIN4 (IO_PIN4_MASK<<IO_PIN4_SHIFT)
#define IO_PIN5 (IO_PIN5_MASK<<IO_PIN5_SHIFT)
#define IO_PIN6 (IO_PIN6_MASK<<IO_PIN6_SHIFT)
#define IO_PIN7 (IO_PIN7_MASK<<IO_PIN7_SHIFT)

#define IO_IES_RESET (0x00U)
#define IO_IE_RESET  (0x00U)
#define IO_IFG_RESET (0x00U)
#define IO_OUT_RESET (0x00U)
#define IO_DIR_RESET (0x00U)
#define IO_REN_RESET (0xFFU)
#define IO_DS_RESET  (0x00U)
#define IO_SEL_RESET (0x00U)

typedef enum
{
    ioOutLow = false,
    ioOutHigh = true
} IO_Out_Enum;
typedef enum
{
    ioDirInput = false,
    ioDirOutput = true
} IO_Dir_Enum;
typedef enum
{
    ioDsReduced = false,
    ioDsFull = true
} IO_Ds_Enum;
typedef enum
{
    ioSelIo = false,
    ioSelPeripheral = true
} IO_Sel_Enum;
typedef enum
{
    ioIesRising = false,
    ioIesFalling = true
} IO_Ies_Enum;

inline __attribute__ ((always_inline)) void IO_writePin(IO_Registers_Struct * Px, uint8_t pin, IO_Out_Enum val)
{
    Px->OUT &= ~(pin*(!val));
    Px->OUT |= val*pin;
}
inline __attribute__ ((always_inline)) IO_Out_Enum IO_readPin(IO_Registers_Struct * Px, uint8_t pin)
{
    return (IO_Out_Enum)((Px->IN&pin)!=0);
}
inline __attribute__ ((always_inline)) void IO_writePort(IO_Registers_Struct * Px, uint8_t vals)
{
    Px->OUT = vals;
}
inline __attribute__ ((always_inline)) uint8_t IO_readPort(IO_Registers_Struct * Px)
{
    return Px->IN;
}
inline __attribute__ ((always_inline)) uint8_t IO_popIfgPin(IO_Registers_Struct * Px, uint8_t pin)
{
    bool flag = (Px->IFG&pin) != 0;
    Px->IFG &= ~pin;
    return flag;
}
inline __attribute__ ((always_inline)) void IO_writeIePin(IO_Registers_Struct * Px, uint8_t pin, bool val)
{
    Px->IE &= ~(pin*(!val));
    Px->IE |= pin*val;
}
inline __attribute__ ((always_inline)) void IO_writeIesPin(IO_Registers_Struct * Px, uint8_t pin, IO_Ies_Enum val)
{
    Px->IES &= ~(pin*(!val));
    Px->IES |= pin*val;
}

void IO_reset(IO_Registers_Struct * Px);

typedef struct
{
    IO_Out_Enum initial_out;
    IO_Dir_Enum dir;
    bool ren;
    IO_Ds_Enum ds;
    IO_Sel_Enum sel;
    IO_Ies_Enum ies;
    bool ie;
} IO_PinConfig_Struct;
void IO_configurePin(IO_Registers_Struct * Px, uint8_t pin, IO_PinConfig_Struct * config);

#endif /* HAL_HEADERS_IO_HAL_H_ */
