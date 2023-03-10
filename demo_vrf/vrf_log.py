import sys
from definitions import *

def vrf_log(report_num, sim_idx):
	print("----------------------------------------------------------------")
	print("----------------------- LOG VERIFICATION -----------------------")
	valid_cflog = 1
	# read sim.cflog 
	with open("sim.cflog", 'r') as sim_cflog_file:
		sim_cflog = sim_cflog_file.read().splitlines()

	# read acfa exit insts
	with open('acfa_exit_insts.log', 'r') as aei_file:
		acfa_exit_insts = aei_file.read().splitlines()

	last_src = "0000"
	last_dest = "0000"
	total_cf_data = 0

	## If this is not the first report received, need to verify this log starts where the previous log left off.
	exp_first_dest = ""
	if report_num != 0:
		with open("exp_first_dest.log", 'r') as file:
			exp_first_dest = file.read()
	exp_first_dest = exp_first_dest[:len(exp_first_dest)-1] #ignore eol

	report_filename = str(report_num)+".cflog"

	full_filename = APP_LOGS_PATH+report_filename

	## Open received log, add log to a list and initialize other data
	with open(full_filename) as cflog:
		recv_cflog = cflog.read().splitlines()
		cflog_ptr = int(recv_cflog[len(recv_cflog)-1])
		cflog_size = int(recv_cflog[len(recv_cflog)-1])
		recv_cflog = recv_cflog[:len(recv_cflog)-2]
	# print(cflog_ptr)
	# print(cflog_size)
	# print("first: "+str(recv_cflog[0]))
	# print("last: "+str(recv_cflog[cflog_size-1]))

	## Begin verification
	print("-------- Validating "+report_filename+" --------")
	if cflog_size == 1:
		# If cflog has 1 entry, it must be because this is the 'boot' trigger.
		if not recv_cflog[0][4:] == TCB_MIN:
			print(recv_cflog[0][4:]+" ?= "+TCB_MIN)
			print(recv_cflog[0][4:] == TCB_MIN)
		exp_first_dest = recv_cflog[0][:4]

	else:
		if report_num == 1:
			## If second report, first entry should be an expected value
			first_check = recv_cflog[0] == TCB_BOOT_RET_ENTRY
			if not first_check:
				valid_cflog = 0
				print("ANOMOLY DETECTED -- first entry of "+str(report_num)+".cflog")
				print(recv_cflog[0]+" ?= "+TCB_BOOT_RET_ENTRY)
		else:
			## Check if first entry is equal to expected value saved from previous verification
			first_check = recv_cflog[0][:4] == TCB_MAX and recv_cflog[0][4:] == exp_first_dest
			if not first_check:
				valid_cflog = 0
				print("ANOMOLY DETECTED -- first entry of "+str(report_num)+".cflog")
				print("or"+str(report_num)+" !> 1 or "+recv_cflog[0][:4]+" != "+TCB_MAX+" and "+recv_cflog[0][4:]+" != "+exp_first_dest)
				print(recv_cflog[0][:4] == TCB_MAX)
				print(recv_cflog[0][4:] == exp_first_dest)
				print(len(recv_cflog[0][4:]))
				print(len(exp_first_dest))

		i = 1
		## Debug pring
		# print("len(recv_cflog): "+str(len(recv_cflog)))
		# print("len(sim_cflog): "+str(len(sim_cflog)))

		## For all entries that are not first and last, compare to the sim.cflog (now in sim_cflog)
		while i < len(recv_cflog)-1 and sim_idx < len(sim_cflog):
			## Debug print
			# print(len(sim_cflog))
			# print(sim_idx)
			# print(len(recv_cflog))
			# print(i)

			if not (sim_cflog[sim_idx] == recv_cflog[i]):
				valid_cflog = 0
				print("ANOMOLY DETECTED -- intermediate entry: ")
				print("FALSE at log entry ("+str(i)+", "+str(sim_idx)+"): "+recv_cflog[i]+" ?= "+sim_cflog[sim_idx])
				# print(sim_cflog[i-1] == recv_cflog[i])
			i += 1
			sim_idx += 1

		# sim_idx += (i-1)
		# print("sim_idx: "+str(sim_idx))

		## Grab last entry
		lastentry = recv_cflog[len(recv_cflog)-1]
		last_src = lastentry[:4]
		last_dest = lastentry[4:]


		if last_dest == TCB_MIN:
			## If report generated by trigger, next report is valid if returns correctly from TCB
			## save the last source as the expected first destination for next report
			exp_first_dest = last_src

		else:
			## Otherwise, this should be the last report. Check if valid exit
			if not (last_dest== TCB_MIN and last_src in acfa_exit_insts):
				valid_cflog = 0
				print("ANOMOLY DETECTED: -- LAST ENTRY, simlog:"+str(sim_idx))
				print(last_dest+" ?= "+TCB_MIN+" AND "+last_src+" ?in "+str(acfa_exit_insts))
				print(last_dest== TCB_MIN and last_src in acfa_exit_insts)

	total_cf_data += cflog_size*4 #(entries * bytes per entry)
	print("Total Bytes of CF report_num: "+str(total_cf_data))

	# print(last_dest)
	# print(last_src)
	# print(acfa_exit_insts)
	last = 0
	if last_src in acfa_exit_insts:
		last = 1
		print("Program exit detected -- this is the last report")
	
	## Save expected dest to this file
	with open("exp_first_dest.log", 'w') as file:
		file.write("%s\n" % str(exp_first_dest))

	if valid_cflog :
		print("Valid CFLOG")
	print("-----------------------------------")

	return valid_cflog, sim_idx, last

if __name__ == '__main__':
	## Initialize script variables
	sim_idx = 0
	last = 0
	report_num = 0
	
	## Verify reports until last report is received
	while last == 0:
		valid_cflog, sim_idx, last = vrf_log(report_num, sim_idx)
		report_num += 1

		## Include this line incremental verification (pause & wait for user input between reports)
		if last == 0:
			a = input()