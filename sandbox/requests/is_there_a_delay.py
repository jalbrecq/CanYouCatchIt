import requests, sqlite3
from datetime import date, datetime, timedelta

def is_delay(stop_id):
    formated_stop_id = "{:04d}".format(stop_id)

    # The STIB API url
    url = "https://opendata-api.stib-mivb.be/OperationMonitoring/4.0/PassingTimeByPoint/" + formated_stop_id

    # Payload
    payload = {}

    # Headers
    # You need to secure this token be carefull it's fragile
    access_token = 'd86ffa37612eff39c64bacb96053c194'

    # Setup the headers
    headers = {
    'Authorization': 'Bearer ' + access_token,
    'Cookie': 'f5avraaaaaaaaaaaaaaaa_session_=OEEDFHADHAIPEDCPACGJLMHJJHFCELBIFFONKBJEDPDLCCOBLCPONHDHNEIJOKPPCGMDMAGEOMALHLHIHJAAAPLKCGFPGILCLCEFENJHMMCPOAADADGOKJFHONBMHBKE; TS010ea478=0136df15ed8891ae979df14d59421064adc5f7e78b2404e3b7caf5821294aa2c57d1d2895669a6cd21601587f50dccb5d83071c806cc8031eb583a663cc797365ea3a8aa2b'
    }

    # Send the GET request
    response = eval(requests.request("GET", url, headers=headers, data=payload).text)
    print(response)

    # Connect to the db
    sqlite_db = sqlite3.connect('sandbox/data/mcts.db')
    c = sqlite_db.cursor()

    # get the current date and time
    today = str(date.today()).replace('-', '')
    time = datetime.now()
    current_time = time.strftime("%H:%M:00")

    # compute the max time
    max_time = time + timedelta(hours=1)
    max_time = max_time.strftime("%H:%M:00")

    # get the day name
    name_day = time.strftime("%A").lower()

    for stop in response['points']:
        passingTimes_nb = 0
        for passingTimes in stop['passingTimes']:
            destination = passingTimes['destination']['fr']
            lineId = passingTimes['lineId']
            expectedArrivalTime = passingTimes['expectedArrivalTime'].split('T')[1].split('+')[0]

            # get the id of the route
            c.execute('SELECT route_id FROM routes WHERE agency_id=?', (lineId, ))
            route_id = c.fetchone()[0]

            # get the service_id
            c.execute('SELECT trips.service_id FROM calendar, trips WHERE calendar.' + name_day + '=1 AND calendar.start_date<=? AND calendar.end_date>=? AND trips.route_id=? AND calendar.service_id=trips.service_id', (today, today, route_id, ))
            service_id = c.fetchone()[0]

            # get the theoretical schedule
            c.execute('SELECT DISTINCT stop_times.arrival_time FROM stop_times, trips WHERE trips.route_id=? AND trips.trip_headsign=? AND trips.service_id=? AND stop_times.stop_id=? AND stop_times.arrival_time>=? AND stop_times.arrival_time<=? AND stop_times.trip_id=trips.trip_id ORDER BY stop_times.arrival_time ASC', (route_id, destination, service_id, formated_stop_id, current_time, max_time, ))
            theoretical_time = c.fetchmany(99)
            theoretical_time = [i for sub in theoretical_time for i in sub]

            print(formated_stop_id, destination, lineId, expectedArrivalTime)
            print(expectedArrivalTime)
            print(route_id, destination, service_id, formated_stop_id, current_time, max_time)
            print(theoretical_time)

            if expectedArrivalTime in theoretical_time:
                print('No delay')
            else:
                print('Delay')
                expectedArrivalTime = datetime.strptime(expectedArrivalTime, '%H:%M:%S').time()
                theoretical_time_1 = datetime.strptime(theoretical_time[0], '%H:%M:%S').time()
                theoretical_time_2 = datetime.strptime(theoretical_time[1], '%H:%M:%S').time()

                expectedArrivalTime = datetime.combine(date.today(), expectedArrivalTime)
                theoretical_time_1 = datetime.combine(date.today(), theoretical_time_1)
                theoretical_time_2 = datetime.combine(date.today(), theoretical_time_2)

                if passingTimes_nb in [0, 1]:
                    diff = theoretical_time_1 - expectedArrivalTime
                    print(diff.total_seconds()/60)
                elif passingTimes_nb in [2, 3]:
                    diff = theoretical_time_2 - expectedArrivalTime
                    print(diff.total_seconds()/60)
            print('-'*20)
            passingTimes_nb += 1

is_delay(516)