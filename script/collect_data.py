from __future__ import division
from __future__ import print_function
from operator import itemgetter
import math
import os
import operator


def stanDev(values):
	length = len(values)
	avg = sum(values)*1.0/len(values)
	total_sum = 0
	for index, value in enumerate(values):
		total_sum += (values[index]-avg)**2

	under_root = total_sum*1.0/length
	return math.sqrt(under_root)

def median(values):
	sortedList = sorted(values)
	length = len(values)
	index = int((length - 1)/2)
	if (length % 2):
		return sortedList[index]
	else:
		return (sortedList[index] + sortedList[index+1])/2.0



#dir = os.path.dirname(__file__)
#fileName = os.path.join(dir, '/Users/johan.carlquist/Documents/exjobb/Instruktioner/ping_size_56_bytes_iterations_100')
# open a summery file that contain all the data.
#file=fileName

def append_parenthethis(value1, value2):
	return "(" + str(value1) + "," + str(value2) + ")"

def collect_data(filename, tot_dic, multiplier):
	fileData = []
	
	with open(file) as openFile:
		for line in openFile:
			for part in line.split():
				if "time=" in part:
					#print part
					secondPart = part.split("=")
					#print secondPart[1]
					fileData.append(float(secondPart[1])*multiplier)
	
	
	fileDict = {'type': '', 'size': '', 'min': '', 'avg': '', 'max': '', 'median': '', 'stdv': '', 'values': fileData}
	
	
	typ=fileName.split("/")[-1].split("_")
	for index, val in enumerate(typ):
		if "ping" == val:
			fileDict['type'] = 'ping'
		if "peek" == val:
			fileDict['type'] = 'peek'
		if "size" == val:
			fileDict['size'] = int(typ[index+1])+76
	
	
	
	if len(fileData) > 0:
		fileDict['min'] = min(fileData)
		fileDict['max'] = max(fileData)
		fileDict['avg'] = sum(fileData)*1.0/len(fileData)
		fileDict['median'] = median(fileData)
		fileDict['stdv'] = stanDev(fileData)
	
		#tot_dic['min'] += append_parenthethis(fileDict['size'], fileDict['min'])
		#tot_dic['max'] += append_parenthethis(fileDict['size'], fileDict['max'])
		#tot_dic['avg'] += append_parenthethis(fileDict['size'], fileDict['avg'])
		#tot_dic['median'] += append_parenthethis(fileDict['size'], fileDict['median'])
		#tot_dic['stdv'] += append_parenthethis(fileDict['size'], fileDict['stdv'])
		
		strk = str(fileDict['size']) + " " +  str(fileDict['min'])
		avg_str="(" + str(fileDict['size']) + "," + str(fileDict['avg']) + ")"
		avg_str=append_parenthethis(fileDict['size'], fileDict['avg'])
		
		#print(strk, file=fh)
	return fileDict



### ITERATE OVER FILES IN FOLDER
#file_to_write='/Users/johan.carlquist/Documents/exjobb/resultat/test_08_13/resultat_tester/grafdata/peek_with_debug_data.txt'
file_to_write='/Users/johan.carlquist/Documents/exjobb/thesis_data/resultat_tester/test_09_18_home/peek_without_debug/peek_data.txt'
fh = open(file_to_write, "w")
directory='/Users/johan.carlquist/Documents/exjobb/thesis_data/resultat_tester/test_09_18_home/peek_without_debug'
#directory='/Users/johan.carlquist/Documents/exjobb/resultat/test_08_13/resultat_tester/peektest/test_08_13/with_debug'
temp_dic = {}
list_dic = []
for fileName in os.listdir(directory):
	if fileName.startswith('ping_'):
		#print name
		file =  os.path.join(directory,fileName)
		temp_dic = collect_data(file, temp_dic, 1)
		list_dic.append(temp_dic)
		continue
	elif fileName.startswith('peek_'):
		file =  os.path.join(directory, fileName)
		temp_dic = collect_data(file, temp_dic, 1)
		list_dic.append(temp_dic)
		continue
	else:
		continue

list_dic.sort(key=operator.itemgetter('size'))


print_min = ""
print_max = ""
print_avg = ""
print_median = ""
print_stdv = ""

print_min = "\\addplot[ mark=diamond ] coordinates {"
print_max = "\\addplot[ color=green, ] coordinates {"
print_avg = "\\addplot[ mark=triangle ] coordinates {"
print_median = "\\addplot[ mark=square ] coordinates {"
print_stdv = "\\addplot[ color=yellow, ] coordinates {"


for test in list_dic:
	print_min += append_parenthethis(test['size'], test['min'])
	print_max += append_parenthethis(test['size'], test['max'])
	print_avg += append_parenthethis(test['size'], test['avg'])
	print_median += append_parenthethis(test['size'], test['median'])
	print_stdv += append_parenthethis(test['size'], test['stdv'])

print_min += "};\\addlegendentry{min}"
print_max += "};\\addlegendentry{max}"
print_avg += "};\\addlegendentry{average}"
print_median += "};\\addlegendentry{median}"
print_stdv += "};\\addlegendentry{stdev}"


#print("min: " + print_min, file=fh)
#print("max: " + print_max, file=fh)
#print("avg: " + print_avg, file=fh)
#print("median: " + print_median, file=fh)
#print("stdv: " + print_stdv, file=fh)

print("" + print_min, file=fh)
#print("" + print_max, file=fh)
print("" + print_avg, file=fh)
print("" + print_median, file=fh)
#print("" + print_stdv, file=fh)

fh.close()



