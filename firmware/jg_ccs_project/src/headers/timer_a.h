/*
 * timer_a.h
 *
 *  Created on: Oct 7, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_TIMER_A_H_
#define SRC_HEADERS_TIMER_A_H_

#include <stdbool.h>
#include <stdint.h>

typedef enum
{
    TA0 = 0,
    TA1 = 1,
    TA2 = 2
}TIMERA_Base_Enum;

typedef enum
{
    timeraClkSrcTAxCLK = 0x0000,
    timeraClkSrcACLK = 0x0001,
    timeraClkSrcSMCLK = 0x0002,
    timeraClkSrcINCLK = 0x0003
} TIMERA_ClkSrc_Enum;

typedef enum
{
    timeraClkDiv1 = 0x0000,
    timeraClkDiv2 = 0x0001,
    timeraClkDiv4 = 0x0002,
    timeraClkDiv8 = 0x0003
} TIMERA_ClkDiv_Enum;

typedef enum
{
    timeraModeStop = 0x0000,
    timeraModeUp = 0x0001,
    timeraModeCont = 0x0002,
    timeraModeUpdown = 0x0003
} TIMERA_Mode_Enum;

typedef enum
{
    timeraCcrCaptureModeNoCapture = 0x0000,
    timeraCcrCaptureModeRisingEdge = 0x0001,
    timerCcrCaptureModeFallingEdge = 0x0002,
    timerCcrCaptureModeBothEdges = 0x0003
} TIMERA_CaptureMode_Enum;

typedef enum
{
    timeraCcrCcInputCCIxA = 0x0000,
    timeraCcrCcInputCCIxB = 0x0001,
    timeraCcrCcInputGND = 0x0002,
    timeraCcrCcInputVCC = 0x0003
} TIMERA_CcrCcInput_Enum;

typedef enum
{
    timeraCcrCaptureSyncAsynchronous = 0x0000,
    timeraCcrCaptureSyncSynchronous = 0x0001
} TIMERA_CcrCaptureSync_Enum;

typedef enum
{
    timeraCcrCcModeCompare = 0x0000,
    timeraCcrCcModeCapture = 0x0001
} TIMERA_CcrCcMode_Enum;

typedef enum
{
    timeraCcrOutputModeOutput = 0x0000,
    timeraCcrOutputModeSet = 0x0001,
    timeraCcrOutputModeToggleReset = 0x0002,
    timeraCcrOutputModeSetReset = 0x0003,
    timeraCcrOutputModeToggle = 0x0004,
    timeraCcrOutputModeReset = 0x0005,
    timeraCcrOutputModeToggleSet = 0x0006,
    timeraCcrOutputModeResetSet = 0x0007
} TIMERA_CcrOutputMode_Enum;

typedef struct
{
    TIMERA_ClkSrc_Enum clock_source;
    TIMERA_ClkDiv_Enum clock_division;
    bool ien;
}TIMERA_Configure_Struct;

typedef struct
{
    TIMERA_CcrCcMode_Enum mode;
    TIMERA_CcrCcInput_Enum input;
    TIMERA_CaptureMode_Enum capture_mode;
    TIMERA_CcrCaptureSync_Enum capture_sync;
    TIMERA_CcrOutputMode_Enum output_mode;
    bool ien;
} TIMERA_ConfigureCcr_Struct;

void TIMERA_configure(TIMERA_Base_Enum tax, TIMERA_Configure_Struct * settings);

void TIMERA_configureCcr(TIMERA_Base_Enum tax, uint8_t ccrn, TIMERA_ConfigureCcr_Struct * settings);

void TIMERA_start(TIMERA_Base_Enum tax, TIMERA_Mode_Enum mode);

void TIMERA_stop(TIMERA_Base_Enum tax);

void TIMERA_setCount(TIMERA_Base_Enum tax, uint16_t val);

uint16_t TIMERA_getCount(TIMERA_Base_Enum tax);

void TIMERA_setCcr(TIMERA_Base_Enum tax, uint8_t ccrn, uint16_t val);

uint16_t TIMERA_getCcr(TIMERA_Base_Enum tax, uint8_t ccrn);

void TIMERA_configureInterrupts(TIMERA_Base_Enum tax, uint8_t ccrn, bool en);

#endif /* SRC_HEADERS_TIMER_A_H_ */
