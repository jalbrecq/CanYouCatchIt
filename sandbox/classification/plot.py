import matplotlib.pyplot as plt
import csv
import os
import numpy as np

path_delay_csv = "../data/csv/delay2020-11-02.csv"

f= open(path_delay_csv,'rt')
with f:
	data= csv.reader(f)
	big_late=0
	late=0
	nul=0
	avance= 0
	grosse_avance=0
	for row in data:
		if len(row[3]) >0:
			
			delay= float(row[3]) 			
			if delay>10:				
				grosse_avance+=1
			elif delay>0:
				avance +=1
			elif delay==0:
				nul +=1
			elif delay> -10:
				late+=1
			else:
				big_late +=1

x= ['big late', 'late', 'on time', 'early','big early']
delay=[big_late,late,nul,avance,grosse_avance]

plt.bar(x,delay)
plt.xlabel("Delay")
plt.ylabel("Number of delay")

plt.show()