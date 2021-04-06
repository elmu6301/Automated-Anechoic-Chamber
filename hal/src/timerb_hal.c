/*
 * timerb_hal.c
 *
 *  Created on: Feb 8, 2021
 *      Author: jgamm
 */

#include "error.h"
#include "timerb_hal.h"
#include <msp430.h>

void TB_unitTest(TB_Registers_Struct * TBx)
{
    uint8_t n;
    TB_reset(TBx);
    ASSERT(TBx->CTL == TB_CTL_RESET);
    for(n=TB_CCTL_NUMBER-1; n<TB_CCTL_NUMBER; --n)
        ASSERT(TBx->CCTL[n] == TB_CCTL_RESET);
    ASSERT(TBx->R == TB_CTL_RESET);
    for(n=TB_CCR_NUMBER-1; n<TB_CCR_NUMBER; --n)
        ASSERT(TBx->CCR[n] == TB_CCR_RESET);
    ASSERT(TBx->EX0 == TB_EX0_RESET);
    TBx->CTL ^= TB_CTL_TBIFG;
    ASSERT((TBx->CTL&TB_CTL_TBIFG) == TB_CTL_TBIFG);
    TBx->CTL ^= TB_CTL_TBIFG;
    TBx->CTL ^= TB_CTL_TBIE;
    ASSERT((TBx->CTL&TB_CTL_TBIE) == TB_CTL_TBIE);
    TBx->CTL ^= TB_CTL_TBIE;
    TBx->CTL ^= TB_CTL_MC;
    ASSERT((TBx->CTL&TB_CTL_MC) == TB_CTL_MC);
    TBx->CTL ^= TB_CTL_MC;
    TBx->CTL ^= TB_CTL_ID;
    ASSERT((TBx->CTL&TB_CTL_ID) == TB_CTL_ID);
    TBx->CTL ^= TB_CTL_ID;
    TBx->CTL ^= TB_CTL_TBSSEL;
    ASSERT((TBx->CTL&TB_CTL_TBSSEL) == TB_CTL_TBSSEL);
    TBx->CTL ^= TB_CTL_TBSSEL;
    TBx->CTL ^= TB_CTL_CNTL;
    ASSERT((TBx->CTL&TB_CTL_CNTL) == TB_CTL_CNTL);
    TBx->CTL ^= TB_CTL_CNTL;
    TBx->CTL ^= TB_CTL_TBCLGRP;
    ASSERT((TBx->CTL&TB_CTL_TBCLGRP) == TB_CTL_TBCLGRP);
    TBx->CTL ^= TB_CTL_TBCLGRP;
    for(n=TB_CCTL_NUMBER-1; n<TB_CCTL_NUMBER; --n)
    {
        TBx->CCTL[n] ^= TB_CCTL_CCIFG;
        ASSERT((TBx->CCTL[n]&TB_CCTL_CCIFG) == TB_CCTL_CCIFG);
        TBx->CCTL[n] ^= TB_CCTL_CCIFG;
        TBx->CCTL[n] ^= TB_CCTL_COV;
        ASSERT((TBx->CCTL[n]&TB_CCTL_COV) == TB_CCTL_COV);
        TBx->CCTL[n] ^= TB_CCTL_COV;
        TBx->CCTL[n] ^= TB_CCTL_OUT;
        ASSERT((TBx->CCTL[n]&TB_CCTL_OUT) == TB_CCTL_OUT);
        TBx->CCTL[n] ^= TB_CCTL_OUT;
        TBx->CCTL[n] ^= TB_CCTL_CCIE;
        ASSERT((TBx->CCTL[n]&TB_CCTL_CCIE) == TB_CCTL_CCIE);
        TBx->CCTL[n] ^= TB_CCTL_CCIE;
        TBx->CCTL[n] ^= TB_CCTL_OUTMOD;
        ASSERT((TBx->CCTL[n]&TB_CCTL_OUTMOD) == TB_CCTL_OUTMOD);
        TBx->CCTL[n] ^= TB_CCTL_OUTMOD;
        TBx->CCTL[n] ^= TB_CCTL_CAP;
        ASSERT((TBx->CCTL[n]&TB_CCTL_CAP) == TB_CCTL_CAP);
        TBx->CCTL[n] ^= TB_CCTL_CAP;
        TBx->CCTL[n] ^= TB_CCTL_CLLD;
        ASSERT((TBx->CCTL[n]&TB_CCTL_CLLD) == TB_CCTL_CLLD);
        TBx->CCTL[n] ^= TB_CCTL_CLLD;
        TBx->CCTL[n] ^= TB_CCTL_SCS;
        ASSERT((TBx->CCTL[n]&TB_CCTL_SCS) == TB_CCTL_SCS);
        TBx->CCTL[n] ^= TB_CCTL_SCS;
        TBx->CCTL[n] ^= TB_CCTL_CCIS;
        ASSERT((TBx->CCTL[n]&TB_CCTL_CCIS) == TB_CCTL_CCIS);
        TBx->CCTL[n] ^= TB_CCTL_CCIS;
        TBx->CCTL[n] ^= TB_CCTL_CM;
        ASSERT((TBx->CCTL[n]&TB_CCTL_CM) == TB_CCTL_CM);
        TBx->CCTL[n] ^= TB_CCTL_CM;
    }
    TBx->R ^= ~TB_R_RESET;
    ASSERT(TBx->R == ~TB_R_RESET);
    TBx->R ^= ~TB_R_RESET;
    for(n=TB_CCR_NUMBER-1; n<TB_CCR_NUMBER; --n)
    {
        TBx->CCR[n] ^= ~TB_CCR_RESET;
        ASSERT(TBx->CCR[n] == ~TB_CCR_RESET);
        TBx->CCR[n] ^= ~TB_CCR_RESET;
    }
    TBx->EX0 ^= 7;
    ASSERT(TBx->EX0 == 7);
    TBx->EX0 ^= 7;
    ASSERT(TBx->CTL == TB_CTL_RESET);
    for(n=TB_CCTL_NUMBER; n<TB_CCTL_NUMBER; --n)
        ASSERT(TBx->CCTL[n] == TB_CCTL_RESET);
    ASSERT(TBx->R == TB_CTL_RESET);
    for(n=TB_CCTL_NUMBER-1; n<TB_CCTL_NUMBER; --n)
        ASSERT(TBx->CCR[n] == TB_CCR_RESET);
    ASSERT(TBx->EX0 == TB_EX0_RESET);
}

void TB_reset(TB_Registers_Struct * TBx)
{
    uint8_t n;
    TBx->CTL = TB_CTL_RESET;
    for(n=TB_CCTL_NUMBER-1; n<TB_CCTL_NUMBER; --n)
        TBx->CCTL[n] = TB_CCTL_RESET;
    TBx->R = TB_R_RESET;
    for(n=TB_CCTL_NUMBER-1; n<TB_CCTL_NUMBER; --n)
        TBx->CCR[n] = TB_CCR_RESET;
    TBx->EX0 = TB_EX0_RESET;
}

void TB_configureCtl(TB_Registers_Struct * TBx, TB_CtlConfig_Struct * config)
{
    TBx->CTL &= ~((!config->ie)<<TB_CTL_TBIE_SHIFT);
    TBx->CTL |= config->ie<<TB_CTL_TBIE_SHIFT;
    TBx->CTL &= config->mc|(~TB_CTL_MC);
    TBx->CTL |= config->mc;
    TBx->CTL &= config->id|(~TB_CTL_ID);
    TBx->CTL |= config->id;
    TBx->CTL &= config->tbssel|(~TB_CTL_TBSSEL);
    TBx->CTL |= config->tbssel;
    TBx->CTL &= config->cntl|(~TB_CTL_CNTL);
    TBx->CTL |= config->cntl;
    TBx->CTL &= config->tbclgrp|(~TB_CTL_TBCLGRP);
    TBx->CTL |= config->tbclgrp;
}

void TB_configureCctl(TB_Registers_Struct * TBx, uint8_t n, TB_CctlConfig_Struct * config)
{
    ASSERT(n <= TB_CCTL_NUMBER);
    TBx->CCTL[n] &= ~((!config->out)<<TB_CCTL_OUT_SHIFT);
    TBx->CCTL[n] |= config->out<<TB_CCTL_OUT_SHIFT;
    TBx->CCTL[n] &= ~((!config->ie)<<TB_CCTL_CCIE_SHIFT);
    TBx->CCTL[n] |= config->ie<<TB_CCTL_CCIE_SHIFT;
    TBx->CCTL[n] &= config->outmod|(~TB_CCTL_OUTMOD);
    TBx->CCTL[n] |= config->outmod;
    TBx->CCTL[n] &= ~((!config->cap)<<TB_CCTL_CAP_SHIFT);
    TBx->CCTL[n] |= config->cap<<TB_CCTL_CAP_SHIFT;
    TBx->CCTL[n] &= config->clld|(~(TB_CCTL_CLLD_MASK<<TB_CCTL_CLLD_SHIFT));
    TBx->CCTL[n] |= config->clld;
    TBx->CCTL[n] &= ~((!config->scs)<<TB_CCTL_SCS_SHIFT);
    TBx->CCTL[n] |= config->scs<<TB_CCTL_SCS_SHIFT;
    TBx->CCTL[n] &= config->ccis|(~(TB_CCTL_CCIS_MASK<<TB_CCTL_CCIS_SHIFT));
    TBx->CCTL[n] |= config->ccis;
    TBx->CCTL[n] &= config->cm|(~(TB_CCTL_CM_MASK<<TB_CCTL_CM_SHIFT));
}

