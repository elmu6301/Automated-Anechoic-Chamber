################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
FreeRTOS/Source/%.obj: ../FreeRTOS/Source/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: MSP430 Compiler'
	"C:/ti/ccs1011/ccs/tools/compiler/ti-cgt-msp430_20.2.1.LTS/bin/cl430" -vmspx --code_model=large --data_model=restricted --near_data=none -O0 --use_hw_mpy=F5 --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/USB_config" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/FreeRTOS" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/FreeRTOS/Source/include" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/FreeRTOS/Source/portable/CCS/MSP430X" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/app/headers" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/hal/headers" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/hil/headers" --include_path="C:/ti/ccs1011/ccs/ccs_base/msp430/include" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware" --include_path="C:/Users/jgamm/Desktop/sp2021/ecen_4620/ecen4620_firmware/driverlib/MSP430F5xx_6xx" --include_path="C:/ti/ccs1011/ccs/tools/compiler/ti-cgt-msp430_20.2.1.LTS/include" --advice:power=all --define=__MSP430F5529__ -g --printf_support=minimal --diag_warning=225 --diag_wrap=off --display_error_number --silicon_errata=CPU21 --silicon_errata=CPU22 --silicon_errata=CPU23 --silicon_errata=CPU40 --preproc_with_compile --preproc_dependency="FreeRTOS/Source/$(basename $(<F)).d_raw" --obj_directory="FreeRTOS/Source" $(GEN_OPTS__FLAG) "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


