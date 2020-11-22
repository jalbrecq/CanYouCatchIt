# Imports
from datetime import datetime, timedelta, date
import sqlite3, time, json, csv, difflib, requests, logging
from logging.handlers import RotatingFileHandler
import os.path
from pathlib import Path
from config import access_token, weather_api_token, level

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

my_handler = RotatingFileHandler('sandbox/log/delay_gathering.log', mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(level)

app_log = logging.getLogger('root')
app_log.setLevel(level)

app_log.addHandler(my_handler)

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

    result = {}

    # Send the GET request
    app_log.info('Send a request to the STIB API to get the list of stops on a given line')
    try:
        response = eval(requests.request("GET", url, headers=headers, data=payload).text)
        print(response)
        print('-'*50)
    except requests.exceptions.ConnectionError:
        app_log.exception('Connection Error probably a lost of internet connection')
        return result
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

    app_log.info('fetch the list of all STIB stops')
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
    app_log.info('Send a request to the STIB API to get the passing time of vehicle by point')
    try:
        return eval(requests.request("GET", url, headers=headers, data=payload).text)
    except requests.exceptions.ConnectionError:
        app_log.exception('Connection Error probably a lost of internet connection')
        return None

def get_schedule(database_path, stop_id, line_id, trip_headsign):
    """Return the STIB theoretical schedule - list of datetime (%H:%M:%S).

    Keyword arguments:
    database_path -- the id of a stop (string or path-like object - no default)
    stop_id -- the id of a stop, this must be at least a four digit number (string - no default)
    line_id -- the line id (string - no default)
    trip_headsign -- the destionation of the trip (string - no default)
    """

    # get the current date and time
    app_log.info('get the current date and time and max time')
    current_datetime = datetime.now()
    today = current_datetime.strftime("%Y%m%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    # compute the max time
    max_time = current_datetime + timedelta(hours=1)
    max_time = max_time.strftime("%H:%M:%S")

    app_log.info('get current day name')
    # get the day name
    name_day = current_datetime.strftime("%A").lower()

    # Connect to the db
    sqlite_db = sqlite3.connect(database_path)
    c = sqlite_db.cursor()

    # get the id of the route
    app_log.info('make a query to gather the route_id')
    c.execute('SELECT route_id FROM routes WHERE agency_id=?', (line_id, ))
    result = c.fetchone()
    if result:
        route_id = result[0]
    else:
        c.close()
        app_log.error('there is no route_id for this line_id: %s', line_id)
        return None

    # get the service_id
    app_log.info('make a query to gather the service_id of a route_id')
    c.execute('SELECT DISTINCT trips.service_id FROM calendar, trips WHERE calendar.' + name_day + '=1 AND calendar.start_date<=? AND calendar.end_date>=? AND trips.route_id=? AND calendar.service_id=trips.service_id', (today, today, route_id, ))
    result = c.fetchall()
    if result:
        services_id = result
    else:
        c.close()
        app_log.error('there is no service_id for this route_id: %s', route_id)
        return None

    # get the theoretical schedule
    # --- NEED OPTIMISATION ---
    app_log.info('make a query to get the theoritical schedule')
    theoretical_time = []
    if services_id:
        for service_id in services_id:
            if not theoretical_time:
                app_log.info('route_id: %s, trip_headsign: %s, service_id: %s, stop_id: %s, current_time: %s, max_time: %s', route_id, trip_headsign, service_id[0], stop_id, current_time, max_time)
                c.execute('SELECT DISTINCT stop_times.trip_id, stop_times.arrival_time FROM stop_times, trips WHERE trips.route_id=? AND trips.trip_headsign=? AND trips.service_id=? AND stop_times.stop_id=? AND stop_times.arrival_time>=? AND stop_times.arrival_time<=? AND stop_times.trip_id=trips.trip_id ORDER BY stop_times.arrival_time ASC', (route_id, trip_headsign, service_id[0], stop_id, current_time, max_time, ))
                theoretical_time = c.fetchall()
            else:
                app_log.info('theoretical_time find')
                break
    c.close()
    if theoretical_time:
        return theoretical_time[0]
    else:
        app_log.warning('no theoretical_time find')
        return None

def compute_delay(stops_id, database_path, access_token):
    """Return delay in second for the next vehicle of each line passing at a given stop.

    Keyword arguments:
    stops_id -- a list of stop id (a list of strings - no default)
    database_path -- the database path (a string or an path like object - no default)
    """

    result = []

    api_responce = get_arrival_time(stops_id, access_token)

    if not api_responce:
        app_log.warning('no arrival time response from the STIB API')
        transport_type = None
        stop_id = None
        line_id = None
        delay = None
        theoretical_time = None
        expectedArrivalTime = None
        direction = None
        trip_id = None
        return [{'transport_type': transport_type, 'trip': trip_id, 'stop': stop_id, 'line': line_id, 'delay': delay, 'theoretical_time': theoretical_time, 'expectedArrivalTime': expectedArrivalTime, 'date': datetime.now(), 'direction': direction}]

    for stop in api_responce['points']:
        lineId_list = []

        for passingTimes in stop['passingTimes']:
            delay = None
            theoretical_time = None
            expectedArrivalTime = None
            direction = None
            trip_id = None

            line_id = passingTimes['lineId']

            if line_id not in lineId_list:
                lineId_list.append(line_id)

                if stop['pointId'].isdecimal():
                    stop_id = "{:04d}".format(int(stop['pointId'])) 
                else:
                    stop_id = stop['pointId']
                stop_id = difflib.get_close_matches(stop_id, stops_id)[0]

                if 'message' in passingTimes:
                    print(passingTimes['message'])

                else:
                    theoretical_time = get_schedule(database_path, stop_id, line_id, passingTimes['destination']['fr'])
                    print(theoretical_time)

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
                            app_log.error('there is no direction_id for this trip_id: %s', trip_id)
                        c.close()

                    else:
                        app_log.warning('not theoretical time: %s, %s', stop_id, line_id)

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
                    app_log.error('there is no route_desc for this line_id: %s', line_id)
                c.close()
                result.append({'transport_type': transport_type, 'trip': trip_id, 'stop': stop_id, 'line': line_id, 'delay': delay, 'theoretical_time': theoretical_time, 'expectedArrivalTime': expectedArrivalTime, 'date': datetime.now(), 'direction': direction})
    return result

def save_delays(stops_id, database_path, access_token, weather_api_token):
    """Return delay in second for the next vehicle of each line passing at a given stop.

    Keyword arguments:
    stop_id -- the id of a stop (a list of strings - no default)
    database_path -- the database path (a string or an path like object - no default)
    """

    while(True):
        
        for points in [stops_id[x:x+10] for x in range(0, len(stops_id), 10)]:
            delays = compute_delay(points, 'sandbox/data/mcts.db', access_token)
        
            # Connect to the db
            sqlite_db = sqlite3.connect(database_path)
            c = sqlite_db.cursor()

            for delay in delays:
                # if not delay['stop'].isnumeric():
                #     print('-'*40 + 'UNUMERICAL STOP ID' + '-'*40)
                app_log.info('%s min of delay for the line (%s) on the stop (%s)', delay['delay'], delay['line'], delay['stop'])
                print('delay:', delay['delay'], ' -- line_id:', delay['line'], ' -- stop_id:', delay['stop'])

                url = "http://api.openweathermap.org/data/2.5/weather?q=Brussels,be&APPID=" + weather_api_token
                
                try:
                    response = requests.request("GET", url, headers={}, data={})
                except requests.exceptions.ConnectionError:
                    app_log.exception('Connection Error probably a lost of internet connection')
                    response = None

                temp = None
                humidity = None
                visibility = None
                wind = None
                rain = None
                if response:
                    try:
                        temp = response.json()['main']['temp']
                        humidity = response.json()['main']['humidity']
                        visibility = response.json()['visibility']
                        wind = response.json()['wind']['speed']
                        rain = 0
                        if 'rain' in response.json() and '1h' in response.json()['rain']:
                            rain = response.json()['rain']['1h']
                    except:
                        app_log.exception('Parsing to dict exception: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)')

                csv_file = Path("sandbox/data/csv2/delay" + datetime.now().date().isoformat() + '.csv')
                f = open('sandbox/data/csv2/delay' + datetime.now().date().isoformat() + '.csv', 'a+')

                with f:
                    writer = csv.writer(f)
                    if not csv_file.is_file():
                        # file exists
                        writer.writerow('transport_type','trip','stop','line','delay','theoretical_time','expectedArrivalTime','date','direction','year','month','day','hour','minute','temp','humidity','visibility','wind','rain')
                    writer.writerow((delay['transport_type'], delay['trip'], delay['stop'], delay['line'], delay['delay'], delay['theoretical_time'], delay['expectedArrivalTime'], delay['date'], delay['direction'], delay['date'].year, delay['date'].month, delay['date'].weekday(), delay['date'].hour, delay['date'].minute, temp, humidity, visibility, wind, rain))

                c.execute("INSERT INTO delay (transport_type, trip, stop, line, delay, theoretical_time, expectedArrivalTime, date, direction, year, month, day, hour, minute, temp, humidity, visibility, wind, rain) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (delay['transport_type'], delay['trip'], delay['stop'], delay['line'], delay['delay'], delay['theoretical_time'], delay['expectedArrivalTime'], delay['date'], delay['direction'], delay['date'].year, delay['date'].month, delay['date'].weekday(), delay['date'].hour, delay['date'].minute, temp, humidity, visibility, wind, rain))

            sqlite_db.commit()
            c.close()

        print('-'*40, 'waiting 150s', '-'*40)
        app_log.info('wainting 150s')
        time.sleep(150)

# print(get_stops(['16'], access_token))
# print(get_arrival_time(["0470F"], access_token))
# print(get_schedule('sandbox/data/mcts.db', '0516', '4', 'GARE DU NORD'))
# print(compute_delay(['0089', '0022', '0470F', '0471', '0039', '0472', '0473F', '0501', '0015', '0506', '0511', '0057', '0516', '0521', '61', '0526', '0529', '0531'], 'sandbox/data/mcts.db', 'd86ffa37612eff39c64bacb96053c194'))
# print(save_delays(get_stops_id('sandbox/data/mcts.db'), 'sandbox/data/mcts.db', access_token, weather_api_token))
print(save_delays(['0089', '5501', '5502', '5503', '5504', '5281G', '5507', '5508', '5509', '5510', '5512', '6474F', '5529', '5532', '5515', '5516', '5517', '5518', '5519', '5520F'], 'sandbox/data/mcts.db', access_token, weather_api_token))
