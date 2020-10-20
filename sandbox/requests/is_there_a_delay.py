import requests, sqlite3
from datetime import date, datetime, timedelta

def is_delay(stop_id):
    # The STIB API url
    url = "https://opendata-api.stib-mivb.be/OperationMonitoring/4.0/PassingTimeByPoint/" + stop_id

    # Payload
    payload = {}

    # Headers
    # You need to secure this token be carefull it's fragile
    access_token = 'Place_your_acces_token_here'

    headers = {
    'Authorization': 'Bearer ' + access_token,
    'Cookie': 'f5avraaaaaaaaaaaaaaaa_session_=OEEDFHADHAIPEDCPACGJLMHJJHFCELBIFFONKBJEDPDLCCOBLCPONHDHNEIJOKPPCGMDMAGEOMALHLHIHJAAAPLKCGFPGILCLCEFENJHMMCPOAADADGOKJFHONBMHBKE; TS010ea478=0136df15ed8891ae979df14d59421064adc5f7e78b2404e3b7caf5821294aa2c57d1d2895669a6cd21601587f50dccb5d83071c806cc8031eb583a663cc797365ea3a8aa2b'
    }

    # Start speaking with the STIB API
    response = eval(requests.request("GET", url, headers=headers, data=payload).text)

    for stop in response['points']:
        for passingTimes in stop['passingTimes']:
            destination = passingTimes['destination']['fr']
            lineId = passingTimes['lineId']
            expectedArrivalTime = passingTimes['expectedArrivalTime']
        print(stop_id, destination, lineId, expectedArrivalTime)
    
    sqlite_db = sqlite3.connect('sandbox/data/mcts.db')
    c = sqlite_db.cursor()
    c.execute('SELECT route_id FROM routes WHERE agency_id=?', (lineId, ))
    route_id = c.fetchone()[0]

    today = str(date.today()).replace('-', '')
    time = datetime.now()
    current_time = time.strftime("%H:%M:%S")
    max_time = time + timedelta(hours=1)
    max_time = max_time.strftime("%H:%M:%S")

    c.execute('SELECT trips.service_id FROM calendar, trips WHERE calendar.tuesday=1 AND calendar.start_date<=? AND calendar.end_date>=? AND trips.route_id=? AND calendar.service_id=trips.service_id', (today, today, route_id, ))
    service_id = c.fetchone()[0]

    c.execute('SELECT DISTINCT stop_times.trip_id, stop_times.arrival_time FROM stop_times, trips WHERE trips.route_id=? AND trips.trip_headsign=? AND trips.service_id=? AND stop_times.stop_id="0089" AND stop_times.arrival_time>=? AND stop_times.arrival_time<=? AND stop_times.trip_id=trips.trip_id ORDER BY stop_times.arrival_time ASC', (route_id, destination, service_id, current_time, max_time))
    print(route_id, destination, service_id, current_time, max_time)
    print(c.fetchmany(99))

is_delay("0089")