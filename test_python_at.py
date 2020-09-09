import time
from datetime import datetime
import serial
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def send_command(device, cmd, status_validation=False, response_validation=False, repeat_cnt=1, wait_after_command=1.5):
	"""
	Send command to device, wait for answer and return response.
	Return dictionary with response and other information (should be object)

	:param device
	:param cmd
	:param status_validation #should validate status, if not OK, repeat or break
	:param response_validation #validate if response contain specific string
	:param repeat_cnt #repeats in case of validation failure
	:param wait_after_command #time in seconds for wait after command was sended to the device
	"""
	for loop_number in range(repeat_cnt):
		time.sleep(0.5) 	# technical break
		logging.info("Sending: %s | Loop: %d" % (cmd, loop_number))
		at_send_timestamp = datetime.timestamp(datetime.now())
		device.write(str.encode(cmd + '\r'))
		time.sleep(wait_after_command)
		for t in range(100):
			if device.in_waiting > 0:
				break
			time.sleep(0.1)
			logging.debug("Waiting for device buffer, bytes: %d" % device.in_waiting)
		at_response_timestamp = datetime.timestamp(datetime.now())
		logging.info("Data in device buffer: %d" % device.in_waiting)
		logging.info("Received response for: %s" % cmd)
		response = device.read(device.in_waiting).decode()
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
	logging.error("Sending AT command %s ended with error  \n -------------" % cmd)
	return False


def is_at_response_contains(response, search_str):
	for response_line in response:
		if search_str in response_line:
			logging.info("AT contains [%s]" % search_str)
			return 1
	logging.warning("AT response doesn't contains [%s]" % search_str)
	return 0


def simcom_ftp_check(device):

	#send_command(device, "AT+CNACT?", 1, False, 3)
	#return

	ip_command = "AT+CGDCONT=1,\"IP\",\"iot.static\""
	ping_cmd = "AT+SNPING4=\"51.83.45.158\",10,32,1000"

	commands = (
		["ATI", 1, False, 1],
		#["AT+CFUN=0", 1, False, 3],
		#["ATI", 1, False, 1],
		#["AT+CFUN=1", 1, False, 3],
		#["AT+CREG=0", 1, False, 1],
		#["AT+CREG?", 1, "+CREG: 0,1", 5],
		#["AT+CGDCONT?", 1, False, 1],
		#[ip_command, 1, False, 1],
		#["AT+CGDCONT?", 1, False, 1],
		#["AT+CNACT=1,1", 1, False, 5],
		#["AT+CNACT?", 1, False, 1],
		#["at+snpdpid=1", 1, False, 1],
		[ping_cmd, 0, False, 1]
	)
	send_command_set(device, commands)


def send_command_set(device, commands):
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


def send_TCP_data(device):
	send_command(device, "AT+CREG=0", True, False, 1, 1)
	send_command(device, "AT+CREG?", True, "+CREG: 0,1", 1, 1)
	send_command(device, "AT+CGACT?", True, False, 1, 2)
	send_command(device, "AT+CPSI?", True, False, 1, 0)
	send_command(device, "at+cncfg=0,1,\"iot.static\"", True, False, 1, 0)


def send_ping(device):
	ping_cmd = "AT+SNPING4=\"51.83.45.158\",5,32,1000"
	send_command(device, ping_cmd, True, False, 1, 10)


def test(device):
	send_command()


def main():
	device = serial.Serial("COM9", 115200, timeout=10)
	send_command(device, "AT+CFUN=0", True, False, 2, 3)
	send_command(device, "AT+CFUN=1", True, False, 2, 3)
	time.sleep(3)
	send_command(device, "AT+CPSI?", True, False, 1, 1)
	send_command(device, "at+cncfg=0,1,\"iot.static\"", True, False, 1, 1)
	if send_command(device, "at+cnact=0,1", True, False, 3, 1):
		time.sleep(1)
		bytes_to_send = 1400
		if send_command(device, "at+caopen=0,0,\"TCP\",\"51.83.45.158\",81", True, "+CAOPEN: 0,0", 3, 3):
			if send_command(device, "at+casend=0,%d" % bytes_to_send, False, False, 1, 0):
				time.sleep(1)
				send_command(device, "|" * bytes_to_send, True, "+CASEND: 0,0,%d" % bytes_to_send, 1, 1)

	send_command(device, "at+caclose=0", True, False, 1, 0)
	send_command(device, "at+cnact=0,0", True, False, 1, 1)


if __name__ == "__main__":
	main()