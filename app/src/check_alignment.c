/*
 * check_alignment.c
 *
 *  Created on: Mar 2, 2021
 *      Author: jgamm
 */

#include "check_alignment.h"
#include "io_hal.h"
#include "error.h"
#include "FreeRTOS.h"
#include "adc12_a.h"
#include <msp430.h>
#include "task.h"
#include "semphr.h"

#define MAX(A, B) ((A)>=(B)? (A) : (B))
#define MEASURESENSOR_EXE_IDX  (0)
#define MEASURESENSOR_DONE_IDX (1)

typedef enum
{
    probe,
    test,
    invalid
} _Id_Enum;
static _Id_Enum id = invalid;
typedef struct
{
    bool state;
    void (*handler)(void *, bool);
    void * handler_args;
} _LaserControl_Struct;
typedef struct
{
    void (*handler)(uint16_t, void *);
    void * handler_args;
} _MeasureSensor_Struct;
static uint8_t cmd_struct[MAX(sizeof(_LaserControl_Struct), sizeof(_MeasureSensor_Struct))];

static SemaphoreHandle_t laser_ownership = NULL;
static SemaphoreHandle_t sensor_ownership = NULL;

static TaskHandle_t laser_control_task = NULL;
static TaskHandle_t measure_sensor_task = NULL;

static StackType_t task_stack_buffer[configMINIMAL_STACK_SIZE];
static StaticTask_t task_task_buffer;
static StaticSemaphore_t item_ownership_buffer;

static void _initTest(void);
static void _initProbe(void);
static void _laserControlTask(void *);
static void _measureSensorTask(void *);

void CA_init(void)
{
    IO_PinConfig_Struct io_config =
    {
     .initial_out = ioOutLow,
     .dir = ioDirInput,
     .ren = false,
     .ds = ioDsReduced,
     .sel = ioSelIo,
     .ies = ioIesFalling,
     .ie = false
    };
    IO_configurePin(CA_TXRXID_PORT, CA_TXRXID_PIN, &io_config);
    id = IO_readPin(CA_TXRXID_PORT, CA_TXRXID_PIN)? probe : test;
    if(id == test)
        _initTest();
    else
        _initProbe();
}

void CA_writeLaser(bool state, void (*handler)(void *, bool), void * handler_args)
{
    ASSERT(id == test);
    ((_LaserControl_Struct *)cmd_struct)->state = state;
    ((_LaserControl_Struct *)cmd_struct)->handler = handler;
    ((_LaserControl_Struct *)cmd_struct)->handler_args = handler_args;
    xTaskNotifyGive(laser_control_task);
}

void CA_measureSensor(void (*handler)(uint16_t, void *), void * handler_args)
{
    ASSERT(id == probe);
    ((_MeasureSensor_Struct *)cmd_struct)->handler = handler;
    ((_MeasureSensor_Struct *)cmd_struct)->handler_args = handler_args;
    xTaskNotifyGiveIndexed(measure_sensor_task, MEASURESENSOR_EXE_IDX);
}

bool CA_idProbe(void)
{
    ASSERT((id==probe) || (id==test));
    return id==probe;
}

static void _initTest(void)
{
    ASSERT(id == test);
    ASSERT(laser_control_task == NULL);
    laser_control_task = xTaskCreateStatic(_laserControlTask, "control laser", configMINIMAL_STACK_SIZE, NULL, 2, task_stack_buffer, &task_task_buffer);
    ASSERT(laser_control_task != NULL);
    ASSERT(laser_ownership == NULL);
    laser_ownership = xSemaphoreCreateBinaryStatic(&item_ownership_buffer);
    ASSERT(laser_ownership != NULL);
    xSemaphoreGive(laser_ownership);

    IO_PinConfig_Struct io_config =
    {
     .initial_out = ioOutLow,
     .dir = ioDirOutput,
     .ren = false,
     .ds = ioDsReduced,
     .sel = ioSelIo,
     .ies = ioIesFalling,
     .ie = false
    };
    IO_configurePin(CA_POWER_PORT, CA_POWER_PIN, &io_config);
}

static void _initProbe(void)
{
    ASSERT(id == probe);
    ASSERT(measure_sensor_task == NULL);
    measure_sensor_task = xTaskCreateStatic(_measureSensorTask, "measure sensor", configMINIMAL_STACK_SIZE, NULL, 2, task_stack_buffer, &task_task_buffer);
    ASSERT(measure_sensor_task != NULL);
    ASSERT(sensor_ownership == NULL);
    sensor_ownership = xSemaphoreCreateBinaryStatic(&item_ownership_buffer);
    ASSERT(sensor_ownership != NULL);
    xSemaphoreGive(sensor_ownership);

    IO_PinConfig_Struct io_config =
    {
     .initial_out = ioOutLow,
     .dir = ioDirOutput,
     .ren = false,
     .ds = ioDsReduced,
     .sel = ioSelIo,
     .ies = ioIesFalling,
     .ie = false
    };
    IO_configurePin(CA_POWER_PORT, CA_POWER_PIN, &io_config);
    io_config.sel = ioSelPeripheral;
    io_config.dir = ioDirInput;
    IO_configurePin(CA_INTENSITY_PORT, CA_INTENSITY_PIN, &io_config);

    ADC12_A_init(ADC12_A_BASE, ADC12_A_SAMPLEHOLDSOURCE_SC, ADC12_A_CLOCKSOURCE_ADC12OSC, ADC12_A_CLOCKDIVIDER_1);
    ADC12_A_configureMemoryParam adc_config =
    {
     .memoryBufferControlIndex = CA_INTENSITY_AMEN,
     .inputSourceSelect = CA_INTENSITY_APIN,
     .positiveRefVoltageSourceSelect = ADC12_A_VREFPOS_AVCC,
     .negativeRefVoltageSourceSelect = ADC12_A_VREFNEG_AVSS,
     .endOfSequence = ADC12_A_NOTENDOFSEQUENCE
    };
    ADC12_A_configureMemory(ADC12_A_BASE, &adc_config);
}

static void _laserControlTask(void * args)
{
    ASSERT(id == test);
    _LaserControl_Struct * cmd = (_LaserControl_Struct *)cmd_struct;
    while(1)
    {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        xSemaphoreTake(laser_ownership, portMAX_DELAY);
        IO_writePin(CA_POWER_PORT, CA_POWER_PIN, (IO_Out_Enum)cmd->state);
        xSemaphoreGive(laser_ownership);
        cmd->handler(cmd->handler_args, false);
    }
}

static void _measureSensorTask(void * args)
{
    ASSERT(id == probe);
    _MeasureSensor_Struct * cmd = (_MeasureSensor_Struct *)cmd_struct;
    while(1)
    {
        ulTaskNotifyTakeIndexed(MEASURESENSOR_EXE_IDX, pdTRUE, portMAX_DELAY);
        xSemaphoreTake(sensor_ownership, portMAX_DELAY);
        IO_writePin(CA_POWER_PORT, CA_POWER_PIN, ioOutHigh);
        ADC12_A_enable(ADC12_A_BASE);
        ADC12_A_setupSamplingTimer(ADC12_A_BASE, ADC12_A_CYCLEHOLD_64_CYCLES, ADC12_A_CYCLEHOLD_4_CYCLES, 0);
        ADC12_A_clearInterrupt(ADC12_A_BASE, CA_INTENSITY_AIFG);
        ADC12_A_enableInterrupt(ADC12_A_BASE, CA_INTENSITY_AIFG);
        ADC12_A_startConversion(ADC12_A_BASE, CA_INTENSITY_AMEN, ADC12_A_SINGLECHANNEL);
        ulTaskNotifyTakeIndexed(MEASURESENSOR_DONE_IDX, pdTRUE, portMAX_DELAY);
        ADC12_A_disableInterrupt(ADC12_A_BASE, CA_INTENSITY_AIFG);
        ADC12_A_disable(ADC12_A_BASE);
        IO_writePin(CA_POWER_PORT, CA_POWER_PIN, ioOutLow);
        xSemaphoreGive(sensor_ownership);
        cmd->handler(ADC12_A_getResults(ADC12_A_BASE, CA_INTENSITY_AMEN), cmd->handler_args);
    }
}

#pragma vector=ADC12_VECTOR
void __attribute__ ((interrupt)) ADC12_A_IRQHandler(void)
{
    vTaskNotifyGiveIndexedFromISR(measure_sensor_task, MEASURESENSOR_DONE_IDX, NULL);
    ADC12_A_clearInterrupt(ADC12_A_BASE, CA_INTENSITY_AIFG);
}
