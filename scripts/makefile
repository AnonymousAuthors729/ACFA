default :

install-clean :
	rm -rf ./verif-tools/verilog2smv-1.1.2 ./verif-tools/verilog2smv.sh	

install :
	cd verif-tools ; \
	tar -vxjf verilog2smv-1.1.2.tar.bz2 ; \
	cd verilog2smv-1.1.2 ; \
	sh build.sh ; \
	cp verilog2smv.sh ../

simple_app :
	sh build/run "simple_app" true

cflow_test :
	sh build/run "cflow_test" true

demo :
	rm -f ../logs/*.cflog
	sh build/run "demo_prv" true

demo-terminal :
	rm -f ../logs/*.cflog
	sh build/run "demo_prv" false

ultrasonic_sensor:
	rm -f ../logs/*.cflog
	sh build/run "ultrasonic_sensor" false

temperature_sensor:
	rm -f ../logs/*.cflog
	sh build/run "temperature_sensor" true

syringe_pump:
	rm -f ../logs/*.cflog
	sh build/run "syringe_pump" true

test :
	sh build/run "test" true

clean :
	rm -rf simv *.mem pmem.inc stimulus.v tmp-build
