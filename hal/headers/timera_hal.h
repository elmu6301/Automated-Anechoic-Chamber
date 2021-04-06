/*
 * timera_hal.h
 *
 *  Created on: Feb 20, 2021
 *      Author: jgamm
 */

#ifndef HAL_HEADERS_TIMERA_HAL_H_
#define HAL_HEADERS_TIMERA_HAL_H_

#include <stdint.h>
#include <stdbool.h>

#define TA_CCTL_NUMBER (7U)
#define TA_CCR_NUMBER  (7U)

typedef struct
{
    volatile uint16_t CTL;
    volatile uint16_t CCTL[TA_CCTL_NUMBER];
    volatile uint16_t R;
    volatile uint16_t CCR[TA_CCR_NUMBER];
    volatile uint16_t EX0;
    volatile uint8_t  RESERVED0[12U];
    volatile const uint16_t IV;
} TA_Registers_Struct;

#define TA0 ((TA_Registers_Struct *) 0x0340U)
#define TA1 ((TA_Registers_Struct *) 0x0380U)
#define TA2 ((TA_Registers_Struct *) 0x0400U)

#define TA_CTL_RESET (0x0000U)

#define TA_CTL_TAIFG_SHIFT  (0U)
#define TA_CTL_TAIE_SHIFT   (1U)
#define TA_CTL_TACLR_SHIFT  (2U)
#define TA_CTL_MC_SHIFT     (4U)
#define TA_CTL_ID_SHIFT     (6U)
#define TA_CTL_TASSEL_SHIFT (8U)

#define TA_CTL_TAIFG_MASK  (1U)
#define TA_CTL_TAIE_MASK   (1U)
#define TA_CTL_TACLR_MASK  (1U)
#define TA_CTL_MC_MASK     (3U)
#define TA_CTL_ID_MASK     (3U)
#define TA_CTL_TASSEL_MASK (3U)

#define TA_CTL_TAIFG  (TA_CTL_TAIFG_MASK<<TA_CTL_TAIFG_SHIFT)
#define TA_CTL_TAIE   (TA_CTL_TAIE_MASK<<TA_CTL_TAIE_SHIFT)
#define TA_CTL_TACLR  (TA_CTL_TACLR_MASK<<TA_CTL_TACLR_SHIFT)
#define TA_CTL_MC     (TA_CTL_MC_MASK<<TA_CTL_MC_SHIFT)
#define TA_CTL_ID     (TA_CTL_ID_MASK<<TA_CTL_ID_SHIFT)
#define TA_CTL_TASSEL (TA_CTL_TASSEL_MASK<<TA_CTL_TASSEL_SHIFT)

typedef enum
{
    taCtlMcStop       = 0U<<TA_CTL_MC_SHIFT,
    taCtlMcUp         = 1U<<TA_CTL_MC_SHIFT,
    taCtlMcContinuous = 2U<<TA_CTL_MC_SHIFT,
    taCtlMcUpdown     = 3U<<TA_CTL_MC_SHIFT
} TA_CtlMc_Enum;
typedef enum
{
    taCtlId1 = 0U<<TA_CTL_ID_SHIFT,
    taCtlId2 = 1U<<TA_CTL_ID_SHIFT,
    taCtlId4 = 2U<<TA_CTL_ID_SHIFT,
    taCtlId8 = 3U<<TA_CTL_ID_SHIFT
} TA_CtlId_Enum;
typedef enum
{
    taCtlTasselTAxCLK = 0U<<TA_CTL_TASSEL_SHIFT,
    taCtlTasselACLK   = 1U<<TA_CTL_TASSEL_SHIFT,
    taCtlTasselSMCLK  = 2U<<TA_CTL_TASSEL_SHIFT,
    taCtlTasselINCLK  = 3U<<TA_CTL_TASSEL_SHIFT
} TA_CtlTassel_Enum;


#define TA_R_RESET (0x0000U)


#define TA_CCTL_RESET (0x0000U)

#define TA_CCTL_CCIFG_SHIFT  (0U)
#define TA_CCTL_COV_SHIFT    (1U)
#define TA_CCTL_OUT_SHIFT    (2U)
#define TA_CCTL_CCI_SHIFT    (3U)
#define TA_CCTL_CCIE_SHIFT   (4U)
#define TA_CCTL_OUTMOD_SHIFT (5U)
#define TA_CCTL_CAP_SHIFT    (8U)
#define TA_CCTL_SCCI_SHIFT   (10U)
#define TA_CCTL_SCS_SHIFT    (11U)
#define TA_CCTL_CCIS_SHIFT   (12U)
#define TA_CCTL_CM_SHIFT     (14U)

#define TA_CCTL_CCIFG_MASK  (1U)
#define TA_CCTL_COV_MASK    (1U)
#define TA_CCTL_OUT_MASK    (1U)
#define TA_CCTL_CCI_MASK    (1U)
#define TA_CCTL_CCIE_MASK   (1U)
#define TA_CCTL_OUTMOD_MASK (7U)
#define TA_CCTL_CAP_MASK    (1U)
#define TA_CCTL_SCCI_MASK   (1U)
#define TA_CCTL_SCS_MASK    (1U)
#define TA_CCTL_CCIS_MASK   (3U)
#define TA_CCTL_CM_MASK     (3U)

#define TA_CCTL_CCIFG  (TA_CCTL_CCIFG_MASK<<TA_CCTL_CCIFG_SHIFT)
#define TA_CCTL_COV    (TA_CCTL_COV_MASK<<TA_CCTL_COV_SHIFT)
#define TA_CCTL_OUT    (TA_CCTL_OUT_MASK<<TA_CCTL_OUT_SHIFT)
#define TA_CCTL_CCI    (TA_CCTL_CCI_MASK<<TA_CCTL_CCI_SHIFT)
#define TA_CCTL_CCIE   (TA_CCTL_CCIE_MASK<<TA_CCTL_CCIE_SHIFT)
#define TA_CCTL_OUTMOD (TA_CCTL_OUTMOD_MASK<<TA_CCTL_OUTMOD_SHIFT)
#define TA_CCTL_CAP    (TA_CCTL_CAP_MASK<<TA_CCTL_CAP_SHIFT)
#define TA_CCTL_SCCI   (TA_CCTL_SCCI_MASK<<TA_CCTL_SCCI_SHIFT)
#define TA_CCTL_SCS    (TA_CCTL_SCS_MASK<<TA_CCTL_SCS_SHIFT)
#define TA_CCTL_CCIS   (TA_CCTL_CCIS_MASK<<TA_CCTL_CCIS_SHIFT)
#define TA_CCTL_CM     (TA_CCTL_CM_MASK<<TA_CCTL_CM_SHIFT)

typedef enum
{
    taCctlOutmodOUT         = 0U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodSet         = 1U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodTogglereset = 2U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodSetreset    = 3U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodToggle      = 4U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodReset       = 5U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodToggleset   = 6U<<TA_CCTL_OUTMOD_SHIFT,
    taCctlOutmodResetset    = 7U<<TA_CCTL_OUTMOD_SHIFT
} TA_CctlOutmod_Enum;
typedef enum
{
    taCctlCcisCCIxA = 0U<<TA_CCTL_CCIS_SHIFT,
    taCctlCcisCCIxB = 1U<<TA_CCTL_CCIS_SHIFT,
    taCctlCcisGND   = 2U<<TA_CCTL_CCIS_SHIFT,
    taCctlCcisVCC   = 3U<<TA_CCTL_CCIS_SHIFT
} TA_CctlCcis_Enum;
typedef enum
{
    taCctlCmNo      = 0U<<TA_CCTL_CM_SHIFT,
    taCctlCmRising  = 1U<<TA_CCTL_CM_SHIFT,
    taCctlCmFalling = 2U<<TA_CCTL_CM_SHIFT,
    taCctlCmBoth    = 3U<<TA_CCTL_CM_SHIFT
} TA_CctlCm_Enum;


#define TA_CCR_RESET (0x0000U)


#define TA_EX0_RESET (0x0000U)


typedef struct
{
    bool ie;
    TA_CtlMc_Enum mc;
    TA_CtlId_Enum id;
    TA_CtlTassel_Enum tassel;
} TA_CtlConfig_Struct;
typedef struct
{
    bool out;
    bool ie;
    TA_CctlOutmod_Enum outmod;
    bool cap;
    bool scs;
    TA_CctlCcis_Enum ccis;
    TA_CctlCm_Enum cm;
} TA_CctlConfig_Struct;


void TA_reset(TA_Registers_Struct * TAx);

void TA_configureCtl(TA_Registers_Struct * TAx, TA_CtlConfig_Struct * config);

void TA_configureCctl(TA_Registers_Struct * TAx, uint8_t n, TA_CctlConfig_Struct * config);

inline __attribute__ ((always_inline)) void TA_setR(TA_Registers_Struct * TAx, uint16_t val)
{
    TAx->R = val;
}

inline __attribute__ ((always_inline)) void TA_setCcr(TA_Registers_Struct * TAx, uint8_t n, uint16_t val)
{
    TAx->CCR[n] = val;
}

inline __attribute__ ((always_inline)) void TA_start(TA_Registers_Struct * TAx, TA_CtlMc_Enum mode)
{
    TAx->CTL &= mode|(~TA_CTL_MC);
    TAx->CTL |= mode;
}

inline __attribute__ ((always_inline)) void TA_stop(TA_Registers_Struct * TAx)
{
    TAx->CTL &= taCtlMcStop|(~TA_CTL_MC);
    TAx->CTL |= taCtlMcStop;
}

#endif /* HAL_HEADERS_TIMERA_HAL_H_ */
