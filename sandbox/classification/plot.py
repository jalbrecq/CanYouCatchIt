import matplotlib.pyplot as plt
import csv,os

path = "../data/csv/"

for root, dirs, files in os.walk("../data/csv"):
	pass

big_late=0
late=0
nul=0
avance= 0
grosse_avance=0

for file in files:
	path = "../data/csv/"
	path+=file
	f= open(path,'rt')
	with f:
		data= csv.reader(f)

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