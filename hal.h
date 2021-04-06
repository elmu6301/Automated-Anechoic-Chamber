/* --COPYRIGHT--,BSD
 * Copyright (c) 2016, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * --/COPYRIGHT--*/
/*
 * ======== hal.h ========
 *
 * Device and board specific pins need to be configured here
 *
 */


/*----------------------------------------------------------------------------
 * The following function names are deprecated.  These were updated to new 
 * names to follow OneMCU naming convention.
 +---------------------------------------------------------------------------*/

#ifndef DEPRECATED
#define   initPorts       USBHAL_initPorts
#define   initClocks      USBHAL_initClocks
#endif

#define CM_PHI_STEP_TID   (timerA1)
#define CM_PHI_STEP_TOP   (1U)
#define CM_PHI_STEP_PORT  (P2)
#define CM_PHI_STEP_PIN   (IO_PIN0)
#define CM_PHI_SD_PORT    (P1)
#define CM_PHI_SD_PIN     (IO_PIN5)
#define CM_PHI_RESET_PORT (P1)
#define CM_PHI_RESET_PIN  (IO_PIN6)
#define CM_PHI_DIR_PORT   (P1)
#define CM_PHI_DIR_PIN    (IO_PIN7)
#define CM_PHI_FAULT_PORT (P2)
#define CM_PHI_FAULT_PIN  (IO_PIN1)
#define CM_PHI_ES_PORT    (P2)
#define CM_PHI_ES_PIN     (IO_PIN6)

#define CM_THETA_STEP_TID   (timerA0)
#define CM_THETA_STEP_TOP   (3U)
#define CM_THETA_STEP_PORT  (P1)
#define CM_THETA_STEP_PIN   (IO_PIN4)
#define CM_THETA_SD_PORT    (P8)
#define CM_THETA_SD_PIN     (IO_PIN0)
#define CM_THETA_RESET_PORT (P8)
#define CM_THETA_RESET_PIN  (IO_PIN1)
#define CM_THETA_DIR_PORT   (P8)
#define CM_THETA_DIR_PIN    (IO_PIN2)
#define CM_THETA_FAULT_PORT (P1)
#define CM_THETA_FAULT_PIN  (IO_PIN0)
#define CM_THETA_ES_PORT    (P1)
#define CM_THETA_ES_PIN     (IO_PIN3)


#define CA_INTENSITY_PORT (P6)
#define CA_INTENSITY_PIN  (IO_PIN1)
#define CA_INTENSITY_APIN (ADC12_A_INPUT_A1)
#define CA_INTENSITY_AMEN (ADC12_A_MEMORY_0)
#define CA_INTENSITY_AIFG (ADC12_A_IFG0)

#define DIST_PCB true
#if DIST_PCB == true
#define SW2_PORT (P2)
#define SW2_PIN (IO_PIN4)
#define LED5_PORT (P7)
#define LED5_PIN (IO_PIN5)
#define CA_POWER_PORT     (P6)
#define CA_POWER_PIN      (IO_PIN3)
#define CA_TXRXID_PORT    (P5)
#define CA_TXRXID_PIN     (IO_PIN6)
#else
#define SW2_PORT (P1)
#define SW2_PIN (IO_PIN0)
#define LED5_PORT (P4)
#define LED5_PIN (IO_PIN7)
#define CA_POWER_PORT (P1)
#define CA_POWER_PIN (IO_PIN0)
#define CA_TXRXID_PORT (P3)
#define CA_TXRXID_PIN (IO_PIN0)
#endif




void USBHAL_initPorts(void);
void USBHAL_initClocks(uint32_t mclkFreq);
//Released_Version_5_20_06_02
