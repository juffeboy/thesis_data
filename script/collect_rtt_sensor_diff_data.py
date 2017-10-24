from __future__ import division
from __future__ import print_function
from operator import itemgetter
import math
import os
import operator
import re
import string
#from unidecode import unidecode

def remove_non_ascii(text):
	return re.sub(r'[^\x00-\x7f]',r'', text)

def append_parenthethis(value1, value2):
	return "(" + str(value1) + "," + str(value2) + ")"

def get_diff(parts):
	diff = 0

	for part in parts:
		if "diff:" in part:
			#print("found diff instance," + str(part))
			diff = int(part.split(":")[1])
			break
	return diff


def get_pit(parts):
	pit = ""
	for part in parts:
		if "pit:" in part:
			#print("found pit instance," + str(part))
			pit = str(part.split(": ")[1])
	return pit


def get_x(parts, searched_part):
	get_x = 0.0

	for part in parts:
		if searched_part in part:
		#	print("FOUND!!" + str(part) + " searched part "+  str(searched_part) + " parts : " + str(parts))
			get_x = float(part.split(":")[1])
			break
	return get_x

def get_sequence(parts, generate_or_handler):
	prefix_to_search_for = ""
	seq = 0
	split_on = ""
	if (generate_or_handler == "prefix"):
		prefix_to_search_for = "prefix"
		split_on = "="
	elif (generate_or_handler == "sequence"):
		prefix_to_search_for = "sequence"
		split_on = ":"
	#else:
		#print("not generate or handler.")

	parts = parts.split(",")
	for part in parts:
		#print("SEQUENCE!!?"+ str(part) + "!?!??!:, ", str(parts) + " gen " + str(generate_or_handler))
		if prefix_to_search_for in part:
			second_part = part.split(split_on)
			st = remove_non_ascii(second_part[1])
			seq = int(re.search(r'\d+', st).group())
			break
	return seq


def pull_info(filename):
	with open(filename) as openFile:
		for line in openFile:
			infoDict = {'sequence_start': '', 'rtt_min': 0.0, 'rtt_target': 0.0}
			temp_pit = ""
			sequence = 0


			line = remove_non_ascii(line)
			parts = line.split(",")

			if "inputs" in parts:
				infoDict['sequence_start'] = get_x(parts, 'in_start_seq')
				infoDict['rtt_min'] = get_x(parts, 'rtt_min')
				infoDict['rtt_target'] = get_x(parts, 'rtt_target')
				#print(infoDict)
				break
			else:
				continue
	return infoDict
	


def pull_data(filename):
	fileData = []
	with open(filename) as openFile:
		lines = openFile.readlines()
		for i in range(0, len(lines)):
			line = lines[i]
		#for line in openFile:
			sequenceDict = {'sequence': '', 'rtt': 0.0, 'srtt': 0.0,'corr': 0.0, 't_sleep': 0.0}
			sequence = 0

			line = remove_non_ascii(line)
			parts = line.split(",")

			#if "inputs" in parts:
			#	infoDict = {'sequence_start': '', 'rtt_min': 0.0, 'rtt_target': 0.0}
			#	infoDict['sequence_start'] = get_x(parts, 'in_start_seq')
			#	infoDict['rtt_min'] = get_x(parts, 'rtt_min')
			#	infoDict['rtt_target'] = get_x(parts, 'rtt_target')

			print("PARTS!!", parts)
			if "RECEIVED" in line:
				print("hello")
				if "timeout" in parts:
					continue
				#get seq.
				sequenceDict['sequence'] = get_sequence(line, "prefix")

				#temp_line = line.next()
				temp_line = lines[i+1]
				temp_line = remove_non_ascii(temp_line)
				
				print("NEXT LINE!!!", temp_line)
				parts = temp_line.split(",")
				sequenceDict['rtt'] = get_x(parts, 'rtt')
				sequenceDict['srtt'] = get_x(parts, 'srtt')
				sequenceDict['corr'] = get_x(parts, 'corr')
				sequenceDict['t_sleep'] = get_x(parts, 't_sleep')
				fileData.append(sequenceDict)
				print("sequence dict", sequenceDict)
				#print("filedata ", fileData)
				continue

			elif "SEQUENCE" in line:
				#get sequence and print timeout or handle timeout.
				sequenceDict['sequence'] = get_sequence(parts, "sequence")
				temp_line = lines[i+2]

				temp_line = remove_non_ascii(temp_line)
				parts = temp_line.split(",")
				sequenceDict['rtt'] = get_x(parts, 'rtt')
				sequenceDict['srtt'] = get_x(parts, 'srtt')
				sequenceDict['corr'] = get_x(parts, 'corr')
				sequenceDict['t_sleep'] = get_x(parts, 't_sleep')

				print("sequence dict", sequenceDict)
				fileData.append(sequenceDict)
				continue
			else:
				continue
	print(fileData)
	return fileData


#def ground_printer(plott, label, output_file, zoom_in):
def ground_printer(rtt,srtt,corr,rtt_min_single, rtt_target_single, rtt_min,rtt_target, label, output_file, zoom_in):
	label = label.replace("_", "/")
	print("\\begin{figure}\centering\\begin{tikzpicture}\\begin{axis}[", file=output_file)
	print("xlabel={intervals}, ylabel={time in },", file=output_file)
	print("xmin=100, xmax=700,ymin=-10, ymax=150,", file=output_file)
	#print("xtick={20,40,60,80,100,120,140,160,180,200},", file=output_file)
	print("xtick={100,200,300,400,500,600},", file=output_file)
	#print("ytick={-20,-10,0,10,20,30,40,60,80,100,120},", file=output_file)
	if (zoom_in):
		print("xmin=500, xmax=600,ymin=-10, ymax=150,", file=output_file)
		print("xtick={500,520,540,560,580,600},", file=output_file)
		label += "/zommed"
	#print("ytick={-10,0,10,15,20,25,30,35,40,45,50,55,60,75},", file=output_file)
	print("ytick={-10,0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150},", file=output_file)
	print("legend pos=north west, grid style={dotted,gray},ymajorgrids=true,]", file=output_file)

	#print("" + plott, file=output_file)
	print("" + rtt, file=output_file)
	print("" + srtt, file=output_file)
	print("" + corr, file=output_file)
	print("" + rtt_min, file=output_file)
	print("" + rtt_target, file=output_file)
	print("\end{axis}\end{tikzpicture}", file=output_file)
	#print("\caption{"+ label + ",  RTTMIN: " + str(rtt_min_single)+ ", RTTTARGET: " + str(rtt_target_single) +  "}", file=output_file)
	print("\caption{"+ label + "}", file=output_file)
	print("\label{fig:"+ label + "}", file=output_file)
	print("\end{figure}", file=output_file)

	#total = before_plot+plott+after
	#return total


def printer(filename, data_list, data_info, output_file):
	data_list.sort(key=operator.itemgetter('sequence'))
	start_seq = data_list[0]['sequence']
	print("START SEQ: " + str(start_seq))
	print_rtt = "\\addplot[ color=green!80 ] coordinates {"
	print_srtt = "\\addplot[ color=blue ] coordinates {"
	print_corr = "\\addplot[ color=red ] coordinates {"
	print_t_sleep = "\\addplot[  ] coordinates {"
	print_rtt_min = "\\addplot[ color=gray!50  ] coordinates {"
	print_rtt_target = "\\addplot[ color=gray!60 ] coordinates {"

	counter = 0
	for item in data_list:
		if counter == 700:
			break
		counter += 1
		#print_seq += append_parenthethis(item['sequence']-start_seq, item['diff'])
		print_rtt += append_parenthethis(item['sequence'], item['rtt']*1000)
		print_srtt += append_parenthethis(item['sequence'], item['srtt']*1000)
		print_corr += append_parenthethis(item['sequence'], item['corr']*1000)
		print_t_sleep += append_parenthethis(item['sequence'], item['t_sleep']*1000)
		print_rtt_min += append_parenthethis(item['sequence'], data_info['rtt_min']*1000)
		print_rtt_target += append_parenthethis(item['sequence'], data_info['rtt_target']*1000)

	print_rtt += "};\\addlegendentry{rtt}"
	print_srtt += "};\\addlegendentry{srtt}"
	print_corr += "};\\addlegendentry{corr}"
	print_t_sleep += "};\\addlegendentry{t_sleep}"
	print_rtt_min += "};\\addlegendentry{rtt/min}"
	print_rtt_target += "};\\addlegendentry{rtt/target}"


	total = ground_printer(print_rtt,print_srtt,print_corr,data_info['rtt_min']*1000,data_info['rtt_target']*1000, print_rtt_min,print_rtt_target, filename, output_file,False)
	total = ground_printer(print_rtt,print_srtt,print_corr,data_info['rtt_min']*1000,data_info['rtt_target']*1000, print_rtt_min,print_rtt_target, filename, output_file,True)
	#total = ground_printer(tot, filename, output_file, False)
	

	#print("" + total, file=output_file)
	#print("" + print_seq, file=output_file)



def main():

	## create file to write to
	## file to read from
	base = '/Users/johan.carlquist/Documents/exjobb/thesis_data/tests_24_10/gateway'
	file_to_write=base + '/gateway_output.txt'
	fh = open(file_to_write, "w")
	directory= base
	temp_dic = {}
	list_dic = []
	for fileName in os.listdir(directory):
		print(fileName)
		print(os.listdir(directory))
		if fileName.startswith('test'):
			file = os.path.join(directory, fileName)
			data_info = pull_info(file)
			print(data_info)
			data_list = pull_data(file)
			printer(fileName, data_list, data_info, fh)
			continue


if __name__ == '__main__':
	main()
