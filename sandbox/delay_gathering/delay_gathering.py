# Imports
from requests import request
from datetime import datetime, timedelta, date
import sqlite3, time, json, csv
import os.path
from pathlib import Path

# Compute and save delays to a sqlite3 database

def get_stops(lines_id, access_token):
    """Return the STIB PassingTimeByPoint api response.

    Keyword arguments:
    lines_id -- the id of a line (a list of 10 strings maximum - no default)
    """

    # The STIB API url
    url = "https://opendata-api.stib-mivb.be/NetworkDescription/1.0/PointByLine/" + "%2C".join(lines_id)

    # Payload
    payload = {}

    # Headers
    # Setup the headers
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    # Send the GET request
    response = eval(request("GET", url, headers=headers, data=payload).text)
    result = {}
    lines_id = []
    if 'message' not in response:
        for line in response["lines"]:
            if line['lineId'] not in lines_id:
                lines_id.append(line['lineId'])
                result[line['lineId']] = {'stops_id': []}
                for point in line['points']:
                    result[line['lineId']]['stops_id'].append(point['id'])
                    result[line['lineId']]['direction'] = line['direction']
                    result[line['lineId']]['destination'] = line['destination']['fr']
    return result

def get_stops_id(database_path):
    """Return the STIB stop ids - list of string.

    Keyword arguments:
    database_path -- the database path (a string or an path like object - no default)
    """

    # Connect to the db
    sqlite_db = sqlite3.connect(database_path)
    c = sqlite_db.cursor()

    # get the id of the lines
    c.execute('SELECT stop_id FROM stops')
    result = c.fetchall()
    
    # disconnect
    c.close()

    return [line_id for i in result for line_id in i]

def get_arrival_time(stops_id, access_token):
    """Return the STIB PassingTimeByPoint api response.

    Keyword arguments:
    stops_id -- the id of a stop (a list of 10 strings maximum - no default)
    """

    # The STIB API url
    url = "https://opendata-api.stib-mivb.be/OperationMonitoring/4.0/PassingTimeByPoint/" + "%2C".join(stops_id)

    # Payload
    payload = {}

    # Headers
    # Setup the headers
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    # Send the GET request
    return(eval(request("GET", url, headers=headers, data=payload).text))

def get_schedule(database_path, stop_id, line_id, trip_headsign):
    """Return the STIB theoretical schedule - list of datetime (%H:%M:%S).

    Keyword arguments:
    database_path -- the id of a stop (string or path-like object - no default)
    stop_id -- the id of a stop, this must be at least a four digit number (string - no default)
    line_id -- the line id (string - no default)
    trip_headsign -- the destionation of the trip (string - no default)
    """

    # get the current date and time
    current_datetime = datetime.now()
    today = current_datetime.strftime("%Y%m%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    # compute the max time
    max_time = current_datetime + timedelta(hours=1)
    max_time = max_time.strftime("%H:%M:%S")

    # get the day name
    name_day = current_datetime.strftime("%A").lower()

    # Connect to the db
    sqlite_db = sqlite3.connect(database_path)
    c = sqlite_db.cursor()

    # get the id of the route
    c.execute('SELECT route_id FROM routes WHERE agency_id=?', (line_id, ))
    result = c.fetchone()
    if result:
        route_id = result[0]
    else:
        c.close()
        print("ERROR: there is no route_id for this line_id: " + str(line_id))
        return "ERROR"

    # get the service_id
    c.execute('SELECT trips.service_id FROM calendar, trips WHERE calendar.' + name_day + '=1 AND calendar.start_date<=? AND calendar.end_date>=? AND trips.route_id=? AND calendar.service_id=trips.service_id', (today, today, route_id, ))
    result = c.fetchone()
    if result:
        service_id = result[0]
    else:
        c.close()
        print("ERROR: there is no service_id for this route_id: " + str(route_id))
        return "ERROR"

    # get the theoretical schedule
    # --- NEED OPTIMISATION ---
    c.execute('SELECT DISTINCT stop_times.trip_id, stop_times.arrival_time FROM stop_times, trips WHERE trips.route_id=? AND trips.trip_headsign=? AND trips.service_id=? AND stop_times.stop_id=? AND stop_times.arrival_time>=? AND stop_times.arrival_time<=? AND stop_times.trip_id=trips.trip_id ORDER BY stop_times.arrival_time ASC', (route_id, trip_headsign, service_id, stop_id, current_time, max_time, ))
    theoretical_time = c.fetchall()
    c.close()
    if theoretical_time:
        return theoretical_time[0]
    else:
        return None

def compute_delay(stops_id, database_path, access_token):
    """Return delay in second for the next vehicle of each line passing at a given stop.

    Keyword arguments:
    stop_id -- the id of a stop (a list of strings - no default)
    database_path -- the database path (a string or an path like object - no default)
    """

    result = []

    api_responce = get_arrival_time(stops_id, access_token)

    for stop in api_responce['points']:
        lineId_list = []

        for passingTimes in stop['passingTimes']:
            delay = None
            theoretical_time = None
            expectedArrivalTime = None
            direction = None

            line_id = passingTimes['lineId']

            if line_id not in lineId_list:
                lineId_list.append(line_id)
                if stop['pointId'].isdecimal():
                    stop_id = "{:04d}".format(int(stop['pointId'])) 
                else:
                    stop_id = stop['pointId']

                if 'message' in passingTimes:
                    print(passingTimes['message'])

                else:
                    theoretical_time = get_schedule(database_path, stop_id, line_id, passingTimes['destination']['fr'])

                    if theoretical_time:

                        trip_id = theoretical_time[0]
                        theoretical_time = datetime.strptime(theoretical_time[1], '%H:%M:%S').time()
                        expectedArrivalTime = datetime.strptime(passingTimes['expectedArrivalTime'].split('T')[1].split('+')[0], '%H:%M:%S').time()

                        theoretical_time = datetime.combine(date.today(), theoretical_time)
                        expectedArrivalTime = datetime.combine(date.today(), expectedArrivalTime)

                        delay = theoretical_time - expectedArrivalTime
                        delay = delay.total_seconds()//60

                        # Connect to the db
                        sqlite_db = sqlite3.connect(database_path)
                        c = sqlite_db.cursor()

                        # get the id of the route
                        c.execute('SELECT direction_id FROM trips WHERE trip_id=?', (trip_id, ))
                        direction = c.fetchone()
                        if direction:
                            direction = direction[0]
                        else:
                            print("ERROR: there is no direction_id for this trip_id: " + str(trip_id))
                        c.close()
                    
                    else:
                        print('not theoretical time', stop_id, line_id, datetime.now())

                # Connect to the db
                sqlite_db = sqlite3.connect(database_path)
                c = sqlite_db.cursor()

                # get the id of the route
                c.execute('SELECT route_desc FROM routes WHERE agency_id=?', (line_id, ))
                response_1 = c.fetchone()

                if response_1:
                    transport_type = response_1[0]
                else:
                    c.close()
                    print("ERROR: there is no route_desc for this line_id: " + str(line_id))
                c.close()
                result.append({'transport_type': transport_type, 'stop': stop_id, 'line': line_id, 'delay': delay, 'theoretical_time': theoretical_time, 'expectedArrivalTime': expectedArrivalTime, 'date': datetime.now(), 'direction': direction})
    return result

def save_delays(stops_id, database_path):
    """Return delay in second for the next vehicle of each line passing at a given stop.

    Keyword arguments:
    stop_id -- the id of a stop (a list of strings - no default)
    database_path -- the database path (a string or an path like object - no default)
    """

    # You need to secure this token be carefull it's fragile
    access_token = 'd86ffa37612eff39c64bacb96053c194'
    weather_api_token = 'e98872d0940b9785a1e048d5a5a599dd'

    while(True):
        
        for points in [stops_id[x:x+10] for x in range(0, len(stops_id), 10)]:
            delays = compute_delay(points, 'sandbox/data/mcts.db', access_token)
        
            # Connect to the db
            sqlite_db = sqlite3.connect(database_path)
            c = sqlite_db.cursor()

            for delay in delays:
                if not delay['stop'].isnumeric():
                    print('-'*40 + 'UNUMERICAL STOP ID' + '-'*40)
                print('delay: ', delay['delay'], ' -- ', 'stop id: ', delay['stop'], ' -- ', 'line id: ', delay['line'])

                url = "http://api.openweathermap.org/data/2.5/weather?q=Brussels,be&APPID=" + weather_api_token

                response = request("GET", url, headers={}, data={})

                temp = response.json()['main']['temp']
                humidity = response.json()['main']['humidity']
                visibility = response.json()['visibility']
                wind = response.json()['wind']['speed']
                rain = 0
                if 'rain' in response.json():
                    rain = response.json()['rain']
                c.execute("INSERT INTO delay (transport_type, stop, line, delay, theoretical_time, expectedArrivalTime, date, direction, year, month, day, hour, minute, temp, humidity, visibility, wind, rain) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (delay['transport_type'], delay['stop'], delay['line'], delay['delay'], delay['theoretical_time'], delay['expectedArrivalTime'], delay['date'], delay['direction'], delay['date'].year, delay['date'].month, delay['date'].weekday(), delay['date'].hour, delay['date'].minute, temp, humidity, visibility, wind, rain))

                f = open('sandbox/data/delay' + datetime.now().date().isoformat() + '.csv', 'a+')
                with f:
                    writer = csv.writer(f)
                    writer.writerow((delay['transport_type'], delay['stop'], delay['line'], delay['delay'], delay['theoretical_time'], delay['expectedArrivalTime'], delay['date'], delay['direction'], delay['date'].year, delay['date'].month, delay['date'].weekday(), delay['date'].hour, delay['date'].minute, temp, humidity, visibility, wind, rain))

            sqlite_db.commit()
            c.close()

        print('-'*40, 'waiting 60s', '-'*40)
        time.sleep(60)

# print(get_arrival_time(["0470F"]))
# print(get_schedule('sandbox/data/mcts.db', '0516', '4', 'GARE DU NORD'))
# print(compute_delay(['0089', '0022', '0470F', '0471', '0039', '0472', '0473F', '0501', '0015', '0506', '0511', '0057', '0516', '0521', '61', '0526', '0529', '0531'], 'sandbox/data/mcts.db', 'd86ffa37612eff39c64bacb96053c194'))
# print(save_delays(get_stops_id(database_path), 'sandbox/data/mcts.db'))
print(save_delays(['0089'], 'sandbox/data/mcts.db'))
