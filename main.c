#include "in430.h"
#include "timerb_hal.h"
#include "ucs_hal.h"
#include "io_hal.h"
#include "pmm_hal.h"
#include "driverlib.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "led_hil.h"
#include "control_motors.h"
#include "interface.h"
#include "check_alignment.h"
#include "USB_API/USB_Common/usb.h"

#include "hal.h"

void test(void)
{
    TB_unitTest(TB0);
}

void init(void)
{
    WDT_A_hold(WDT_A_BASE);


    //PMM_setVCore(PMM_CORE_LEVEL_3);
    //USBHAL_initClocks(24000000UL);
    PMM_setVCore(PMM_CORE_LEVEL_2);
    USBHAL_initClocks(8000000UL);


    //PMM_setVCore(PMM_CORE_LEVEL_2);
    //USBHAL_initClocks(8000000);
    //PMM_reset(PMM0);
    //PMM_writePmmCoreV(PMM0, pmmPmmCoreV3);
    //UCS_reset(UCS0);
    //UCS_DcoConfig_Struct dco_config =
    //{ // Approximately Fdco=24MHz, Fdcodiv=6MHz
    // .dismod = false,
    // .dcorsel = 5,
    // .flln = 183,
    // .flld = ucsCtl2Flld4,
    // .fllrefdiv = ucsCtl3Fllrefdiv1,
    // .selref = ucsCtl3SelrefREFOCLK
    //};
    //UCS_configureDco(UCS0, &dco_config);
    //UCS_MclkConfig_Struct mclk_config =
    //{
    // .selm = ucsCtl4SelmDCOCLK,
    // .divm = ucsCtl5Divm1,
    // .mclkreqen = true
    //};
    //UCS_configureMclk(UCS0, &mclk_config);
    //UCS_SmclkConfig_Struct smclk_config =
    //{
    // .sels = ucsCtl4SelsDCOCLKDIV,
    // .divs = ucsCtl5Divs1,
    // .smclkreqen = true
    //};
    //UCS_configureSmclk(UCS0, &smclk_config);
    //UCS_AclkConfig_Struct aclk_config =
    //{
    // .sela = ucsCtl4SelaREFOCLK,
    // .diva = ucsCtl5Diva4,
    // .divpa = ucsCtl5Divpa32,
    // .aclkreqen = true
    //};
    //UCS_configureAclk(UCS0, &aclk_config);
    IO_reset(P1);
    IO_reset(P2);
    IO_reset(P3);
    IO_reset(P4);
    IO_reset(P5);
    IO_reset(P6);
    IO_reset(P7);
    IO_reset(P8);
    IO_reset(PJ);
    LEDI_init();
    CM_init();
    IF_init();
    CA_init();
}

void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer,
                                    StackType_t **ppxIdleTaskStackBuffer,
                                    uint32_t *pulIdleTaskStackSize )
{
static StaticTask_t xIdleTaskTCB;
static StackType_t uxIdleTaskStack[ configMINIMAL_STACK_SIZE ];
    *ppxIdleTaskTCBBuffer = &xIdleTaskTCB;
    *ppxIdleTaskStackBuffer = uxIdleTaskStack;
    *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
}



int main(void)
{
    init();
    test();

    //ASSERT(false);

    vTaskStartScheduler();


    ASSERT(false);

}







#if defined(__TI_COMPILER_VERSION__) || (__IAR_SYSTEMS_ICC__)
#pragma vector = UNMI_VECTOR
__interrupt void UNMI_ISR (void)
#elif defined(__GNUC__) && (__MSP430__)
void __attribute__ ((interrupt(UNMI_VECTOR))) UNMI_ISR (void)
#else
#error Compiler not found!
#endif
{
    switch (__even_in_range(SYSUNIV, SYSUNIV_BUSIFG ))
    {
        case SYSUNIV_NONE:
            __no_operation();
            break;
        case SYSUNIV_NMIIFG:
            __no_operation();
            break;
        case SYSUNIV_OFIFG:
            UCS_clearFaultFlag(UCS_XT2OFFG);
            UCS_clearFaultFlag(UCS_DCOFFG);
            SFR_clearInterrupt(SFR_OSCILLATOR_FAULT_INTERRUPT);
            break;
        case SYSUNIV_ACCVIFG:
            __no_operation();
            break;
        case SYSUNIV_BUSIFG:
            // If the CPU accesses USB memory while the USB module is
            // suspended, a "bus error" can occur.  This generates an NMI.  If
            // USB is automatically disconnecting in your software, set a
            // breakpoint here and see if execution hits it.  See the
            // Programmer's Guide for more information.
            SYSBERRIV = 0; // clear bus error flag
            USB_disable(); // Disable
    }
}
