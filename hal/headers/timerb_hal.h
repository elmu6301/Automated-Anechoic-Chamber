#ifndef HAL_HEADERS_TIMERB_HAL_H_
#define HAL_HEADERS_TIMERB_HAL_H_

#include <stdint.h>
#include <stdbool.h>

// Timer_B register layout
#define TB_CCTL_NUMBER (7U)
#define TB_CCR_NUMBER (7U)

typedef struct
{
    volatile uint16_t       CTL;
    volatile uint16_t       CCTL[TB_CCTL_NUMBER];
    volatile uint16_t       R;
    volatile uint16_t       CCR[TB_CCR_NUMBER];
    volatile uint16_t       EX0;
    volatile const uint8_t  RESERVED0[14U];
    volatile const uint16_t IV;
} TB_Registers_Struct;

// Timer_B base addresses
#define TB0 ((TB_Registers_Struct *) 0x03C0U)

// Timer_B Control (TBx_CTL)
#define TB_CTL_RESET (0x0000U)

#define TB_CTL_TBIFG_SHIFT   (0U)
#define TB_CTL_TBIE_SHIFT    (1U)
#define TB_CTL_TBCLR_SHIFT   (2U)
#define TB_CTL_MC_SHIFT      (4U)
#define TB_CTL_ID_SHIFT      (6U)
#define TB_CTL_TBSSEL_SHIFT  (8U)
#define TB_CTL_CNTL_SHIFT    (11U)
#define TB_CTL_TBCLGRP_SHIFT (13U)

#define TB_CTL_TBIFG_MASK   (1U)
#define TB_CTL_TBIE_MASK    (1U)
#define TB_CTL_TBCLR_MASK   (1U)
#define TB_CTL_MC_MASK      (3U)
#define TB_CTL_ID_MASK      (3U)
#define TB_CTL_TBSSEL_MASK  (3U)
#define TB_CTL_CNTL_MASK    (3U)
#define TB_CTL_TBCLGRP_MASK (3U)

#define TB_CTL_TBIFG   (TB_CTL_TBIFG_MASK<<TB_CTL_TBIFG_SHIFT)
#define TB_CTL_TBIE    (TB_CTL_TBIE_MASK<<TB_CTL_TBIE_SHIFT)
#define TB_CTL_TBCLR   (TB_CTL_TBCLR_MASK<<TB_CTL_TBCLR_SHIFT)
#define TB_CTL_MC      (TB_CTL_MC_MASK<<TB_CTL_MC_SHIFT)
#define TB_CTL_ID      (TB_CTL_ID_MASK<<TB_CTL_ID_SHIFT)
#define TB_CTL_TBSSEL  (TB_CTL_TBSSEL_MASK<<TB_CTL_TBSSEL_SHIFT)
#define TB_CTL_CNTL    (TB_CTL_CNTL_MASK<<TB_CTL_CNTL_SHIFT)
#define TB_CTL_TBCLGRP (TB_CTL_TBCLGRP_MASK<<TB_CTL_TBCLGRP_SHIFT)

typedef enum
{
    tbCtlMcStop       = 0U<<TB_CTL_MC_SHIFT,
    tbCtlMcUp         = 1U<<TB_CTL_MC_SHIFT,
    tbCtlMcContinuous = 2U<<TB_CTL_MC_SHIFT,
    tbCtlMcUpdown     = 3U<<TB_CTL_MC_SHIFT
} TB_CtlMc_Enum;
typedef enum
{
    tbCtlId1 = 0U<<TB_CTL_ID_SHIFT,
    tbCtlId2 = 1U<<TB_CTL_ID_SHIFT,
    tbCtlId4 = 2U<<TB_CTL_ID_SHIFT,
    tbCtlId8 = 3U<<TB_CTL_ID_SHIFT
} TB_CtlId_Enum;
typedef enum
{
    tbCtlTbsselTBxCLK = 0U<<TB_CTL_TBSSEL_SHIFT,
    tbCtlTbsselACLK   = 1U<<TB_CTL_TBSSEL_SHIFT,
    tbCtlTbsselSMCLK  = 2U<<TB_CTL_TBSSEL_SHIFT,
    tbCtlTbsselINCLK  = 3U<<TB_CTL_TBSSEL_SHIFT
} TB_CtlTbssel_Enum;
typedef enum
{
    tbCtlCntl16bit = 0U<<TB_CTL_CNTL_SHIFT,
    tbCtlCntl12bit = 1U<<TB_CTL_CNTL_SHIFT,
    tbCtlCntl10bit = 2U<<TB_CTL_CNTL_SHIFT,
    tbCtlCntl8bit  = 3U<<TB_CTL_CNTL_SHIFT
} TB_CtlCntl_Enum;
typedef enum
{
    tbCtlTbclgrp0 = 0U<<TB_CTL_TBCLGRP_SHIFT,
    tbCtlTbclgrp1 = 1U<<TB_CTL_TBCLGRP_SHIFT,
    tbCtlTbclgrp2 = 2U<<TB_CTL_TBCLGRP_SHIFT,
    tbCtlTbclgrp3 = 3U<<TB_CTL_TBCLGRP_SHIFT
} TB_CtlTbclgrp_Enum;

// Timer_B Capture/Compare Control n (TBx_CCTLn)
#define TB_CCTL_RESET (0x0000U)

#define TB_CCTL_CCIFG_SHIFT  (0U)
#define TB_CCTL_COV_SHIFT    (1U)
#define TB_CCTL_OUT_SHIFT    (2U)
#define TB_CCTL_CCI_SHIFT    (3U)
#define TB_CCTL_CCIE_SHIFT   (4U)
#define TB_CCTL_OUTMOD_SHIFT (5U)
#define TB_CCTL_CAP_SHIFT    (8U)
#define TB_CCTL_CLLD_SHIFT   (9U)
#define TB_CCTL_SCS_SHIFT    (11U)
#define TB_CCTL_CCIS_SHIFT   (12U)
#define TB_CCTL_CM_SHIFT     (14U)

#define TB_CCTL_CCIFG_MASK  (1U)
#define TB_CCTL_COV_MASK    (1U)
#define TB_CCTL_OUT_MASK    (1U)
#define TB_CCTL_CCI_MASK    (1U)
#define TB_CCTL_CCIE_MASK   (1U)
#define TB_CCTL_OUTMOD_MASK (7U)
#define TB_CCTL_CAP_MASK    (1U)
#define TB_CCTL_CLLD_MASK   (3U)
#define TB_CCTL_SCS_MASK    (1U)
#define TB_CCTL_CCIS_MASK   (3U)
#define TB_CCTL_CM_MASK     (3U)

#define TB_CCTL_CCIFG  (TB_CCTL_CCIFG_MASK<<TB_CCTL_CCIFG_SHIFT)
#define TB_CCTL_COV    (TB_CCTL_COV_MASK<<TB_CCTL_COV_SHIFT)
#define TB_CCTL_OUT    (TB_CCTL_OUT_MASK<<TB_CCTL_OUT_SHIFT)
#define TB_CCTL_CCI    (TB_CCTL_CCI_MASK<<TB_CCTL_CCI_SHIFT)
#define TB_CCTL_CCIE   (TB_CCTL_CCIE_MASK<<TB_CCTL_CCIE_SHIFT)
#define TB_CCTL_OUTMOD (TB_CCTL_OUTMOD_MASK<<TB_CCTL_OUTMOD_SHIFT)
#define TB_CCTL_CAP    (TB_CCTL_CAP_MASK<<TB_CCTL_CAP_SHIFT)
#define TB_CCTL_CLLD   (TB_CCTL_CLLD_MASK<<TB_CCTL_CLLD_SHIFT)
#define TB_CCTL_SCS    (TB_CCTL_SCS_MASK<<TB_CCTL_SCS_SHIFT)
#define TB_CCTL_CCIS   (TB_CCTL_CCIS_MASK<<TB_CCTL_CCIS_SHIFT)
#define TB_CCTL_CM     (TB_CCTL_CM_MASK<<TB_CCTL_CM_SHIFT)

typedef enum
{
    tbCctlOutmodOut         = 0U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodSet         = 1U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodTogglereset = 2U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodSetreset    = 3U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodToggle      = 4U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodReset       = 5U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodToggleset   = 6U<<TB_CCTL_OUTMOD_SHIFT,
    tbCctlOutmodResetset    = 7U<<TB_CCTL_OUTMOD_SHIFT
} TB_CctlOutmod_Enum;
typedef enum
{
    tbCctlClld0 = 0U<<TB_CCTL_CLLD_SHIFT,
    tbCctlClld1 = 1U<<TB_CCTL_CLLD_SHIFT,
    tbCctlClld2 = 2U<<TB_CCTL_CLLD_SHIFT,
    tbCctlClld3 = 3U<<TB_CCTL_CLLD_SHIFT
} TB_CctlClld_Enum;
typedef enum
{
    tbCctlCcisCCIxA = 0U<<TB_CCTL_CCIS_SHIFT,
    tbCctlCcisCCIxB = 1U<<TB_CCTL_CCIS_SHIFT,
    tbCctlCcisGND   = 2U<<TB_CCTL_CCIS_SHIFT,
    tbCctlCcisVCC   = 3U<<TB_CCTL_CCIS_SHIFT
} TB_CctlCcis_Enum;
typedef enum
{
    tbCctlCmNo      = 0U<<TB_CCTL_CM_SHIFT,
    tbCctlCmRising  = 1U<<TB_CCTL_CM_SHIFT,
    tbCctlCmFalling = 2U<<TB_CCTL_CM_SHIFT,
    tbCctlCmBoth    = 3U<<TB_CCTL_CM_SHIFT
} TB_CctlCm_Enum;

// Timer_B Counter (TBxR)
#define TB_R_RESET (0x0000U)

// Timer_B Capture/Compare n (TBxCCRn)
#define TB_CCR_RESET (0x0000U)

// Timer_B Expansion 0 (TBxEX0)
#define TB_EX0_RESET (0x0000U)

// Timer_B control functions
typedef struct
{
    bool ie;
    TB_CtlMc_Enum mc;
    TB_CtlId_Enum id;
    TB_CtlTbssel_Enum tbssel;
    TB_CtlCntl_Enum cntl;
    TB_CtlTbclgrp_Enum tbclgrp;
} TB_CtlConfig_Struct;
typedef struct
{
    bool out;
    bool ie;
    TB_CctlOutmod_Enum outmod;
    bool cap;
    TB_CctlClld_Enum clld;
    bool scs;
    TB_CctlCcis_Enum ccis;
    TB_CctlCm_Enum cm;
} TB_CctlConfig_Struct;


void TB_unitTest(TB_Registers_Struct * TBx);

void TB_reset(TB_Registers_Struct * TBx);

void TB_configureCtl(TB_Registers_Struct * TBx, TB_CtlConfig_Struct * config);

void TB_configureCctl(TB_Registers_Struct * TBx, uint8_t n, TB_CctlConfig_Struct * config);

inline __attribute__ ((always_inline)) void TB_setR(TB_Registers_Struct * TBx, uint16_t val)
{
    TBx->R = val;
}

inline __attribute__ ((always_inline)) void TB_setCcr(TB_Registers_Struct * TBx, uint8_t n, uint16_t val)
{
    TBx->CCR[n] = val;
}

inline __attribute__ ((always_inline)) void TB_start(TB_Registers_Struct * TBx, TB_CtlMc_Enum mode)
{
    TBx->CTL &= mode|(~TB_CTL_MC);
    TBx->CTL |= mode;
}

inline __attribute__ ((always_inline)) void TB_stop(TB_Registers_Struct * TBx)
{
    TBx->CTL &= tbCtlMcStop|(~TB_CTL_MC);
    TBx->CTL |= tbCtlMcStop;
}


#endif /* HAL_HEADERS_TIMERB_HAL_H_ */
