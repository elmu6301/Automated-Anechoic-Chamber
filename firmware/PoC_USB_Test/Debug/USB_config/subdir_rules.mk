################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
USB_config/%.obj: ../USB_config/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: MSP430 Compiler'
	"C:/ti/ccs1011/ccs/tools/compiler/ti-cgt-msp430_20.2.3.LTS/bin/cl430" -vmspx --data_model=restricted -O3 --use_hw_mpy=F5 --include_path="C:/ti/ccs1011/ccs/ccs_base/msp430/include" --include_path="C:/Users/elena/Documents/College/ECEN 4610 CAPSTONE/workspace_v10/PoC_USB_Test" --include_path="C:/Users/elena/Documents/College/ECEN 4610 CAPSTONE/workspace_v10/PoC_USB_Test/driverlib/MSP430F5xx_6xx" --include_path="C:/Users/elena/Documents/College/ECEN 4610 CAPSTONE/workspace_v10/PoC_USB_Test/USB_config" --include_path="C:/ti/ccs1011/ccs/tools/compiler/ti-cgt-msp430_20.2.3.LTS/include" --advice:power="none" --define=__MSP430F5529__ --define=DEPRECATED -g --printf_support=minimal --diag_warning=225 --diag_wrap=off --display_error_number --silicon_errata=CPU21 --silicon_errata=CPU22 --silicon_errata=CPU23 --silicon_errata=CPU40 --preproc_with_compile --preproc_dependency="USB_config/$(basename $(<F)).d_raw" --obj_directory="USB_config" $(GEN_OPTS__FLAG) "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


