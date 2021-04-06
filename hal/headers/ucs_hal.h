/*
 * ucs_hal.h
 *
 *  Created on: Feb 8, 2021
 *      Author: jgamm
 */

#ifndef HAL_HEADERS_UCS_HAL_H_
#define HAL_HEADERS_UCS_HAL_H_

#include <stdint.h>
#include <stdbool.h>

// Unified Clock System register layout
typedef struct
{
    volatile uint16_t CTL0;
    volatile uint16_t CTL1;
    volatile uint16_t CTL2;
    volatile uint16_t CTL3;
    volatile uint16_t CTL4;
    volatile uint16_t CTL5;
    volatile uint16_t CTL6;
    volatile uint16_t CTL7;
    volatile uint16_t CTL8;
    volatile uint16_t CTL9;
} UCS_Registers_Struct;

// Unified Clock System base addresses
#define UCS0 ((UCS_Registers_Struct *) 0x0160U)

// Unified Clock System Control 0 (UCSCTL0)
#define UCS_CTL0_RESET (0x0000U)

#define UCS_CTL0_MOD_SHIFT (3U)
#define UCS_CTL0_DCO_SHIFT (8U)

#define UCS_CTL0_MOD_MASK (0x1FU)
#define UCS_CTL0_DCO_MASK (0x1FU)

#define UCS_CTL0_MOD (UCS_CTL0_MOD_MASK<<UCS_CTL0_MOD_SHIFT)
#define UCS_CTL0_DCO (UCS_CTL0_DCO_MASK<<UCS_CTL0_DCO_SHIFT)

// Unified Clock System Control 1 (UCSCTL1)
#define UCS_CTL1_RESET (0x0020U)

#define UCS_CTL1_DISMOD_SHIFT (0U)
#define UCS_CTL1_DCORSEL_SHIFT (4U)

#define UCS_CTL1_DISMOD_MASK (1U)
#define UCS_CTL1_DCORSEL_MASK (7U)

#define UCS_CTL1_DISMOD (UCS_CTL1_DISMOD_MASK<<UCS_CTL1_DISMOD_SHIFT)
#define UCS_CTL1_DCORSEL (UCS_CTL1_DCORSEL_MASK<<UCS_CTL1_DCORSEL_SHIFT)

// Unified Clock System Control 2 (UCSCTL2)
#define UCS_CTL2_RESET (0x101FU)

#define UCS_CTL2_FLLN_SHIFT (0U)
#define UCS_CTL2_FLLD_SHIFT (12U)

#define UCS_CTL2_FLLN_MASK (0x3FFU)
#define UCS_CTL2_FLLD_MASK (0x7U)

#define UCS_CTL2_FLLN (UCS_CTL2_FLLN_MASK<<UCS_CTL2_FLLN_SHIFT)
#define UCS_CTL2_FLLD (UCS_CTL2_FLLD_MASK<<UCS_CTL2_FLLD_SHIFT)

typedef enum
{
    ucsCtl2Flld1 = 0<<UCS_CTL2_FLLD_SHIFT,
    ucsCtl2Flld2 = 1<<UCS_CTL2_FLLD_SHIFT,
    ucsCtl2Flld4 = 2<<UCS_CTL2_FLLD_SHIFT,
    ucsCtl2Flld8 = 3<<UCS_CTL2_FLLD_SHIFT,
    ucsCtl2Flld16 = 4<<UCS_CTL2_FLLD_SHIFT,
    ucsCtl2Flld32 = 5<<UCS_CTL2_FLLD_SHIFT
} UCS_Ctl2Flld_Enum;

// Unified Clock System Control 3 (UCSCTL3)
#define UCS_CTL3_RESET (0x0000U)

#define UCS_CTL3_FLLREFDIV_SHIFT (0U)
#define UCS_CTL3_SELREF_SHIFT (4U)

#define UCS_CTL3_FLLREFDIV_MASK (7U)
#define UCS_CTL3_SELREF_MASK (7U)

#define UCS_CTL3_FLLREFDIV (UCS_CTL3_FLLREFDIV_MASK<<UCS_CTL3_FLLREFDIV_SHIFT)
#define UCS_CTL3_SELREF (UCS_CTL3_SELREF_MASK<<UCS_CTL3_SELREF_SHIFT)

typedef enum
{
    ucsCtl3Fllrefdiv1 = 0<<UCS_CTL3_FLLREFDIV_SHIFT,
    ucsCtl3Fllrefdiv2 = 1<<UCS_CTL3_FLLREFDIV_SHIFT,
    ucsCtl3Fllrefdiv4 = 2<<UCS_CTL3_FLLREFDIV_SHIFT,
    ucsCtl3Fllrefdiv8 = 3<<UCS_CTL3_FLLREFDIV_SHIFT,
    ucsCtl3Fllrefdiv12 = 4<<UCS_CTL3_FLLREFDIV_SHIFT,
    ucsCtl3Fllrefdiv16 = 5<<UCS_CTL3_FLLREFDIV_SHIFT
} UCS_Ctl3Fllrefdiv_Enum;
typedef enum
{
    ucsCtl3SelrefXT1CLK = 0<<UCS_CTL3_SELREF_SHIFT,
    ucsCtl3SelrefREFOCLK = 2<<UCS_CTL3_SELREF_SHIFT,
    ucsCtl3SelrefXT2CLK = 5<<UCS_CTL3_SELREF_SHIFT
} UCS_Ctl3Selref_Enum;

// Unified Clock System Control 4 (UCSCTL4)
#define UCS_CTL4_RESET (0x0044U)

#define UCS_CTL4_SELM_SHIFT (0U)
#define UCS_CTL4_SELS_SHIFT (4U)
#define UCS_CTL4_SELA_SHIFT (8U)

#define UCS_CTL4_SELM_MASK (7U)
#define UCS_CTL4_SELS_MASK (7U)
#define UCS_CTL4_SELA_MASK (7U)

#define UCS_CTL4_SELM (UCS_CTL4_SELM_MASK<<UCS_CTL4_SELM_SHIFT)
#define UCS_CTL4_SELS (UCS_CTL4_SELS_MASK<<UCS_CTL4_SELS_SHIFT)
#define UCS_CTL4_SELA (UCS_CTL4_SELA_MASK<<UCS_CTL4_SELA_SHIFT)

typedef enum
{
    ucsCtl4SelmXT1CLK = 0<<UCS_CTL4_SELM_SHIFT,
    ucsCtl4SelmVLOCLK = 1<<UCS_CTL4_SELM_SHIFT,
    ucsCtl4SelmREFOCLK = 2<<UCS_CTL4_SELM_SHIFT,
    ucsCtl4SelmDCOCLK = 3<<UCS_CTL4_SELM_SHIFT,
    ucsCtl4SelmDCOCLKDIV = 4<<UCS_CTL4_SELM_SHIFT,
    ucsCtl4SelmXT2CLK = 5<<UCS_CTL4_SELM_SHIFT
} UCS_Ctl4Selm_Enum;
typedef enum
{
    ucsCtl4SelsXT1CLK = 0<<UCS_CTL4_SELS_SHIFT,
    ucsCtl4SelsVLOCLK = 1<<UCS_CTL4_SELS_SHIFT,
    ucsCtl4SelsREFOCLK = 2<<UCS_CTL4_SELS_SHIFT,
    ucsCtl4SelsDCOCLK = 3<<UCS_CTL4_SELS_SHIFT,
    ucsCtl4SelsDCOCLKDIV = 4<<UCS_CTL4_SELS_SHIFT,
    ucsCtl4SelsXT2CLK = 5<<UCS_CTL4_SELS_SHIFT
} UCS_Ctl4Sels_Enum;
typedef enum
{
    ucsCtl4SelaXT1CLK = 0<<UCS_CTL4_SELA_SHIFT,
    ucsCtl4SelaVLOCLK = 1<<UCS_CTL4_SELA_SHIFT,
    ucsCtl4SelaREFOCLK = 2<<UCS_CTL4_SELA_SHIFT,
    ucsCtl4SelaDCOCLK = 3<<UCS_CTL4_SELA_SHIFT,
    ucsCtl4SelaDCOCLKDIV = 4<<UCS_CTL4_SELA_SHIFT,
    ucsCtl4SelaXT2CLK = 5<<UCS_CTL4_SELA_SHIFT
} UCS_Ctl4Sela_Enum;

// Unified Clock System Control 5 (UCSCTL5)
#define UCS_CTL5_RESET (0x0000U)

#define UCS_CTL5_DIVM_SHIFT (0U)
#define UCS_CTL5_DIVS_SHIFT (4U)
#define UCS_CTL5_DIVA_SHIFT (8U)
#define UCS_CTL5_DIVPA_SHIFT (12U)

#define UCS_CTL5_DIVM_MASK (7U)
#define UCS_CTL5_DIVS_MASK (7U)
#define UCS_CTL5_DIVA_MASK (7U)
#define UCS_CTL5_DIVPA_MASK (7U)

#define UCS_CTL5_DIVM (UCS_CTL5_DIVM_MASK<<UCS_CTL5_DIVM_SHIFT)
#define UCS_CTL5_DIVS (UCS_CTL5_DIVS_MASK<<UCS_CTL5_DIVS_SHIFT)
#define UCS_CTL5_DIVA (UCS_CTL5_DIVA_MASK<<UCS_CTL5_DIVA_SHIFT)
#define UCS_CTL5_DIVPA (UCS_CTL5_DIVPA_MASK<<UCS_CTL5_DIVPA_SHIFT)

typedef enum
{
    ucsCtl5Divm1 = 0<<UCS_CTL5_DIVM_SHIFT,
    ucsCtl5Divm2 = 1<<UCS_CTL5_DIVM_SHIFT,
    ucsCtl5Divm4 = 2<<UCS_CTL5_DIVM_SHIFT,
    ucsCtl5Divm8 = 3<<UCS_CTL5_DIVM_SHIFT,
    ucsCtl5Divm16 = 4<<UCS_CTL5_DIVM_SHIFT,
    ucsCtl5Divm32 = 5<<UCS_CTL5_DIVM_SHIFT
} UCS_Ctl5Divm_Enum;
typedef enum
{
    ucsCtl5Divs1 = 0<<UCS_CTL5_DIVS_SHIFT,
    ucsCtl5Divs2 = 1<<UCS_CTL5_DIVS_SHIFT,
    ucsCtl5Divs4 = 2<<UCS_CTL5_DIVS_SHIFT,
    ucsCtl5Divs8 = 3<<UCS_CTL5_DIVS_SHIFT,
    ucsCtl5Divs16 = 4<<UCS_CTL5_DIVS_SHIFT,
    ucsCtl5Divs32 = 5<<UCS_CTL5_DIVS_SHIFT
} UCS_Ctl5Divs_Enum;
typedef enum
{
    ucsCtl5Diva1 = 0<<UCS_CTL5_DIVA_SHIFT,
    ucsCtl5Diva2 = 1<<UCS_CTL5_DIVA_SHIFT,
    ucsCtl5Diva4 = 2<<UCS_CTL5_DIVA_SHIFT,
    ucsCtl5Diva8 = 3<<UCS_CTL5_DIVA_SHIFT,
    ucsCtl5Diva16 = 4<<UCS_CTL5_DIVA_SHIFT,
    ucsCtl5Diva32 = 5<<UCS_CTL5_DIVA_SHIFT
} UCS_Ctl5Diva_Enum;
typedef enum
{
    ucsCtl5Divpa1 = 0<<UCS_CTL5_DIVPA_SHIFT,
    ucsCtl5Divpa2 = 1<<UCS_CTL5_DIVPA_SHIFT,
    ucsCtl5Divpa4 = 2<<UCS_CTL5_DIVPA_SHIFT,
    ucsCtl5Divpa8 = 3<<UCS_CTL5_DIVPA_SHIFT,
    ucsCtl5Divpa16 = 4<<UCS_CTL5_DIVPA_SHIFT,
    ucsCtl5Divpa32 = 5<<UCS_CTL5_DIVPA_SHIFT
} UCS_Ctl5Divpa_Enum;

// Unified Clock System Control 6 (UCSCTL6)
#define UCS_CTL6_RESET (0xC1CDU)

#define UCS_CTL6_XT1OFF_SHIFT (0U)
#define UCS_CTL6_SMCLKOFF_SHIFT (1U)
#define UCS_CTL6_XCAP_SHIFT (2U)
#define UCS_CTL6_XT1BYPASS_SHIFT (4U)
#define UCS_CTL6_XTS_SHIFT (5U)
#define UCS_CTL6_XT1DRIVE_SHIFT (6U)
#define UCS_CTL6_XT2OFF_SHIFT (8U)
#define UCS_CTL6_XT2BYPASS_SHIFT (12U)
#define UCS_CTL6_XT2DRIVE_SHIFT (14U)

#define UCS_CTL6_XT1OFF_MASK (1U)
#define UCS_CTL6_SMCLKOFF_MASK (1U)
#define UCS_CTL6_XCAP_MASK (3U)
#define UCS_CTL6_XT1BYPASS_MASK (1U)
#define UCS_CTL6_XTS_MASK (1U)
#define UCS_CTL6_XT1DRIVE_MASK (3U)
#define UCS_CTL6_XT2OFF_MASK (1U)
#define UCS_CTL6_XT2BYPASS_MASK (1U)
#define UCS_CTL6_XT2DRIVE_MASK (3U)

#define UCS_CTL6_XT1OFF (UCS_CTL6_XT1OFF_MASK<<UCS_CTL6_XT1OFF_SHIFT)
#define UCS_CTL6_SMCLKOFF (UCS_CTL6_SMCLKOFF_MASK<<UCS_CTL6_SMCLKOFF_SHIFT)
#define UCS_CTL6_XCAP (UCS_CTL6_XCAP_MASK<<UCS_CTL6_XCAP_SHIFT)
#define UCS_CTL6_XT1BYPASS (UCS_CTL6_XT1BYPASS_MASK<<UCS_CTL6_XT1BYPASS_SHIFT)
#define UCS_CTL6_XTS (UTS_CTL6_XTS_MASK<<UTS_CTL6_XTS_SHIFT)
#define UCS_CTL6_XT1DRIVE (UCS_CTL6_XT1DRIVE_MASK<<UCS_CTL6_XT1DRIVE_SHIFT)
#define UCS_CTL6_XT2OFF (UCS_CTL6_XT2OFF_MASK<<UCS_CTL6_XT2OFF_SHIFT)
#define UCS_CTL6_XT2BYPASS (UCS_CTL6_XT2BYPASS_MASK<<UCS_CTL6_XT2BYPASS_SHIFT)
#define UCS_CTL6_XT2DRIVE (UCS_CTL6_XT2DRIVE_MASK<<UCS_CTL6_XT2DRIVE_SHIFT)

typedef enum
{
    ucsCtl6Xt1drive0 = 0<<UCS_CTL6_XT1DRIVE_SHIFT,
    ucsCtl6Xtl1drive1 = 1<<UCS_CTL6_XT1DRIVE_SHIFT,
    ucsCtl6Xtl1drive2 = 2<<UCS_CTL6_XT1DRIVE_SHIFT,
    ucsCtl6Xtl1drive3 = 3<<UCS_CTL6_XT1DRIVE_SHIFT
} UCS_Ctl6Xtl1drive_Enum;
typedef enum
{
    ucsCtl6Xt2drive0 = 0<<UCS_CTL6_XT2DRIVE_SHIFT,
    ucsCtl6Xt2drive1 = 1<<UCS_CTL6_XT2DRIVE_SHIFT,
    ucsCtl6Xt2drive2 = 2<<UCS_CTL6_XT2DRIVE_SHIFT,
    ucsCtl6Xt2drive3 = 3<<UCS_CTL6_XT2DRIVE_SHIFT
} UCS_Ctl6Xt2drive_Enum;

// Unified Clock System Control 7 (UCSCTL7)
#define UCS_CTL7_RESET (0x0703U)

#define UCS_CTL7_DCOFFG_SHIFT (0U)
#define UCS_CTL7_XT1LFOFFG_SHIFT (1U)
#define UCS_CTL7_XT1HFOFFG_SHIFT (2U)
#define UCS_CTL7_XT2OFFG_SHIFT (3U)

#define UCS_CTL7_DCOFFG_MASK (1U)
#define UCS_CTL7_XT1LFOFFG_MASK (1U)
#define UCS_CTL7_XT1HFOFFG_MASK (1U)
#define UCS_CTL7_XT2OFFG_MASK (1U)

#define UCS_CTL7_DCOFFG (UCS_CTL7_DCOFFG_MASK<<UCS_CTL7_DCOFFG_SHIFT)
#define UCS_CTL7_XT1LFOFFG (UCS_CTL7_XT1LFOFFG_MASK<<UCS_CTL7_XT1LFOFFG_SHIFT)
#define UCS_CTL7_XT1HFOFFG (UCS_CTL7_XT1HFOFFG_MASK<<UCS_CTL7_XT1HFOFFG_SHIFT)
#define UCS_CTL7_XT2OFFG (UCS_CTL7_XT2OFFG_MASK<<UCS_CTL7_XTO2FFG_SHIFT)

// Unified Clock System Control 8 (UCSCTL8)
#define UCS_CTL8_RESET (0x0707U)

#define UCS_CTL8_ACLKREQEN_SHIFT (0U)
#define UCS_CTL8_MCLKREQEN_SHIFT (1U)
#define UCS_CTL8_SMCLKREQEN_SHIFT (2U)
#define UCS_CTL8_MODOSCREQEN_SHIFT (3U)

#define UCS_CTL8_ACLKREQEN_MASK (1U)
#define UCS_CTL8_MCLKREQEN_MASK (1U)
#define UCS_CTL8_SMCLKREQEN_MASK (1U)
#define UCS_CTL8_MODOSCREQEN_MASK (1U)

#define UCS_CTL8_ACLKREQEN (UCS_ACLKREQEN_MASK<<UCS_ACLKREQEN_SHIFT)
#define UCS_CTL8_MCLKREQEN (UCS_CTL8_MCLKREQEN_MASK<<UCS_CTL8_MCLKREQEN_SHIFT)
#define UCS_CTL8_SMCLKREQEN (UCS_CTL8_SMCLKREQEN_MASK<<UCS_CTL8_SMCLKREQEN_SHIFT)
#define UCS_CTL8_MODOSCREQEN (UCS_CTL8_MODOSCREQEN_MASK<<UCS_CTL8_MODOSCREQEN_SHIFT)

// Unified Clock System Control 9 (UCSCTL9)
#define UCS_CTL9_RESET (0x0000U)

#define UCS_CTL9_XT1BYPASSLV_SHIFT (0U)
#define UCS_CTL9_XT2BYPASSLV_SHIFT (1U)

#define UCS_CTL9_XT1BYPASSLF_MASK (1U)
#define UCS_CTL9_XT2BYPASSLV_MASK (1U)

#define UCS_CTL9_XT1BYPASSLF (UCS_CTL9_XT1BYPASSLF_MASK<<UCS_CTL9_XT1BYPASSLF_SHIFT)
#define UCS_CTL9_XT1BYPASSLV (UCS_CTL9_XT1BYPASSLV_MASK<<UCS_CTL9_XT1BYPASSLV_SHIFT)

// Unified Clock System control functions
typedef struct
{
    bool dismod;
    uint8_t dcorsel;
    uint16_t flln;
    UCS_Ctl2Flld_Enum flld;
    UCS_Ctl3Fllrefdiv_Enum fllrefdiv;
    UCS_Ctl3Selref_Enum selref;
} UCS_DcoConfig_Struct;
typedef struct
{
    UCS_Ctl4Selm_Enum selm;
    UCS_Ctl5Divm_Enum divm;
    bool mclkreqen;
} UCS_MclkConfig_Struct;
typedef struct
{
    UCS_Ctl4Sels_Enum sels;
    UCS_Ctl5Divs_Enum divs;
    bool smclkreqen;
} UCS_SmclkConfig_Struct;
typedef struct
{
    UCS_Ctl4Sela_Enum sela;
    UCS_Ctl5Diva_Enum diva;
    UCS_Ctl5Divpa_Enum divpa;
    bool aclkreqen;
} UCS_AclkConfig_Struct;

void UCS_reset(UCS_Registers_Struct * UCS);

void UCS_configureDco(UCS_Registers_Struct * UCS, UCS_DcoConfig_Struct * config);

void UCS_configureMclk(UCS_Registers_Struct * UCS, UCS_MclkConfig_Struct * config);

void UCS_configureSmclk(UCS_Registers_Struct * UCS, UCS_SmclkConfig_Struct * config);

void UCS_configureAclk(UCS_Registers_Struct * UCS, UCS_AclkConfig_Struct * config);

#endif /* HAL_HEADERS_UCS_HAL_H_ */
