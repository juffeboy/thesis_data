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

def trim_request_intervall(seq):
	sent_under_intervall = 0
	rel_time = 0 
	temp_timeout = 0.5
	while True:
		s_peek = send_peek(seq, temp_timeout)
		sent_under_intervall = sent_under_intervall + 1
		p_peek = process_peek(s_peek)
		check_peek = int(p_peek)
		if (check_peek == -1): #check if timeout.
			# check if the next sequence has started.
			break
		elif (check_peek > 0):
			rel_time = rel_time + p_peek
	return rel_time	
		
def regular_request_intervall(start_seq):
	seq = start_seq
	sent_under_intervall = 0
	rel_time = mote_interval
	updated_rel_time = 0.0
	while True:
		## update...	
		updated_rel_time = mote_interval - trim_request_intervall(seq)
		seq = seq + 1
		## end update..
		s_peek = send_peek(seq, mote_interval)
		p_peek = prcess_peek(s_peek)
		check_peek = int(p_peek)
		if (check_peek == -1):
			#do something?
		elif (check_peek > 0):
			seq = seq + 1
			## print to log!!

def main():
	latest_seq = get_latest_seq(1)
	print("The latest SEQ is.. : ", latest_seq)


if __name__ == '__main__':
	main()
