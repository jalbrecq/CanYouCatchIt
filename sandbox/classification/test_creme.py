import matplotlib.pyplot as plt
import csv,os
from creme import stream 



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
    


    X_y =stream.iter_csv(path)
    for x, y in X_y:
      print(x)
      


    
# fieldnames = ["transport_type", "stop", "line","delay","theoretical_time","expectedArrivalTime","date","direction","date_year","date_month","date_weekday","dat_hour","_date_minute","date_seconde","temp","humidity","visibility","wind","rain"]
# transport_type,stop,line,delay,theoretical_time,expectedArrivalTime,date,direction,date_year,date_month,date_weekday,date_hour,date_minute,date_seconde,temp,humidity,visibility,wind,rain