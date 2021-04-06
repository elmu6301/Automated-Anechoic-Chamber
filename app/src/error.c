/*
 * error.c
 *
 *  Created on: Feb 8, 2021
 *      Author: jgamm
 */

#include "error.h"
#include "io_hal.h"
#include "timerb_hal.h"
#include <msp430.h>
#include <stdbool.h>
#include "flashctl.h"
#include "USB_API/USB_Common/usb.h"
#include "hal.h"

#define VALID_PATTERN (0xAAAAU)
#define SEG_LEN       (128U)
#define MSG_LEN       ((SEG_LEN-2*sizeof(uint16_t))/2)
#define INFOB_BASE    ((uint8_t *)(0x1880))

static void _updateLastAssertInfo(char *, char *, uint16_t);

ERROR_AssertInfo_Struct * ERROR_lastAssertInfo(void)
{
    static ERROR_AssertInfo_Struct info;
    if(*((uint16_t *)(INFOB_BASE)) != VALID_PATTERN)
        return 0;
    info.file = (char *) (INFOB_BASE+2*sizeof(uint16_t)+MSG_LEN);
    info.expression = (char *) (INFOB_BASE+2*sizeof(uint16_t));
    for(info.file_len=0; (info.file_len<MSG_LEN) && (info.file[info.file_len] != '\0'); ++info.file_len);
    for(info.expression_len=0; (info.expression_len<MSG_LEN) && (info.expression[info.expression_len] != '\0'); ++info.expression_len);
    info.line = ((uint16_t *)INFOB_BASE)[1];
    return &info;
}

static void _updateLastAssertInfo(char * expression, char * file, uint16_t line)
{
    static uint8_t to_write[128] = {[0 ... 127] = 0};
    ((uint16_t *)to_write)[0] = VALID_PATTERN;
    ((uint16_t *)to_write)[1] = line;
    uint8_t idx;
    for(idx=0; (idx<MSG_LEN) && (expression[idx] != '\0'); ++idx)
        ((char *)to_write)[idx+2*sizeof(uint16_t)] = expression[idx];
    if(idx != MSG_LEN)
        ((char *)to_write)[idx+2*sizeof(uint16_t)] = '\0';
    for(idx=0; (idx<MSG_LEN) && (file[idx] != '\0'); ++idx)
        ((char *)to_write)[idx+2*sizeof(uint16_t)+MSG_LEN]  = file[idx];
    if(idx != MSG_LEN)
        ((char *)to_write)[idx+2*sizeof(uint16_t)+MSG_LEN] = '\0';
    FlashCtl_eraseSegment(INFOB_BASE);
    FlashCtl_write8(to_write, INFOB_BASE, 128);
    while(FlashCtl_getStatus(FLASHCTL_BUSY));
}

void __attribute__ ((noreturn)) _assert_failure(char * expression, char * file, uint16_t line)
{
    TB_reset(TB0);//__disable_interrupt();
    USB_disable();
    _updateLastAssertInfo(expression, file, line);
    volatile uint32_t i;
    IO_PinConfig_Struct led_config =
    {
     .initial_out = ioOutLow,
     .dir = ioDirOutput,
     .ren = false,
     .ds = ioDsReduced,
     .sel = ioSelIo,
     .ies = ioIesFalling,
     .ie = false
    };
    IO_configurePin(LED5_PORT, LED5_PIN, &led_config);
    while(1)
    {
        for(i=0xFFFF; i<0x10000; --i);
        IO_writePin(LED5_PORT, LED5_PIN, (IO_Out_Enum)!IO_readPin(LED5_PORT, LED5_PIN));
    }
}


