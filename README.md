## ACFA: Secure Runtime Auditing and Guaranteed Device Healing via Active Control Flow Attestation

Low-end embedded devices are increasingly used in a wide range of ``smart'' applications and spaces. They are implemented under strict cost and energy budgets, using microcontroller units (MCUs) that lack  security features akin to those available in general-purpose processors.
In this context, Remote Attestation (RA) was proposed as an inexpensive security service that enables a verifier (Vrf) to remotely detect illegal modifications to the software binary installed on a low-end prover MCU (Prv). Despite its effectiveness to validate Prv binary integrity, attacks that hijack the software's control flow (potentially leading to privilege escalation or code reuse attacks) cannot be detected by classic RA.

Control Flow Attestation (CFA)
augments RA with information about the exact order in which instructions in the binary are executed. As such, CFA enables detection of the aforementioned control flow attacks.
However, we observe that current CFA architectures can not guarantee that Vrf ever receives control flow reports in case of attacks. In turn, while they support detection of exploits, they provide no means to pinpoint the exploit origin. Furthermore, existing CFA requires either (1) binary instrumentation, incurring significant runtime overhead and code size increase; or (2) relatively expensive hardware support, such as hash engines. In addition, current techniques are neither continuous (they are only meant to attest small and self-contained operations) nor active (once compromises are detected, they offer no secure means to remotely remediate the problem).

To jointly address these challenges, we propose ACFA: a hybrid (hardware/software) architecture for Active CFA. ACFA enables continuous monitoring of all control flow transfers in the MCU and does not require binary instrumentation. It also leverages the recently proposed concept of ``active roots-of-trust'' to enable secure auditing of vulnerability sources and guaranteed remediation, in case of compromise detection.

This github repository provides an open-source reference implementation of ACFA on top of a commodity low-end MCU (TI MSP430) and evaluate it to demonstrate its security and cost-effectiveness.

## Dependencies Installation

Environment (processor and OS) used for development and verification:
Intel i7-3770
Ubuntu 18.04.3 LTS

Dependencies on Ubuntu:

		sudo apt-get install bison pkg-config gawk clang flex gcc-msp430 iverilog tcl-dev
		cd scripts
		sudo make install

## Building Software
To generate the Microcontroller program memory configuration containing VRASED trusted software (SW-Att) and sample applications we are going to use the Makefile inside the scripts directory:

        cd scripts

To build a specific test-case run:

        make "name of test-case"

For instance:

        make simple_app

to build the software including the binaries of simple_app test-case.
Note that this step will not run any simulation, but simply generate the MSP430 binaries corresponding to the test-case of choice.
As a result of the build, two files pmem.mem and smem.mem should be created inside msp_bin directory:

- pmem.mem program memory contents corresponding the application binaries

- smem.mem contains SW-Att binaries.

In the next steps, during synthesis, these files will be loaded to the MSP430 memory when we either: deploy ACFA on the FPGA or run ACFA simulation using VIVADO simulation tools.

If you want to clean the built files run:

        make clean

        Note: Latest Build tested using msp430-gcc (GCC) 4.6.3 2012-03-01

To test ACFA with a different application you will need to repeat these steps to generate the new "pmem.mem" file and re-run synthesis.

## Creating an ACFA project on Vivado and Running Synthesis

This is an example of how to synthesize and prototype ACFA using Basys3 FPGA and XILINX Vivado v2019.2 (64-bit) IDE for Linux

- Vivado IDE is available to download at: https://www.xilinx.com/support/download.html

- Basys3 Reference/Documentation is available at: https://reference.digilentinc.com/basys3/refmanual

#### Creating a Vivado Project for ACFA

1 - Clone this repository;

2 - Follow the steps in [Building ACFA Software](#building-ACFA-software) to generate .mem files for the application of your choice.

2- Start Vivado. On the upper left select: File -> New Project

3- Follow the wizard, select a project name and location. In project type, select RTL Project and click Next.

4- In the "Add Sources" window, select Add Files and add all .v and .mem files contained in the following directories of this reposiroty:

        openmsp430/fpga
        openmsp430/msp_core
        openmsp430/msp_memory
        openmsp430/msp_periph
        /vrased/hw-mod
        /msp_bin

and select Next.

Note that /msp_bin contains the pmem.mem and smem.mem binaries, generated in step [Building ACFA Software].

5- In the "Add Constraints" window, select add files and add the file

        openmsp430/contraints_fpga/Basys-3-Master.xdc

and select Next.

        Note: this file needs to be modified accordingly if you are running ACFA in a different FPGA.

6- In the "Default Part" window select "Boards", search for Basys3, select it, and click Next.

        Note: if you don't see Basys3 as an option you may need to download Basys3 to your Vivado installation.

7- Select "Finish". This will conclude the creation of a Vivado Project for ACFA.

Now we need to configure the project for systhesis.

8- In the PROJECT MANAGER "Sources" window, search for openMSP430_fpga (openMSP430_fpga.v) file, right click it and select "Set as Top".
This will make openMSP430_fpga.v the top module in the project hierarchy. Now its name should appear in bold letters.

9- In the same "Sources" window, search for openMSP430_defines.v file, right click it and select Set File Type and, from the dropdown menu select "Verilog Header".

Now we are ready to synthesize openmsp430 with ACFA hardware the following step might take several minutes.

10- On the left menu of the PROJECT MANAGER click "Run Synthesis", select execution parameters (e.g, number of CPUs used for synthesis) according to your PC's capabilities.

11- If synthesis succeeds, you will be prompted with the next step to "Run Implementation". You *do not* to "Run Implementation" if you only want simulate ACFA.
"Run implementation" is only necessary if your purpose is to deploy ACFA on an FPGA.

If you want to deploy ACFA on an FPGA, continue following the instructions on [Deploying ACFA on Basys3 FPGA].

If you want to simulate ACFA using VIVADO sim-tools, continue following the instructions on [Running ACFA on Vivado Simulation Tools].

## Running ACFA on Vivado Simulation Tools

After completing the steps 1-10 in [Creating a Vivado Project for ACFA]:

1- In Vivado, click "Add Sources" (Alt-A), then select "Add or create simulation sources", click "Add Files", and select everything inside openmsp430/simulation.

2- Now, navigate "Sources" window in Vivado. Search for "tb_openMSP430_fpga", and *In "Simulation Sources" tab*, right-click "tb_openMSP430_fpga.v" and set its file type as top module.

3- Go back to Vivado window and in the "Flow Navigator" tab (on the left-most part of Vivado's window), click "Run Simulation", then "Run Behavioral Simulation".

4- On the newly opened simulation window, select a time span for your simulation to run (see times for each default test-case below) and the press "Shift+F2" to run.

5- In the green wave window you will see values for several signals. The imporant ones are "exec", and "pc[15:0]". pc cointains the program counter value. exec corresponds to the value of ACFA's exec flag, as described in the paper.

In Vivado simulation, for all test-cases provided by default, the final value of pc[0:15] should correspond to the instruction address inside "success" function (i.e., the program should halt inside "success" function).

To determine the address of an instruction, e.g, addresses of the "success" function as well start and end addresses of ER (values of ER_min and ER_max, per ACFA's paper) one can check the compilation file at scripts/tmp-build/XX/vrased.lst  (where XX is the name of the test-case, i.e., if you ran "make simple_app", XX=simple_app). In this file search for the name of the function of interest, e.g., "success" or "dummy_function", etc.

#### NOTE: To simulate a different test-case you need to re-run "make test-case_name" to generate the corresponding pmem.mem file and re-run the synthesis step (step 10 in [Creating a Vivado Project for ACFA]) on Vivado. 

## Generate Bitstream

1- After Step 10 in [Creating a Vivado Project for ACFA], select "Run Implementation" and wait until this process completes (typically takes around 1 hour).

2- If implementation succeeds, you will be prompted with another window, select option "Generate Bitstream" in this window. This will generate the bitstream that is used to step up the FPGA according to VRASED hardware and software.

# ACFA Demo

The end-to-end demo showcases software that is vulnerable to buffer overflow, and demonstrates how ACFA generates periodic reports and allows for control flow auditing. During the demo, the vulnerable software and location of the exploit is determined momentarily after it has occurred, allowing Vrf to make a choice about remediation before allowing Prv to continue executing. 

In `demo_prv/main.c`, a buffer named `user_input` represents a stream of data read from input. In addition, Prv main software is unaware of the data. It compares this data to the buffer "pass" which contains a password. Prv software reads the stream by continuously saving the data until it receives a return char (`'\r'`). After this, it compares the user input to the password. If the password 

The entire end-to-end demo can be found in two directories: demo_prv and demo_vrf. The demo can be executed by either 'executing' in the Vivado simulator OR implementing ACFA on the Basys3 FPGA, generating a bitstream, and uploading to the FPGA. 

## Setup Angr

The ACFA demo makes use of Angr as a tool for binary analysis in the implementation of the verifier. Visit Angr official site for detailed instructions on installation: https://docs.angr.io/introductory-errata/install 

In addition, ACFA demo makes use of the msp430 extension for Angr found here:
https://github.com/angr/angr-platforms/tree/master/angr_platforms/msp430

## Using Vivado Simulator (fast option)

### Prv - Setup and compile Prv software

1- Select which version of the software to execute in `demo_prv/main.c`: non-attack scenario or buffer-overflow exploit. Define `user_input` using line 35 for the non-attack scenario, and use line '38' for the buffer-overflow exploit. Make sure to only have one of these lines active at a time by commenting-out the other.

2- the TCB is implemented in `vrased/sw-att/wrapper.c`. Edit line 87 to the following:
	`#define IS_SIM  SIM`

3- `cd` into `scripts` directory and execute `make demo`. Read the console output to ensure there are no errors.

### Prv - Execute Prv Software

1- `cd` into `logs` directory and delete or move any `.cflog` files (not including those in `past_runs` directory)

2- Follow previous instructions to simulate ACFA, and run the Vivado simulator for 55ms. You should see in the waveform window 4 triggers during execution.

3- After simulating, a set of reports will be saved in the `logs` directory. Verify that they were generated by visiting `logs` and finding four files: `0.cflog`, `0.cflog`, `1.cflog`, `2.cflog`, `3.cflog`.

### Vrf - Symbolically Execute Software

1- In this demo, Vrf does not know the code is incredibly vulnerable, sends it to prover anyway, and expects the non-attack scenario to occur. Vrf uses angr tool to symbolically execute the embedded software. If you created a python environment for angr after installing it, activate the angr environment with the following command: (If you installed it without a python environment, skip to step 2)
	`source [PATH TO ENVIRONMENT DIRECTORY]`
1b- To later exit the python environment, use the command `deactivate`

2- Then, in the directory `demo_vrf`, execute the python script `symbolic_exec.py`. This will generate (or update) the following files:
	- `sim.cflog`: contains the expected log entries generated by ACFA hardware for the given software.
	-  `acfa_exit_insts.log`: set of instructions in the last CFG block. Since ACFA generates an interrupt to trigger the TCB/protocol, it cannot be guaranteed that it will call the ISR at the same instruction, but ACFA guarantees it is always triggerd when the final block is reached. Therefore the entire block is saved for reference during CFLog verification.

3- Run the python script `vrf_log.py` to verify the validity of the CFlogs generated during the software execution (in Vivado Simulator) compared to the expected output. After one report has been inspected, press enter to verify the next one. The program continues until the last report has been received. This version of Vrf allows the Prv to continue executing always for the purpose of viewing all reports generated (even those detecting the attack)

## Using Basys3 FPGA Implementatino (realistic option)

### Prv - Setup and compile Prv software

1- Select which version of the software to execute in `demo_prv/main.c`: non-attack scenario or buffer-overflow exploit. Define `user_input` using line 35 for the non-attack scenario, and use line '38' for the buffer-overflow exploit. Make sure to only have one of these lines active at a time by commenting-out the other.

2- the TCB is implemented in `vrased/sw-att/wrapper.c`. Edit line 87 to the following:
	`#define IS_SIM  NOTSIM`

3- `cd` into `scripts` directory and execute `make demo`. Read the console output to ensure there are no errors.

### Synthesis, Implement, and Generate Bitstream

1- Follow the previous steps to Synthesis ACFA modules in Vivado

2- Follow the previous steps to Generate Bitstream.

### Start the Verifier

1- `cd` into `demo_vrf` and open the file `run_vrf.sh`. If you installed angr into a python environment, edit line 3 to reference the correct directory for your python environment. If you are not using a python environment, comment out lines 3 and 16.

2- Start the Vrf by executing the script `run_vrf.sh`. When the console output `'Starting protocol....'` appears, the Vrf is waiting for a report from the Prv.

### Start the Prv

1- In Vivado, upload the bitstream to the FPGA. As soon as it is uploaded, execution will begin. Select "Open Hardware Manager", connect the FPGA to you computer's USB port and click "Auto-Connect". Your FPGA should be now displayed on the hardware manager menu. Right-click your FPGA and select "Program Device" to program the FPGA.

### Read output

1- After this, the Prv will have finished executing. Reports sent to Vrf are saved in `demo_vrf` with the extension `.cflog`.

2- Output from the serial communication is saved in `prot.log`

## Demo Result
By running the version of the application that causes a buffer-overflow, anomalies will be detected and reported in the console. In the case of the buffer overflow example, The buffer overflow is detected at line 6 in `1.cflog`. More characters were read than expected, causing the loop of `read_data()` to execute eight times. In addition, the effect of the buffer overflow is seen at the next anamoly in line 9. The function `waitForPassword()` should return before the if statement (addr `0xe058`), but because of the buffer overflow the function returned to the 'Grant-Access condition' (addr `0xe06c`) without comparing the contents of `user_input` to `pass`.
