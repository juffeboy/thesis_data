import subprocess
import sys
from subprocess import Popen, PIPE
import ast

ccnl_path = "/home/johanc/ccn-lite/bin/ccn-lite-peek"
sensor_address = "fd02::212:4b00:7a8:7185/1001"
content_path = "s"
mote_interval = 3

def send_peek(data_seq, timeouts):
	send_path = content_path + "/"+str(data_seq)
	cmd_string = ccnl_path + " -w "+ str(timeouts) + " -p 1 -6 1 -s ndn2013 -u " + sensor_address + " " + send_path 
	ping_peek = subprocess.Popen(cmd_string, stdout=subprocess.PIPE, shell=True)
	cmd_out, cmd_err = ping_peek.communicate()
	#print("cmd_out: " + cmd_out)
	#if cmd_err:
	#	print("cmd_err: " + cmd_err)
	return cmd_out

def process_peek(in_peek):
	peek_info = in_peek.split(",") 
	if (len(peek_info) > 0): 
	#print(peek_info)
		for part in peek_info:
			if "time=" in part:
				splitted_part = part.split("=")
				t = splitted_part[1]
				if (t == "timeout\n"):
					#print("TIMEOOUUUUT")
					return "-1"
				else:
					return t
	else:
		return "-1"


def get_latest_seq(start_seq):
	#print("probeing..")
	found_one = False
	seq = start_seq
	while True:
		print("probeing.. " + str(seq))
		s_peek = send_peek(seq, 0.5)
		p_peek = int(float(process_peek(s_peek)))
		if ((p_peek == -1) and found_one):
			#timeout
			break
		elif (p_peek > 0):
			found_one = True
		seq = seq+1
	return seq




def main():
	latest_seq = get_latest_seq(1)
	print("The latest SEQ is.. : ", latest_seq)










if __name__ == '__main__':
	main()
