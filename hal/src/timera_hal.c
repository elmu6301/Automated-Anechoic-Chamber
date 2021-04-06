/*
 * timera_hal.c
 *
 *  Created on: Feb 20, 2021
 *      Author: jgamm
 */

#include "timera_hal.h"
#include "error.h"

void TA_reset(TA_Registers_Struct * TAx)
{
    uint8_t n;
    TAx->CTL = TA_CTL_RESET;
    for(n=TA_CCTL_NUMBER-1; n<TA_CCTL_NUMBER; --n)
        TAx->CCTL[n] = TA_CCTL_RESET;
    TAx->R = TA_R_RESET;
    for(n=TA_CCR_NUMBER-1; n<TA_CCR_NUMBER; --n)
        TAx->CCR[n] = TA_CCR_RESET;
    TAx->EX0 = TA_EX0_RESET;
}

void TA_configureCtl(TA_Registers_Struct * TAx, TA_CtlConfig_Struct * config)
{
    TAx->CTL &= ~((!config->ie)<<TA_CTL_TAIE_SHIFT);
    TAx->CTL |= config->ie<<TA_CTL_TAIE_SHIFT;
    TAx->CTL &= config->mc|(~TA_CTL_MC);
    TAx->CTL |= config->mc;
    TAx->CTL &= config->id|(~TA_CTL_ID);
    TAx->CTL |= config->id;
    TAx->CTL &= config->tassel|(~TA_CTL_TASSEL);
    TAx->CTL |= config->tassel;
}

void TA_configureCctl(TA_Registers_Struct * TAx, uint8_t n, TA_CctlConfig_Struct * config)
{
    ASSERT(n <= TA_CCTL_NUMBER);
    TAx->CCTL[n] &= ~((!config->out)<<TA_CCTL_OUT_SHIFT);
    TAx->CCTL[n] |= config->out<<TA_CCTL_OUT_SHIFT;
    TAx->CCTL[n] &= ~((!config->ie)<<TA_CCTL_CCIE_SHIFT);
    TAx->CCTL[n] |= config->ie<<TA_CCTL_CCIE_SHIFT;
    TAx->CCTL[n] &= config->outmod|(~TA_CCTL_OUTMOD);
    TAx->CCTL[n] |= config->outmod;
    TAx->CCTL[n] &= ~((!config->cap)<<TA_CCTL_CAP_SHIFT);
    TAx->CCTL[n] |= config->cap<<TA_CCTL_CAP_SHIFT;
    TAx->CCTL[n] &= ~((!config->scs)<<TA_CCTL_SCS_SHIFT);
    TAx->CCTL[n] |= config->scs<<TA_CCTL_SCS_SHIFT;
    TAx->CCTL[n] &= config->ccis|(~TA_CCTL_CCIS);
    TAx->CCTL[n] |= config->ccis;
    TAx->CCTL[n] &= config->cm|(~TA_CCTL_CM);
    TAx->CCTL[n] |= config->cm;
}
