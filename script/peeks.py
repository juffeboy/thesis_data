import subprocess
import sys
from subprocess import Popen, PIPE
import ast
import datetime 
import time
from datetime import timedelta
from os.path import expanduser

home_path = expanduser("~")

ccnl_path = home_path + "/ccn-lite/bin/ccn-lite-peek"
#ccnl_path = "/home/johanc/ccn-lite/bin/ccn-lite-peek"
sensor_address = "fd02::212:4b00:7a8:7185/1001"
content_path = "smotelmotel/"
mote_interval = 1

def send_peek(data_seq, timeouts):
	send_path = content_path + str(data_seq)
	cmd_string = ccnl_path + " -w "+ str(timeouts) + " -p 1 -6 1 -s ndn2013 -u " + sensor_address + " " + send_path 
	ping_peek = subprocess.Popen(cmd_string, stdout=subprocess.PIPE, shell=True)
	cmd_out, cmd_err = ping_peek.communicate()
	#print("cmd_out: " + cmd_out)
	#if cmd_err:
	#	print("cmd_err: " + cmd_err)
	return cmd_out

def process_peek_return_string(in_peek):
	peek_info = in_peek.split(",")
	if (len(peek_info) > 0):
		if "timeout" in in_peek:
			return "timeout"
		else:
			return in_peek.rstrip('\n')	

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
					return t.rstrip('\n')
	else:
		return "-1"


def get_latest_seq(start_seq):
	#print("probeing..")
	found_one = False
	seq = start_seq
	while True:
		print("probeing.. " + str(seq))
		s_peek = send_peek(seq, 0.1)
		p_peek = int(float(process_peek(s_peek)))
		if ((p_peek == -1) and found_one):
			#timeout
			#seq = seq - 1 
			break
		elif (p_peek > 0):
			found_one = True
		seq = seq+1
	return seq

def trim_req_time(seq):
	t_start = time.time()
	prev_t_sent = 0
	current_t_sent = 0
	rtt_time = 0
	rec_t = 0 # the time when the message was `recieved``
	timeouts = 0 
	temp_timeout = 0.3
	sent_number_of_requests = 0
	print("try to trim request time: ")

	while True:
		current_t_sent = time.time()
		s_peek = send_peek(seq, temp_timeout)
		sent_number_of_requests = sent_number_of_requests + 1
		up_peek = process_peek_return_string(s_peek)
		if (up_peek == "timeout"):
			#do something
			print(" uppeek got : " + up_peek)
			timeouts = timeouts + 1
			prev_t_sent = current_t_sent
		else:
			elapsed_time_to_ok = current_t_sent - prev_t_sent 	
			total_time_spent = current_t_sent - t_start
			rec_t = time.time()
			rtt_time = rec_t - current_t_sent
			break
	print("time elapsed between timeout and ok: "+ str(elapsed_time_to_ok) + ". Last RTT-time: "+ str(rtt_time))
	print("Total time spend from start to ok(in seconds): " + str(total_time_spent) + ". # of Timeouts: "+str(timeouts)) 	
	return (total_time_spent, elapsed_time_to_ok, rtt_time)	

def small_steps(start_seq):
	seq = start_seq
	shorten_per_interval = 0.10
	extra_delay_of_mote = 0.0046
	trim_interval = 100
	timed_out = False
	shorting_stopped = False
	interval_stop = 2400
	while (seq<interval_stop):
		t_start = time.time()
		s_peek = send_peek(seq, mote_interval)
		p_peek = process_peek(s_peek)
		up_peek = process_peek_return_string(s_peek)
		check_peek = int(float(p_peek))
		optional_extra_time = 0

		if (check_peek == -1):
		#if (up_peek == "timeout"):
			print("seqence: " + str(seq) + " got timeout")
			s_peek = send_peek(seq, mote_interval)
			p_peek = process_peek(s_peek)
			up_peek = process_peek_return_string(s_peek)
			if (up_peek == "timeout"):
				print("seqence: " + str(seq) + " got timeout... AGAIN!") 
			else:
				print("seqence: " + str(seq) + " took: " + p_peek + " . Sending OK, but it got timeout the first time!")	
			timed_out = True

		elif (check_peek > 0):
			# we got the right packet et.c....
			print("seqence: " + str(seq) + " took: " + p_peek)

		if (seq%trim_interval==0):
			print("will start trimming from next seq.")
			timed_out = False
			shorting_stopped = False

		if (timed_out):
			timed_out = False
			shorting_stopped = True
			print("came into timed_out")
			optional_extra_time = +shorten_per_interval	
		elif shorting_stopped:
			print("shorting_stopped")
			optional_extra_time = 0
		else:
			print("shorting interval time with speed: "+str(shorten_per_interval))
			optional_extra_time = -shorten_per_interval	

		t_rec = time.time()
		t_elapsed = t_rec - t_start
		t_total_sleep = abs(mote_interval + t_start - t_rec + extra_delay_of_mote + optional_extra_time)
		seq = seq+1
		print("time interval: "+ str(t_elapsed) + ". mote_interval + t_st - t_rec = " + str(mote_interval) + " + " + str(t_start) + "+ " + str(t_rec) + " = " + str(mote_interval + t_start - t_rec) + ", or :" + str(t_total_sleep) + '\n')
		
		time.sleep(t_total_sleep)
		#time.sleep(t_elapsed)	

def reg_request_interval(start_seq):
	seq = start_seq
	sent_under_interval = 0
	extra_delay_of_mote = 0.0046
	trim_interval = 20

	timed_out = False
	print("Starting regular interval")

	while seq<2400:
		t_start = time.time()
		trimmed	= False
		s_peek = send_peek(seq, mote_interval)
		p_peek = process_peek(s_peek)
		up_peek = process_peek_return_string(s_peek)
		check_peek = int(float(p_peek))

		#if (check_peek == -1):
		if (up_peek == "timeout"):
			print("sequence: " + str(seq) + " got timeout")
			s_peek = send_peek(seq, mote_interval)
			p_peek = process_peek(s_peek)
			up_peek = process_peek_return_string(s_peek)
			if up_peek == "timeout":
				print("seqence: " + str(seq) + " got timeout... AGAIN!") 
			else:
				print("seqence: " + str(seq) + " took: " + p_peek + " . Sending OK, but it got timeout the first time!")	
			timed_out = True
		elif(check_peek > 0):
			print("sequence: " + str(seq) + " took: " + p_peek)

		if (seq%trim_interval==0):
			t_before_trim = time.time()
			sleep_before_trim = (mote_interval + t_start - t_before_trim)/2 
			print("TRIMMING")
			print("time_to_sleep_before_trim: " + str(sleep_before_trim))
			time.sleep(sleep_before_trim)

			seq = seq + 1
			trim_time = trim_req_time(seq)
			print("seqence: " + str(seq) + " took: " + str(trim_time[0]) + ". But was trimmed, The sleep before was " + str(sleep_before_trim))
			trimmed = True

		optional_extra_time = 0
		t_end = time.time()
		t_elapsed = t_end - t_start
		t_total_sleep = mote_interval + t_start - t_end + extra_delay_of_mote + optional_extra_time
		if (timed_out):
			timed_out = False
			if (t_total_sleep < 0) or (t_total_sleep > 3):
				print("timed out out of bounds: " + str(t_total_sleep))
				t_total_sleep = abs(t_total_sleep) 
		if (trimmed):
			optional_extra_time = trim_time[2]
			t_total_sleep = mote_interval - optional_extra_time + extra_delay_of_mote
			print("trimmedddd, optional time: " + str(optional_extra_time) + "t_total_time with 2*: " + str(t_total_sleep))

		print("t_total_sleep: "+ str(t_total_sleep) + " time interval: " + str(t_elapsed) + ". mote_interval + t_start - t_end + extra_delay_mote =  " + str(mote_interval) + " + " + str(t_start) + " - " + str(t_end) + " +- " + str(extra_delay_of_mote) + "\n")
		seq = seq + 1
		time.sleep(t_total_sleep)

def main():
	latest_seq = 1
	if (len(sys.argv) > 1):
		latest_seq = int(get_latest_seq(int(sys.argv[1])))
	else:
		latest_seq = get_latest_seq(1)
	time.sleep(mote_interval)
	print("The latest SEQ is.. : ", latest_seq)
	#reg_request_interval(latest_seq)
	small_steps(latest_seq)

if __name__ == '__main__':
	main()
