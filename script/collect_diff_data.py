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

def get_sequence(parts, generate_or_handler):
	prefix_to_search_for = ""
	seq = 0
	if (generate_or_handler == "generate"):
		prefix_to_search_for = "prefix:"
	elif (generate_or_handler == "handler"):
		prefix_to_search_for = "name:"
	#else:
		#print("not generate or handler.")

	for part in parts:
		if prefix_to_search_for in part:
			second_part = part.split(":")
			st = remove_non_ascii(second_part[1])
			seq = int(re.search(r'\d+', st).group())
			#print("get_sequence seq: "+ str(seq))
			break
			#seq = int(second_part[1])
	return seq



def pull_data(filename):
	fileData = []

	

	with open(filename) as openFile:
		for line in openFile:
			sequenceDict = {'sequence': '', 'pit': '', 'diff': 0,'calls': 0, 'time_generated': ''}
			temp_pit = ""
			sequence = 0

			line = remove_non_ascii(line)
			parts = line.split(",")
			#print("LINE:" + line)
			#print("PARTS:" + str(parts))
			if (parts[0] == "generate"):
				#print("generate")
				temp_pit = get_pit(parts)
				if (temp_pit == "y"):
					## we want to save the value.
					sequence = get_sequence(parts, parts[0])
					sequenceDict['sequence'] = sequence
					sequenceDict['pit'] = get_pit(parts)
					sequenceDict['diff'] = -get_diff(parts)
				else:
					continue

			elif (parts[0] == "handler"):
				#print("handler")
				temp_pit = get_pit(parts)
				if (temp_pit == "n"):
					sequence = get_sequence(parts, parts[0])
					sequenceDict['sequence'] = sequence
					sequenceDict['pit'] = get_pit(parts)
					sequenceDict['diff'] = get_diff(parts)
				else:
					continue
			elif (parts[0] == "end_generate"):
				#print("end_generate")
				continue
			elif (parts[0] == "end_handler"):
				#print("end_handler")
				continue
			else:
				print("strange, we shoudlnot come here.")
				continue
			## put the data into the array.

			already_exists = any(it['sequence'] == sequence for it in fileData)
			#exists = (item for item in fileData if item["sequence"] == sequence).next()
			if already_exists:
			#if (len(exists)>0):
				## already exists.
				#print("already exists, this one could not be added! " + str(sequenceDict))
				continue
			else:
				#print("The dict looks like this!" + str(sequenceDict))
				fileData.append(sequenceDict)
	print(fileData)
	return fileData


def ground_printer(plott, label, output_file, zoom_in):

	label = label.replace("_", "/")
	print("\\begin{figure}\centering\\begin{tikzpicture}\\begin{axis}[", file=output_file)
	print("xlabel={intervals}, ylabel={Age data},", file=output_file)
	#print("ytick={-20,-10,0,10,20,30,40,60,80,100,120},", file=output_file)
	if (zoom_in):
		print("xmin=500, xmax=600,ymin=-20, ymax=20,", file=output_file)
		print("xtick={500,520,540,560,580,600},", file=output_file)
		label += "/zommed"
	else:
		print("xmin=100, xmax=700,ymin=-20, ymax=20,", file=output_file)
		#print("xtick={20,40,60,80,100,120,140,160,180,200},", file=output_file)
		print("xtick={100,200,300,400,500,600},", file=output_file)

	print("ytick={-20,-15,-10,-5,0,5,10,15,20},", file=output_file)
	print("legend pos=north west, grid style={dotted,gray},ymajorgrids=true,]", file=output_file)

	print("" + plott, file=output_file)

	print("\end{axis}\end{tikzpicture}", file=output_file)
	print("\caption{"+ label + "}", file=output_file)
	print("\label{fig:"+ label + "}", file=output_file)
	print("\end{figure}", file=output_file)

	#total = before_plot+plott+after
	#return total

def printer(filename, data_list, output_file):
	data_list.sort(key=operator.itemgetter('sequence'))
	start_seq = data_list[0]['sequence']
	print("START SEQ: " + str(start_seq))
	print_seq = "\\addplot[  ] coordinates {"
	#print_seq = "\\addplot[ mark=diamond ] coordinates {"
	print_diff = ""

	counter = 0
	for item in data_list:
		if item['sequence'] < 100 :
			counter += 1
			continue
		if counter == 800:
			break
		counter += 1
		#print_seq += append_parenthethis(item['sequence']-start_seq, item['diff'])
		print_seq += append_parenthethis(item['sequence'], item['diff'])

	print_seq += "};\\addlegendentry{seq}"
	print_diff += "};\\addlegendentry{diff}"

	total = ground_printer(print_seq, filename, output_file, False)
	total = ground_printer(print_seq, filename, output_file, True)
	#print("" + total, file=output_file)
	#print("" + print_seq, file=output_file)



def main():

	## create file to write to
	## file to read from
	base = '/Users/johan.carlquist/Documents/exjobb/thesis_data/tests_24_10/sensor'
	file_to_write=base + '/sensor_output.txt'
	fh = open(file_to_write, "w")
	directory= base
	temp_dic = {}
	list_dic = []
	for fileName in os.listdir(directory):
		print(fileName)
		print(os.listdir(directory))
		if fileName.startswith('test'):
			file = os.path.join(directory, fileName)
			data_list = pull_data(file)
			printer(fileName, data_list, fh)
			continue


if __name__ == '__main__':
	main()
