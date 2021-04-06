/*
 * pmm_hal.c
 *
 *  Created on: Feb 13, 2021
 *      Author: jgamm
 */

#include "pmm_hal.h"
#include "error.h"

static void _unlock(PMM_Registers_Struct * PMMx)
{
    PMMx->PMMCTL0H = 0xA5U; // Unlock PMM registers
}

static void _lock(PMM_Registers_Struct * PMMx)
{
    PMMx->PMMCTL0H = 0U; // Lock PMM registers
}

void PMM_reset(PMM_Registers_Struct * PMMx)
{
    _unlock(PMMx);
    PMMx->PMMCTL0L = PMM_PMMCTL0_RESET&0xFF;
    PMMx->SVSMHCTL = PMM_SVSMHCTL_RESET;
    PMMx->SVSMLCTL = PMM_SVSMLCTL_RESET;
    PMMx->SVSMIO = PMM_SVSMIO_RESET;
    PMMx->PMMRIE = PMM_PMMRIE_RESET;
    PMMx->PMMIFG = PMM_PMMIFG_RESET;
    PMMx->PM5CTL0 = PMM_PM5CTL0_RESET;
    _lock(PMMx);
}

void PMM_writePmmCoreV(PMM_Registers_Struct * PMMx, PMM_PmmCoreV_Enum val)
{
    if(val == (PMMx->PMMCTL0L & PMM_PMMCTL0_PMMCOREV)) // no change needed
        return;
    _unlock(PMMx);
    while(val > (PMMx->PMMCTL0L & PMM_PMMCTL0_PMMCOREV))
    { // step up 1 level at a time, as described in reference manual
        uint8_t level = 1 + ((PMMx->PMMCTL0L & PMM_PMMCTL0_PMMCOREV) >> PMM_PMMCTL0_PMMCOREV_SHIFT);
        while((PMMx->PMMIFG & PMM_PMMIFG_SVSMHDLYIFG) == 0);
        while((PMMx->PMMIFG & PMM_PMMIFG_SVSMLDLYIFG) == 0);
        PMMx->SVSMHCTL = PMM_SVSMHCTL_SVSHE | (level<<PMM_SVSMHCTL_SVSHRVL_SHIFT) | PMM_SVSMHCTL_SVMHE | (level<<PMM_SVSMHCTL_SVSMHRRL_SHIFT);
        PMMx->SVSMLCTL = PMM_SVSMLCTL_SVSLE | PMM_SVSMLCTL_SVMLE | (level<<PMM_SVSMLCTL_SVSMLRRL_SHIFT);
        while((PMMx->PMMIFG & PMM_PMMIFG_SVSMLDLYIFG) == 0);
        PMMx->PMMIFG &= ~(PMM_PMMIFG_SVMLVLRIFG | PMM_PMMIFG_SVMLIFG);
        PMMx->PMMCTL0L &= (level<<PMM_PMMCTL0_PMMCOREV_SHIFT)|(~PMM_PMMCTL0_PMMCOREV);
        PMMx->PMMCTL0L |= level<<PMM_PMMCTL0_PMMCOREV_SHIFT;
        if((PMMx->PMMIFG & PMM_PMMIFG_SVMLIFG))
            while ((PMMx->PMMIFG & PMM_PMMIFG_SVMLVLRIFG) == 0);
        PMMx->SVSMLCTL = PMM_SVSMLCTL_SVSLE | (level<<PMM_SVSMLCTL_SVSLRVL_SHIFT) | PMM_SVSMLCTL_SVMLE | (level<<PMM_SVSMLCTL_SVSMLRRL_SHIFT);
    }
    while(val < (PMMx->PMMCTL0L & PMM_PMMCTL0_PMMCOREV))
    { // step up 1 level at a time, as described in reference manual
        uint8_t level = ((PMMx->PMMCTL0L & PMM_PMMCTL0_PMMCOREV) >> PMM_PMMCTL0_PMMCOREV_SHIFT)-1;
        while((PMMx->PMMIFG & PMM_PMMIFG_SVSMHDLYIFG) == 0);
        while((PMMx->PMMIFG & PMM_PMMIFG_SVSMLDLYIFG) == 0);
        PMMx->SVSMHCTL = PMM_SVSMHCTL_SVSHE | (level<<PMM_SVSMHCTL_SVSHRVL_SHIFT) | PMM_SVSMHCTL_SVMHE | (level<<PMM_SVSMHCTL_SVSMHRRL_SHIFT);
        PMMx->SVSMLCTL = PMM_SVSMLCTL_SVSLE | PMM_SVSMLCTL_SVMLE | (level<<PMM_SVSMLCTL_SVSMLRRL_SHIFT);
        while((PMMx->PMMIFG & PMM_PMMIFG_SVSMLDLYIFG) == 0);
        PMMx->PMMIFG &= ~(PMM_PMMIFG_SVMLVLRIFG | PMM_PMMIFG_SVMLIFG);
        PMMx->PMMCTL0L &= (level<<PMM_PMMCTL0_PMMCOREV_SHIFT)|(~PMM_PMMCTL0_PMMCOREV);
        PMMx->PMMCTL0L |= level<<PMM_PMMCTL0_PMMCOREV_SHIFT;
        if((PMMx->PMMIFG & PMM_PMMIFG_SVMLIFG))
            while ((PMMx->PMMIFG & PMM_PMMIFG_SVMLVLRIFG) == 0);
        PMMx->SVSMLCTL = PMM_SVSMLCTL_SVSLE | (level<<PMM_SVSMLCTL_SVSLRVL_SHIFT) | PMM_SVSMLCTL_SVMLE | (level<<PMM_SVSMLCTL_SVSMLRRL_SHIFT);
    }
    _lock(PMMx);
}
