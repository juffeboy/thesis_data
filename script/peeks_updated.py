
import subprocess
import sys
from subprocess import Popen, PIPE
from os.path import expanduser
import time
from random import randint


home_path = expanduser("~")
sensor_address = "fd02::212:4b00:7a8:7185/1001"
ccnl_path = home_path + "/ccn-lite/bin/ccn-lite-peek"
content_path = "smotelmotel/"


def send_peek(data_seq, timeouts):
	send_path = content_path + str(data_seq)
	cmd_string = ccnl_path + " -w "+ str(timeouts) + " -p 1 -6 1 -s ndn2013 -u " + sensor_address + " " + send_path
	ping_peek = subprocess.Popen(cmd_string, stdout=subprocess.PIPE, shell=True)

	cmd_out, cmd_err = ping_peek.communicate()
	return cmd_out

def main():
	latest_seq = 1
	timeout = 1
	counter = 0
	#extra_delay_of_mote = 0.0046
	extra_delay_of_mote = 0.0079
	mote_interval = 1
	pit = False
	##pit = True 

	if (len(sys.argv) > 1):
		latest_seq = int(sys.argv[1])
	else:
		latest_seq = 1 
	while True:
		if (pit):
			latest_seq = randint(0,100)
			counter += 1
			send_peek(latest_seq, timeout)
			time.sleep(1)
		else:
			counter +=1 
			time_before = time.time()
			output = send_peek(latest_seq, timeout)
			time_after = time.time()
			total_delay = abs(mote_interval + time_before - time_after + extra_delay_of_mote)
			time.sleep(total_delay)
			latest_seq += 1
			print("REC:: ", output)	
			print("SEQ: " + str(latest_seq) + ", COUNTER: "+ str(counter))
		

if __name__ == '__main__':
	main()

