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
content_path = "smotelmotel/"
mote_interval = 3

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
	start_time = datetime.datetime.now()
	current_sent_time = datetime.datetime.now()
	prev_sent_time = current_sent_time
	#total_time_spent = datetime.datetime.now()
	
	timeouts = 0
	
	last_seq_time_sent = 0
	current_seq_time_sent= 0
	temp_timeout = 0.3
	sent_number_of_requests = 0
	print("try to trim request time: ")
	while True:
		current_sent_time = datetime.datetime.now()
		s_peek = send_peek(seq, temp_timeout)
		sent_number_of_requests = sent_number_of_requests + 1
		up_peek = process_peek_return_string(s_peek)
		if (up_peek == "timeout"):
			#do something
			print(" uppeek got : " + up_peek)
			timeouts = timeouts + 1
			prev_sent_time = current_sent_time
		else:
			elapsed_time_to_ok = current_sent_time - prev_sent_time 	
			total_time_spent = current_sent_time - start_time
			break

	print("time elapsed between timeout and ok: ", elapsed_time_to_ok)
	#print("Total time spend from start to ok: ", total_time_spent) 	
	print("Total time spend from start to ok(in seconds): " + str( total_time_spent.total_seconds()) + ". # of Timeouts: "+str(timeouts)) 	
	#return elapsed_time_to_ok
	return (total_time_spent.total_seconds(), elapsed_time_to_ok.total_seconds())
			


def regular_request_interval(start_seq):
	seq = start_seq
	sent_under_intervall = 0
	rel_time = mote_interval
	updated_rel_time = 0.0
	trim_time = 0
	info_to_be_printed = ""
	print("Starting regular interval")

	while True:
		start_interval_time = datetime.datetime.now()
		trimmed = False 
		s_peek = send_peek(seq, mote_interval)
		p_peek = process_peek(s_peek)
		up_peek = process_peek_return_string(s_peek)
		check_peek = int(float(p_peek))
		if (check_peek == -1):
			#do something?
			#print(""  + up_peek)
			
			info_to_be_printed = "seqence: " + str(seq) + " got timeout" 
			#print("seqence: " + str(seq) + " got timeout")
		elif (check_peek > 0):
			# we got the right packet et.c....
			#print(""  + up_peek)
			info_to_be_printed = "seqence: " + str(seq) + " took: " + p_peek
			#print("seqence: " + str(seq) + " took: " + p_peek)
			
		## update...	
		if (seq%5==0): # for every fifth
			# sleep some
			time_before_trim = datetime.datetime.now()
			time_to_sleep_before_trim = time_before_trim - start_interval_time
			time_to_sleep_before_trim = time_to_sleep_before_trim.total_seconds()
			sleep_before = float((mote_interval - time_to_sleep_before_trim) / 2) ## den har ror till det pa ett positivt satt.
			#sleep_before = float(2*mote_interval/3) - time_to_sleep_before_trim ## blir valdigt konstant rorelse.
			#sleep_before = float(2*(mote_interval - time_to_sleep_before_trim) / 3)
			print("time_to sleep: " + str(sleep_before) + ",  time_to_sleep: " + str(time_to_sleep_before_trim))
			time.sleep(sleep_before)
			## only sleep half of this time.

			seq = seq + 1
			trim_time = trim_req_time(seq)
			print("seqence: " + str(seq) + " took: " + str(trim_time[0]) + ". But was trimmed.")
			trimmed = True
			## print to log!!
			#updated_rel_time = mote_interval - trim_request_intervall(seq)

		## sleep
		end_interval_time = datetime.datetime.now()
		elapsed_interval_time = end_interval_time - start_interval_time
		interval_time = format(mote_interval - elapsed_interval_time.total_seconds(), '.2f')
		if (trimmed):
			interval_time = format(mote_interval - trim_time[1], '.2f')
			if (interval_time < 0) or (interval_time > 3): 
				interval_time = mote_interval 

		print(info_to_be_printed + ". \ntotal time spent in interval : " + str(elapsed_interval_time.total_seconds()) + ". \nMote_interval - interval_time: " + str(interval_time) + '\n')
		#time.sleep(mote_interval - interval_time)
		seq = seq + 1
		time.sleep(float(interval_time))

def little_less_per_interval(start_seq):
	seq = start_seq
	shorten_per_interval = 0.1
	timed_out = False
	stop_shorting = False

	while True:
		start_interval_time = datetime.datetime.now()
		s_peek = send_peek(seq, mote_interval)
		p_peek = process_peek(s_peek)
		up_peek = process_peek_return_string(s_peek)
		check_peek = int(float(p_peek))
		
		if (check_peek == -1):
			#do something?
			## resend.
			print("seqence: " + str(seq) + " got timeout") 
			
			s_peek = send_peek(seq, mote_interval)
			p_peek = process_peek(s_peek)
			up_peek = process_peek_return_string(s_peek)
			
			if up_peek == "timeout":
				print("seqence: " + str(seq) + " got timeout... AGAIN!") 
			else:
				print("seqence: " + str(seq) + " took: " + p_peek + " but it got timeout the first time!")	
			timed_out = True
			
		elif (check_peek > 0):
			# we got the right packet et.c....
			print("seqence: " + str(seq) + " took: " + p_peek)
		end_interval_time = datetime.datetime.now()
		elapsed_interval_time = end_interval_time - start_interval_time
		if timed_out:
			sleep_time = format(mote_interval - elapsed_interval_time.total_seconds() + shorten_per_interval, '.5f')
			timed_out = False
			stop_shorting = True
			print("timed_out")
		elif stop_shorting:
			print("stop_Shorting")
			sleep_time = format(mote_interval - elapsed_interval_time.total_seconds(), '.5f')
			#sleep_time = format(mote_interval - elapsed_interval_time.total_seconds() - 0.00005, '.5f')
		else:
			print("shorting")
			sleep_time = format(mote_interval - elapsed_interval_time.total_seconds() - shorten_per_interval, '.5f')
		print("sleep_time: " + str(sleep_time) + ". elapesd_interval_time: " + str(elapsed_interval_time))
		#up_end_interval_time = datetime.datetime.now()
		#elapsed_interval_time = up_end_interval_time - end_interval_time
		#print("newdiff: " + str(elapsed_interval_time.total_seconds()))
		seq = seq + 1
		time.sleep(float(sleep_time))


def main():
	latest_seq = get_latest_seq(1)
	time.sleep(mote_interval)
	print("The latest SEQ is.. : ", latest_seq)
	#regular_request_interval(latest_seq)
	little_less_per_interval(latest_seq)


if __name__ == '__main__':
	main()
