/*
 * ucs.h
 *
 *  Created on: Oct 28, 2020
 *      Author: jgamm
 */

#ifndef SRC_HEADERS_UCS_H_
#define SRC_HEADERS_UCS_H_

#include <stdbool.h>
#include <stdint.h>

#define UCS_XT2_PRESENT true
#define UCS_XT2_FREQ_MHZ 4
#define UCS_XT2_BYPASS 0 // external crystal
#define UCS_XT1_PRESENT false
#define UCS_XT1_FREQ_KHZ
#define UCS_XT1_BYPASS
#define UCS_VLO_FREQ_HZ 10000
#define UCS_REFO_FREQ_HZ 32768

typedef enum
{
    ucsClockSelXT1CLK = 0,
    ucsClockSelVLOCLK = 1,
    ucsClockSelREFOCLK = 2,
    ucsClockSelDCOCLK = 3,
    ucsClockSelDCOCLKDIV = 4,
    ucsClockSelXT2CLK
} UCS_ClockSel_Enum;

typedef enum
{
    ucsDiv1 = 0,
    ucsDiv2 = 1,
    ucsDiv4 = 2,
    ucsDiv8 = 3,
    ucsDiv16 = 4,
    ucsDiv32 = 5
} UCS_Div_Enum;

typedef enum
{
    ucsDcoRange70to1700kHz = 0,
    ucsDcoRange150to3450kHz = 1,
    ucsDcoRange320to7380kHz = 2,
    ucsDcoRange640to14000kHz = 3,
    ucsDcoRange1300to28200kHz = 4,
    ucsDcoRange2500to54100kHz = 5,
    ucsDcoRange4600to88000kHz = 6,
    ucsDcoRange8500to135000kHz = 7
} UCS_DcoRange_Enum;

typedef struct
{
    UCS_ClockSel_Enum fll_source;
    uint8_t fll_source_div;
    uint8_t fll_div;
    uint16_t fll_mult;
    UCS_DcoRange_Enum range;
} UCS_DcoConfig_Struct;

void UCS_initialize(void);

void UCS_configureACLK(UCS_ClockSel_Enum source, UCS_Div_Enum div);

void UCS_configureSMCLK(UCS_ClockSel_Enum source, UCS_Div_Enum div);

void UCS_configureMCLK(UCS_ClockSel_Enum source, UCS_Div_Enum div);

void UCS_configureDco(UCS_DcoConfig_Struct * settings);

#endif /* SRC_HEADERS_UCS_H_ */
