################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
src/source/%.o: ../src/source/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: GNU Compiler'
	"C:/ti/ccs1011/ccs/tools/compiler/msp430-gcc-9.2.0.50_win64/bin/msp430-elf-gcc-9.2.0.exe" -c -mmcu=msp430f5529 -mhwmult=f5series -I"C:/ti/ccs1011/ccs/ccs_base/msp430/include_gcc" -I"C:/Users/jgamm/Desktop/f2020/ecen4610/code_composer_workspace/ecen4610_firmware/src/headers" -I"C:/Users/jgamm/Desktop/f2020/ecen4610/code_composer_workspace/ecen4610_firmware" -I"C:/ti/ccs1011/ccs/tools/compiler/msp430-gcc-9.2.0.50_win64/msp430-elf/include" -Og -g -gdwarf-3 -gstrict-dwarf -Wall -Werror -mlarge -mcode-region=none -mdata-region=lower -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


