import os
import sys, argparse
import time, datetime
import csv

import serial
import serial.tools.list_ports as listPorts

#la magia del teclado en unix y windows
import kb_handler

_menu_ = """========================
Commands:
[L/l] LED on/off
[H/h] Horno on/off
[+]   Muestreo - 10ms
[-]   Muestreo + 10ms
[S/s] Start/Pause test
[ESC] Finish test and exit
========================"""

_clearcmd_ = "cls" if os.name == "nt" else "clear"

result_fname = "out.csv"
_running_ = False
_sampling_ = 250
_led_ = False
_horno_ = False
_sensor_ = 0

#windows only
def arduinoSerial():
	portname = ""
	for port in listPorts.comports():
		if("Arduino" in port[1]):
			portname = port[0]
			break
		if("COM" in port[1] and "COM1" not in port[1]):
			portname = port[0]
			break
		if("ttyUSB" in port[0]):
			portname = port[0]
			break

	return portname

def printMenu(cmds):
	global _clearcmd_
	os.system(_clearcmd_)
	if cmds:
		print(_menu_)
	printResults(result_fname,_running_, _sampling_, _led_, _horno_, _sensor_)
		
def printResults(file,state, samples, led, horno, sens):
	print("out=>\t\t{0}".format(file))
	print("Estado=>\t{0}".format("Running" if state else "Paused"))
	print("Muestreo=>\t{0}".format(samples))
	print("LED=>\t\t{0}".format("ON" if led else "OFF"))
	print("Horno=>\t\t{0}".format("ON" if horno else "OFF"))
	print("Sensor=>\t{0}".format(sens))

def main(argv):
	global result_fname
	global _running_
	global _sampling_
	global _led_
	global _horno_
	global _sensor_
	
	pr_cmds = False
	#Parser de las opciones de linea de comando
	parser = argparse.ArgumentParser()
	#opciones
	parser.add_argument("-o", "--output", help="name of the file storing the results (def=out.csv)")
	parser.add_argument("-c", "--commands",action="store_true", help="print usable commands above results")
	args = parser.parse_args()
	#procesa opciones
	if args.output:
		result_fname = args.output
	if args.commands:
		pr_cmds = True
	
	#setup stuff
	kb = kb_handler.KBHit()
	ser = serial.Serial()
	baudrate = 19200
	portname = arduinoSerial()
	if(not portname == ""):
		try:
			ser = serial.Serial(portname, baudrate, timeout=2)
			
			#Puerto serial abierto correctamente, control del arduino:
			with open(result_fname, "a") as ofile:
				ofile.write("Time\tdelay\tLED\tHorno\tSensor" + "\tdate: " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
				notdone = True
				while notdone:
					printMenu(pr_cmds)
					#control
					while kb.kbhit():
						k = kb.getch()
						if k in ['L', 'l']:
							_led_ = not _led_
							ser.write(b'L' if _led_ == True else b'l')
						elif k in ['H', 'h']:
							_horno_ = not _horno_
							ser.write(b'H' if _horno_ == True else b'h')
						elif k == '+':
							_sampling_ = _sampling_ - 10 if _sampling_ > 20 else _sampling_
							ser.write(b'+')
						elif k == '-':
							_sampling_ = _sampling_ + 10 if _sampling_ < 1000 else _sampling_
							ser.write(b'-')
						elif k in ['S', 's']:
							_running_ = not _running_
							ser.write(b'S' if _running_ == True else b's')
						elif ord(k) == 27:
							if _running_:
								ser.write(b's') #stop comm
							if ser.isOpen():
								ser.close()
							print("Nighty night!!")
							notdone = False
							break
					if not notdone: #doble negacion
						break
						
					#reception de datos seriales
					
					datareceived = False
					serline = ""
					#espera a tener al menos una linea completa
					
					while ser.inWaiting():
						serline = ser.readline().decode("utf-8").rstrip()
						ofile.write(serline + '\n')
						datareceived = True
					ofile.flush()
					
					#obtiene dato de sensor
					if datareceived:
						cols = serline.split('\t')
						try:
							_sensor_ = int(cols[-1])
						except:
							_sensor_ = "Error parsing sensor data"
						#print (cols)
					
					
					#print to file the header:
					#  Serial.println("Time\tdel\tLd\tHn\tVal");
					
					time.sleep(0.1) #30FPS no matter what
				
		except Exception as error:
			#print("Error opening serial port: {0}".format(portname))
			#if(ser is not None and ser.isOpen()):
			#	ser.close()
			
			print('caught this error: ' + repr(error))
			exit()
	else:
		print("Arduino not found")
		exit()

if __name__ == "__main__" :
	main(sys.argv)
	
