/*
 * ucs_hal.c
 *
 *  Created on: Feb 8, 2021
 *      Author: jgamm
 */

#include "ucs_hal.h"
#include "error.h"

void UCS_reset(UCS_Registers_Struct * UCS)
{
    UCS->CTL0 = UCS_CTL0_RESET;
    UCS->CTL1 = UCS_CTL1_RESET;
    UCS->CTL2 = UCS_CTL2_RESET;
    UCS->CTL3 = UCS_CTL3_RESET;
    UCS->CTL4 = UCS_CTL4_RESET;
    UCS->CTL5 = UCS_CTL5_RESET;
    UCS->CTL6 = UCS_CTL6_RESET;
    UCS->CTL7 = UCS_CTL7_RESET;
    UCS->CTL8 = UCS_CTL8_RESET;
    UCS->CTL9 = UCS_CTL9_RESET;
}

void UCS_configureDco(UCS_Registers_Struct * UCS, UCS_DcoConfig_Struct * config)
{
    ASSERT(config->dcorsel <= 0x7);
    ASSERT(config->flln <= 0x1FF);
    UCS->CTL1 &= ~((!config->dismod)<<UCS_CTL1_DISMOD_SHIFT);
    UCS->CTL1 |= config->dismod<<UCS_CTL1_DISMOD_SHIFT;
    UCS->CTL1 &= (config->dcorsel<<UCS_CTL1_DCORSEL_SHIFT)|(~UCS_CTL1_DCORSEL);
    UCS->CTL1 |= config->dcorsel<<UCS_CTL1_DCORSEL_SHIFT;
    UCS->CTL2 &= (config->flln<<UCS_CTL2_FLLN_SHIFT)|(~UCS_CTL2_FLLN);
    UCS->CTL2 |= config->flln<<UCS_CTL2_FLLN_SHIFT;
    UCS->CTL2 &= config->flld|(~UCS_CTL2_FLLD);
    UCS->CTL3 &= config->fllrefdiv|(~UCS_CTL3_FLLREFDIV);
    UCS->CTL3 |= config->fllrefdiv;
    UCS->CTL3 &= config->selref|(~UCS_CTL3_SELREF);
    UCS->CTL3 |= config->selref;
}

void UCS_configureMclk(UCS_Registers_Struct * UCS, UCS_MclkConfig_Struct * config)
{
    UCS->CTL4 &= config->selm|(~UCS_CTL4_SELM);
    UCS->CTL4 |= config->selm;
    UCS->CTL5 &= config->divm|(~UCS_CTL5_DIVM);
    UCS->CTL5 |= config->divm;
    UCS->CTL8 &= ~((!config->mclkreqen)<<UCS_CTL8_MCLKREQEN_SHIFT);
    UCS->CTL8 |= config->mclkreqen<<UCS_CTL8_MCLKREQEN_SHIFT;
}

void UCS_configureSmclk(UCS_Registers_Struct * UCS, UCS_SmclkConfig_Struct * config)
{
    UCS->CTL4 &= config->sels|(~UCS_CTL4_SELS);
    UCS->CTL4 |= config->sels;
    UCS->CTL5 &= config->divs|(~UCS_CTL5_DIVS);
    UCS->CTL5 |= config->divs;
    UCS->CTL8 &= ~((!config->smclkreqen)<<UCS_CTL8_SMCLKREQEN_SHIFT);
    UCS->CTL8 |= config->smclkreqen<<UCS_CTL8_SMCLKREQEN_SHIFT;
}

void UCS_configureAclk(UCS_Registers_Struct * UCS, UCS_AclkConfig_Struct * config)
{
    UCS->CTL4 &= config->sela|(~UCS_CTL4_SELA);
    UCS->CTL4 |= config->sela;
    UCS->CTL5 &= config->diva|(~UCS_CTL5_DIVA);
    UCS->CTL5 |= config->diva;
    UCS->CTL8 &= ~((!config->aclkreqen)<<UCS_CTL8_ACLKREQEN_SHIFT);
    UCS->CTL8 |= config->aclkreqen<<UCS_CTL8_ACLKREQEN_SHIFT;
}
