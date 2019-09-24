import json
import calendar
from datetime import datetime, timedelta
from calendarapi import get_calendar_service, insertEvent

def read_json(path='data.json'):
	with open(path, encoding='utf-8') as db:
		data = json.load(db)
	return data['schedule'], data['room'], data['time'], data['description']

log = open('log.txt', 'w')

def print_log(event_result):
	print(event_result['id'], file=log)
							
	print('id:', event_result['id'])
	print('summary:', event_result['summary'])
	print("starts at:", event_result['start']['dateTime'])
	print("ends at:", event_result['end']['dateTime'], '\n')

def main():
	sched, room, time, desc = read_json()

	for period in sched:
		cnt = 0  # Difference between firstDay and current day
		for day in list(calendar.day_abbr):
			if day != 'Sun':
				if period[day] != '':
					subject = period[day]
					location = room[subject]
					description = desc[subject]
					timezone = 'Asia/Jakarta'
					start_time = datetime.strptime("2019.10.07 "
						+ time[str(period['id'])]['start'], "%Y.%m.%d %H:%M") + timedelta(days=cnt)
					end_time = start_time + timedelta(hours=2)
					
					event_result = insertEvent(subject, location, description, start_time, end_time, timezone, day) 
					print_log(event_result)
			
			cnt += 1


if __name__ == "__main__":
	main()
