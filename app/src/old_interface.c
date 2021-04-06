/*
 * interface.c
 *
 *  Created on: Feb 22, 2021
 *      Author: jgamm
 */

#include "FreeRTOS.h"
#include "semphr.h"

#include <stdint.h>
#include <stdbool.h>

#include "interface.h"
#include "control_motors.h"
#include "check_alignment.h"
#include "error.h"

#include "USB_config/descriptors.h"
#include "USB_API/USB_Common/device.h"
#include "USB_API/USB_Common/usb.h"
#include "USB_API/USB_CDC_API/UsbCdc.h"
#include "USB_app/usbConstructs.h"

#include "timerb_hal.h"
#include "io_hal.h"
#include "io_interrupts.h"

#include <msp430.h>

typedef enum
{
    turnMotor = '0',
    alignMotor = '1',
    writeLaser = '2',
    readSensor = '3',
    reportStatus = '4',
    reportAssertInfo = '5',
    invokeBsl = '6',
    invalid
} _Cmd_Enum;
typedef enum
{
    thetaMsg = '0',
    phiMsg = '1'
} _Motor_Enum;
typedef enum
{
    cwMsg = '0',
    ccwMsg = '1'
} _Dir_Enum;
typedef enum
{
    laserOnMsg = '1',
    laserOffMsg = '0'
} _LaserState_Enum;

typedef struct
{
    CM_Motor_Enum motor;
} _AlignMotorCmd_Struct;
typedef struct
{
    CM_Motor_Enum motor;
    uint32_t num_steps;
    CM_Dir_Enum dir;
} _TurnMotorCmd_Struct;
typedef struct
{
    bool state;
} _WriteLaserCmd_Struct;

#define MAX(A, B) ((A)>=(B)? (A) : (B))
#define CMD_STRUCT_SIZE (MAX(sizeof(_AlignMotorCmd_Struct), MAX(sizeof(_TurnMotorCmd_Struct), sizeof(_WriteLaserCmd_Struct))))

static SemaphoreHandle_t rx_available = NULL;

static TaskHandle_t rx_task = NULL;

static void _rxTask(void *);
static void _callCommand(_Cmd_Enum cmd, void * params);
static void _doneHandler(void);
static void _doneHandlerRv(uint16_t);
static void _reportAssertHandler(void);
static void _invokeBsl(void);

void IF_informRx(void)
{
    xSemaphoreGiveFromISR(rx_available, NULL);
}

#define SW2_PORT (P2)
#define SW2_PIN  (IO_PIN4)

void IF_init(void)
{
    IO_PinConfig_Struct button_config =
    {
     .initial_out = ioOutHigh,
     .dir = ioDirInput,
     .ren = true,
     .ds = ioDsReduced,
     .sel = ioSelIo,
     .ies = ioIesFalling,
     .ie = true
    };
    IO_configurePin(SW2_PORT, SW2_PIN, &button_config);
    IO_attachInterrupt(SW2_PORT, SW2_PIN, _invokeBsl);

    static StaticSemaphore_t rx_available_buffer;
    ASSERT(rx_available == NULL);
    rx_available = xSemaphoreCreateBinaryStatic(&rx_available_buffer);
    ASSERT(rx_available != NULL);

    static StackType_t rx_task_stack_buffer[configMINIMAL_STACK_SIZE];
    static StaticTask_t rx_task_task_buffer;
    ASSERT(rx_task == NULL);
    rx_task = xTaskCreateStatic(_rxTask, "rx task", configMINIMAL_STACK_SIZE, NULL, 2, rx_task_stack_buffer, &rx_task_task_buffer);
    ASSERT(rx_task != NULL);

    USB_setup(true, true);
}

static inline uint32_t stoui32(char * s, uint8_t len)
{
    uint32_t rv = 0;
    uint32_t base;
    for(base=1, len=len-1; len<0xFF; --len, base*=10)
        rv += ((uint32_t)(s[len]-'0'))*base;
    return rv;
}

#define RX_BUFFER_SIZE (16U)
static void _rxTask(void * params)
{
    uint8_t count = 0;
    char rx_buffer[RX_BUFFER_SIZE];
    const char ack[] = "a\n";
    uint8_t cmd_struct[CMD_STRUCT_SIZE];
    void (*wb_handler)(void) = 0;
    while(1)
    {
        xSemaphoreTake(rx_available, portMAX_DELAY);
        count += USBCDC_receiveDataInBuffer((uint8_t*)(rx_buffer+count), RX_BUFFER_SIZE, CDC0_INTFNUM);
        ASSERT(count <= RX_BUFFER_SIZE);
        ASSERT(count >= 1);
        if(rx_buffer[count-1] == '\n')
        {
            switch((_Cmd_Enum) rx_buffer[0])
            {
            case turnMotor:
                ASSERT(count == 14);
                ((_TurnMotorCmd_Struct *)cmd_struct)->motor = rx_buffer[1]==thetaMsg? theta : phi;
                ((_TurnMotorCmd_Struct *)cmd_struct)->num_steps = stoui32(rx_buffer+2, 10);
                ((_TurnMotorCmd_Struct *)cmd_struct)->dir = rx_buffer[12]==cwMsg? clockwise : counterclockwise;
                _callCommand(turnMotor, cmd_struct);
                break;
            case alignMotor:
                ASSERT(count == 3);
                ((_AlignMotorCmd_Struct *)cmd_struct)->motor = rx_buffer[1]==thetaMsg? theta : phi;
                _callCommand(alignMotor, cmd_struct);
                break;
            case writeLaser:
                ASSERT(count == 3);
                ((_WriteLaserCmd_Struct *)cmd_struct)->state = rx_buffer[1]==laserOnMsg? true : false;
                _callCommand(writeLaser, cmd_struct);
                break;
            case readSensor:
                ASSERT(count == 2);
                _callCommand(readSensor, NULL);
                break;
            case reportStatus:
                ASSERT(false);
                break;
            case reportAssertInfo:
                wb_handler = _reportAssertHandler;
                break;
            case invokeBsl:
                wb_handler = _invokeBsl;
                break;
            default:
                ASSERT(false);
            }
            count = 0;
            USBCDC_sendDataInBackground((uint8_t*)ack, (sizeof(ack)/sizeof(char))-1, CDC0_INTFNUM, 1);
        }
        if(wb_handler != 0)
        {
            (*wb_handler)();
            wb_handler = 0;
        }
    }
}

static void _callCommand(_Cmd_Enum cmd, void * params)
{
    switch(cmd)
    {
    case turnMotor:
        CM_turnMotorSteps(((_TurnMotorCmd_Struct *)params)->motor, ((_TurnMotorCmd_Struct *)params)->num_steps, ((_TurnMotorCmd_Struct *)params)->dir, _doneHandler);
        break;
    case alignMotor:
        CM_align(((_AlignMotorCmd_Struct *)params)->motor, _doneHandler);
        break;
    case writeLaser:
        CA_writeLaser(((_WriteLaserCmd_Struct *)params)->state, _doneHandler);
        break;
    case readSensor:
        CA_measureSensor(_doneHandlerRv);
        break;
    case reportStatus:
        ASSERT(false);
        break;
    default:
        ASSERT(false);
    }
}

static void _doneHandler(void)
{
    static const char done_str[] = "d\n";
    USBCDC_sendDataInBackground((uint8_t*)done_str, (sizeof(done_str)/sizeof(char))-1, CDC0_INTFNUM, 1);
}

static void _doneHandlerRv(uint16_t rv)
{
    uint8_t i;
    uint16_t base;
    static char done_str[] ="00000d\n";
    for(i=0, base=10000; i<5; ++i, base/=10)
        done_str[i] = (char)('0'+((rv/base)%10));
    USBCDC_sendDataInBackground((uint8_t*)done_str, (sizeof(done_str)/sizeof(char))-1, CDC0_INTFNUM, 1);
}

static void _reportAssertHandler(void)
{
    static char done_str[124 + 2 + 5];
    ERROR_AssertInfo_Struct * info = ERROR_lastAssertInfo();
    if(info == 0)
    {
        done_str[0] = 'd';
        done_str[1] = '\n';
        USBCDC_sendDataInBackground((uint8_t *)done_str, 2, CDC0_INTFNUM, 1);
        return;
    }
    uint8_t idx;
    for(idx=0; idx<info->file_len; ++idx)
        done_str[idx] = info->file[idx];
    done_str[idx] = '\n';
    for(idx=0; idx<info->expression_len; ++idx)
        done_str[idx+info->file_len+1] = info->expression[idx];
    idx += info->file_len+1;
    done_str[idx] = '\n';
    ++idx;
    uint16_t base;
    for(base=10000; base>0; base/=10, ++idx)
        done_str[idx] = '0'+((info->line/base)%10);
    done_str[idx] = '\n';
    ++idx;
    done_str[idx] = 'd';
    ++idx;
    done_str[idx] = '\n';
    ++idx;
    USBCDC_sendDataInBackground((uint8_t *)done_str, idx, CDC0_INTFNUM, 1);
}

static void _invokeBsl(void)
{
    static char done_str[] = "d\n";
    USBCDC_sendDataAndWaitTillDone((uint8_t *)done_str, (sizeof(done_str)/sizeof(char))-1, CDC0_INTFNUM, 1);
    __disable_interrupt();
    TB_reset(TB0);
    ((void (*)()) 0x1000)();
}
