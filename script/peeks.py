import subprocess
import sys
from subprocess import Popen, PIPE
import ast
import datetime 
import time
from os.path import expanduser

home_path = expanduser("~")

ccnl_path = home_path + "/ccn-lite/bin/ccn-lite-peek"
#ccnl_path = "/home/johanc/ccn-lite/bin/ccn-lite-peek"
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

def trim_req_time(seq):
	start_time = datetime.datetime.now()
	current_sent_time = datetime.datetime.now()
	prev_sent_time = current_sent_time
	total_time_spent = datetime.datetime.now()
	
	timeouts = 0
	
	last_seq_time_sent = 0
	current_seq_time_sent= 0
	temp_timeout = 0.5
	sent_number_of_requests = 0
	print("try to trim request time: ")
	while True:
		current_sent_time = datetime.datetime.now()
		s_peek = send_peek(seq, temp_timeout)
		sent_number_of_requests = sent_number_of_requests + 1
		p_peek = process_peek(s_peek)
		check_peek = int(float(p_peek))
		if (check_peek == -1):
			#do something
			timeouts = timeouts + 1
			prev_sent_time = current_sent_time
		elif (check_peek > 0):
			elapsed_time_to_ok = current_sent_time - prev_sent_time 	
			total_time_spent = current_sent_time - start_time
			break

	print("time elapsed between timeout and ok: ", elapsed_time_to_ok)
	print("Total time spend from start to ok: ", total_time_spent) 	
	return elapsed_time_to_ok
			


def regular_request_interval(start_seq):
	seq = start_seq
	sent_under_intervall = 0
	rel_time = mote_interval
	updated_rel_time = 0.0
	trim_time = 0
	print("Starting regular interval")
	while True:
		s_peek = send_peek(seq, mote_interval)
		p_peek = process_peek(s_peek)
		check_peek = int(float(p_peek))
		if (check_peek == -1):
			#do something?
			print("seqence: " + str(seq) + " got timeout")
		elif (check_peek > 0):
			seq = seq + 1
			print("seqence: " + str(seq) + " took: " + p_peek)
		## print to log!!
			
		## update...	
		if (seq%5==0): # for every fifth
			trim_time = trim_req_time(seq)
			seq = seq + 1
			print("seqence: " + str(seq) + " took: " + str(trim_time) + ". But was trimmed.")
			## print to log!!
			#updated_rel_time = mote_interval - trim_request_intervall(seq)

		## sleep
		time.sleep(mote_interval)

def main():
	latest_seq = get_latest_seq(1)
	print("The latest SEQ is.. : ", latest_seq)
	regular_request_interval(latest_seq)


if __name__ == '__main__':
	main()
