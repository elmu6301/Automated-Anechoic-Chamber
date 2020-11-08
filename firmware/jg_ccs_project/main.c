#include <msp430.h>

#include "app_assert.h"
#include "io.h"
#include "timer_a.h"
#include "interrupts.h"
#include "pulse_train.h"
#include "vcom.h"
#include "app_clocks.h"
#include "interface.h"
#include "find_reference.h"
#include "motor_driver.h"

/**
 * main.c
 */
int main(void)
{
    //Initialization code
	WDTCTL = WDTPW | WDTHOLD;	// stop watchdog timer
	INT_configureGie(false);
    IO_disableAllPins();
	CLOCKS_initialize();
	INT_initialize();
	MD_Configuration_Struct md_settings =
	{
	 .timer = TA0,
	 .step_port = ioPort1,
	 .step_pin = 2,
	 .dir_port = ioPort1,
	 .dir_pin = 4,
	 .res_port = ioPort1,
	 .res_pin = 5,
	 .sd_port = ioPort1,
	 .sd_pin = 6
	};
	MD_configure(&md_settings);
    INT_configureGie(true);

    bool command_in_waiting = false;
	VCOM_Init_Struct vcom_settings =
	{
	 .parity = uartParityNone,
	 .order = uartLsbFirst,
	 .data_bits = uartDataBits8,
	 .stop_bits = uartStopBits1,
	 .baud_rate = uartBaudRate115200
	};
    VCOM_initialize(&vcom_settings, &command_in_waiting);


	while(1)
	{
	    if(command_in_waiting)
	    {
	        INTERFACE_parseAndExecuteCommand();
	        command_in_waiting = false;
	    }
	}

	return 0;
}
