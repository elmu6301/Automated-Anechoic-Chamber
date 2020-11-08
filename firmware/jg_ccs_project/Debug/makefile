################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

CG_TOOL_ROOT := C:/ti/ccs1011/ccs/tools/compiler/msp430-gcc-9.2.0.50_win64

GEN_OPTS__FLAG := 
GEN_CMDS__FLAG := 

ORDERED_OBJS += \
"./main.o" \
"./src/source/app_assert.o" \
"./src/source/app_clocks.o" \
"./src/source/delay.o" \
"./src/source/find_reference.o" \
"./src/source/interface.o" \
"./src/source/interrupts.o" \
"./src/source/io.o" \
"./src/source/motor_driver.o" \
"./src/source/pulse_train.o" \
"./src/source/timer_a.o" \
"./src/source/timer_b.o" \
"./src/source/uart.o" \
"./src/source/ucs.o" \
"./src/source/vcom.o" \
-T"../msp430f5529.ld" \
$(GEN_CMDS__FLAG) \
-Wl,--start-group \
-lgcc \
-lc \
-Wl,--end-group \

-include ../makefile.init

RM := DEL /F
RMDIR := RMDIR /S/Q

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir_vars.mk
-include src/source/subdir_vars.mk
-include subdir_rules.mk
-include src/source/subdir_rules.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C55_DEPS)),)
-include $(C55_DEPS)
endif
ifneq ($(strip $(C_UPPER_DEPS)),)
-include $(C_UPPER_DEPS)
endif
ifneq ($(strip $(S67_DEPS)),)
-include $(S67_DEPS)
endif
ifneq ($(strip $(S62_DEPS)),)
-include $(S62_DEPS)
endif
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(OPT_DEPS)),)
-include $(OPT_DEPS)
endif
ifneq ($(strip $(C??_DEPS)),)
-include $(C??_DEPS)
endif
ifneq ($(strip $(ASM_UPPER_DEPS)),)
-include $(ASM_UPPER_DEPS)
endif
ifneq ($(strip $(S??_DEPS)),)
-include $(S??_DEPS)
endif
ifneq ($(strip $(C64_DEPS)),)
-include $(C64_DEPS)
endif
ifneq ($(strip $(CXX_DEPS)),)
-include $(CXX_DEPS)
endif
ifneq ($(strip $(S64_DEPS)),)
-include $(S64_DEPS)
endif
ifneq ($(strip $(INO_DEPS)),)
-include $(INO_DEPS)
endif
ifneq ($(strip $(CLA_DEPS)),)
-include $(CLA_DEPS)
endif
ifneq ($(strip $(S55_DEPS)),)
-include $(S55_DEPS)
endif
ifneq ($(strip $(SV7A_DEPS)),)
-include $(SV7A_DEPS)
endif
ifneq ($(strip $(C62_DEPS)),)
-include $(C62_DEPS)
endif
ifneq ($(strip $(C67_DEPS)),)
-include $(C67_DEPS)
endif
ifneq ($(strip $(PDE_DEPS)),)
-include $(PDE_DEPS)
endif
ifneq ($(strip $(K_DEPS)),)
-include $(K_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
ifneq ($(strip $(CC_DEPS)),)
-include $(CC_DEPS)
endif
ifneq ($(strip $(C++_DEPS)),)
-include $(C++_DEPS)
endif
ifneq ($(strip $(C43_DEPS)),)
-include $(C43_DEPS)
endif
ifneq ($(strip $(S43_DEPS)),)
-include $(S43_DEPS)
endif
ifneq ($(strip $(ASM_DEPS)),)
-include $(ASM_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(CPP_DEPS)),)
-include $(CPP_DEPS)
endif
ifneq ($(strip $(SA_DEPS)),)
-include $(SA_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
EXE_OUTPUTS += \
ecen4610_firmware.out \

EXE_OUTPUTS__QUOTED += \
"ecen4610_firmware.out" \

BIN_OUTPUTS += \
ecen4610_firmware.hex \

BIN_OUTPUTS__QUOTED += \
"ecen4610_firmware.hex" \


# All Target
all: $(OBJS) $(LD_SRCS) $(GEN_CMDS)
	@$(MAKE) --no-print-directory -Onone "ecen4610_firmware.out"

# Tool invocations
ecen4610_firmware.out: $(OBJS) $(LD_SRCS) $(GEN_CMDS)
	@echo 'Building target: "$@"'
	@echo 'Invoking: GNU Linker'
	"C:/ti/ccs1011/ccs/tools/compiler/msp430-gcc-9.2.0.50_win64/bin/msp430-elf-gcc-9.2.0.exe" -mhwmult=f5series -Og -g -gdwarf-3 -gstrict-dwarf -Wall -Werror -mcode-region=none -mlarge -Wl,-Map,"ecen4610_firmware.map" -Wl,--gc-sections -L"C:/ti/ccs1011/ccs/ccs_base/msp430/include_gcc" -mmcu=msp430f5529 -o"ecen4610_firmware.out" $(ORDERED_OBJS)
	@echo 'Finished building target: "$@"'
	@echo ' '

ecen4610_firmware.hex: $(EXE_OUTPUTS)
	@echo 'Building files: $(strip $(EXE_OUTPUTS__QUOTED))'
	@echo 'Invoking: GNU Objcopy Utility'
	"C:/ti/ccs1011/ccs/tools/compiler/msp430-gcc-9.2.0.50_win64/bin/msp430-elf-objcopy.exe"  $(EXE_OUTPUTS__QUOTED) "ecen4610_firmware.hex"
	@echo 'Finished building: $(strip $(EXE_OUTPUTS__QUOTED))'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(BIN_OUTPUTS__QUOTED)$(EXE_OUTPUTS__QUOTED)
	-$(RM) "main.o" "src\source\app_assert.o" "src\source\app_clocks.o" "src\source\delay.o" "src\source\find_reference.o" "src\source\interface.o" "src\source\interrupts.o" "src\source\io.o" "src\source\motor_driver.o" "src\source\pulse_train.o" "src\source\timer_a.o" "src\source\timer_b.o" "src\source\uart.o" "src\source\ucs.o" "src\source\vcom.o" 
	-$(RM) "main.d" "src\source\app_assert.d" "src\source\app_clocks.d" "src\source\delay.d" "src\source\find_reference.d" "src\source\interface.d" "src\source\interrupts.d" "src\source\io.d" "src\source\motor_driver.d" "src\source\pulse_train.d" "src\source\timer_a.d" "src\source\timer_b.d" "src\source\uart.d" "src\source\ucs.d" "src\source\vcom.d" 
	-@echo 'Finished clean'
	-@echo ' '

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets

