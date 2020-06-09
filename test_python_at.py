import time
from datetime import datetime
import serial
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)


def send_command(device, cmd, status_validation=False, response_validation=False, repeat_cnt=1):
	# send at command and returns response
	for loop_number in range(repeat_cnt):
		time.sleep(0.5) 	# technical break
		logging.info("Sending: %s | Loop: %d" % (cmd, loop_number))
		at_send_timestamp = datetime.timestamp(datetime.now())
		device.write(str.encode(cmd + '\r'))
		while device.in_waiting == 0:
			time.sleep(0.01)
		at_response_timestamp = datetime.timestamp(datetime.now())
		logging.info("Received response for: %s" % cmd)
		response = device.read(device.in_waiting).decode()
		device.in_waiting
		response = response.replace('\r', '')
		response = response.strip().split('\n')
		response_dict = {
			'command': cmd,
			'response': response,
			'status': is_at_response_contains(response, "OK"),
			'at_send_timestamp': at_send_timestamp,
			'at_response_timestamp': at_response_timestamp,
			'loop_number': loop_number
		}
		logging.info("Received: %s" % response_dict)
		# status validation (check if we have OK in command response)
		if status_validation:
			if response_dict["status"] != 1:
				logging.warning("Response status not valid: [OK] is missed")
				continue
		# response validation (check if we have valid string in command response)
		if response_validation:
			if is_at_response_contains(response_dict["response"], response_validation) == 0:
				logging.warning("Response doesn't contains %s" % response_validation)
				continue
			else:
				logging.info("Sending AT command %s ended with success \n -------------" % cmd)
				return response_dict
		else:
			logging.info("Sending AT command %s ended with success \n -------------" % cmd)
			return response_dict
	logging.error("Sending AT command %s ended with error" % cmd)
	return False


def is_at_response_contains(response, search_str):
	for response_line in response:
		if response_line == search_str:
			logging.info("AT contains [%s]" % search_str)
			return 1
	logging.warning("AT response doesn't contains %s" % search_str)
	return 0


def simcom_ftp_check(device):

	#send_command(device, "AT+CNACT?", 1, False, 3)
	#return

	ip_command = "AT+CGDCONT=1,\"IP\",\"iot.static\""

	commands = (
		["ATI", 1, "OK", 1],
		["AT+CFUN=0", 1, "OK", 3],
		["ATI", 1, "OK", 1],
		["AT+CFUN=1", 1, "OK", 3],
		["AT+CREG=0", 1, "OK", 1],
		["AT+CREG?", 1, "+CREG: 0,1", 5],
		["AT+CGDCONT?", 1, "OK", 1],
		[ip_command, 1, "OK", 1],
		["AT+CGDCONT?", 1, "OK", 1],
		["AT+CNACT=1,1", 1, "OK", 5],
		["AT+CNACT?", 1, "OK", 1]
		#["at+snpdpid=1", 1, "OK"],
		#["at+snping4=\"51.83.45.158\",10,32,1000 ", 1]
	)
	send_command_set(commands, device)


def send_command_set(commands, device):
	# command defined as: [command, status, response_contains]
	break_on_error = True
	logging.info("Start executing command set: %s" % str(commands))
	# execute commands set
	for cmd in commands:
		# execute command
		cmd_res = send_command(device, cmd[0], cmd[1], cmd[2], cmd[3])
		if break_on_error and cmd_res == False:
			logging.error("Command error in command set")
			break
		time.sleep(1)
	logging.info("Stop executing commands set")


def main():
	device = serial.Serial("COM9", 115200, timeout=10)
	simcom_ftp_check(device)


if __name__ == "__main__":
	main()