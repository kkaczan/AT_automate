import time
from datetime import datetime
import serial
import logging
logging.basicConfig(format='%(asctime)s %(message)s')


def send_command(device, cmd):
	# sends commands and returns response
	print("Sending: %s" % cmd)
	at_send_timestamp = datetime.timestamp(datetime.now())
	device.write(str.encode(cmd + '\r'))
	while device.in_waiting == 0:
		time.sleep(1)
	at_response_timestamp = datetime.now()
	time.sleep(0.5)
	response = device.read(device.in_waiting).decode()
	response = response.replace('\r', '')
	response = response.strip().split('\n')
	response_dict = {
		'response': response,
		'status': is_at_response_ok(response),
		'at_send_timestamp': at_send_timestamp,
		'at_response_timestamp':at_response_timestamp
	}
	print("Received: %s" % response_dict)
	print("------------------")
	return response_dict


def test():
	device = serial.Serial("COM9", 115200, timeout=10) 
	try:
		time.sleep(1)
		device.write(b'ATI\r')
		while device.in_waiting == 0:
			time.sleep(5)
		print("Bytes in buffer: " + str(device.in_waiting))
		print("[")
		print(device.read(device.in_waiting).decode('ascii', errors='replace'))
		print("]")
	finally:
		device.close()


def is_at_response_ok(response):
	for s in response:
		if s == 'OK':
			print("AT_response: OK")
			return 1
	print("AT_response: ERROR")
	return 0


def simcom_ftp_check(device):
	send_command(device, "ATI")
	send_command(device, "AT+COPS?")

def main():
	device = serial.Serial("COM9", 115200, timeout=10)
	simcom_ftp_check(device)
	#at_ati = send_command(device, "ATI")
	#at_cops = send_command(device, "AT+COPS?")



if __name__ == "__main__":
	main()