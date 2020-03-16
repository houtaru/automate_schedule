from google_calendar_api import GoogleCalendarClient

import re
import yaml
from datetime import datetime, timedelta
import argparse
from tabula import read_pdf

def event_entry(summary, 
                description,
                location,
                timezone,
                start_hour,
                end_hour,
                day,
                count
                ):
    """ Create event prototype
    Args:
        summary (str): Contain subject id
        description (str): Contain subject name, teacher infomation
        location (str): room where class takes place
        start_hour (datetime): start time of class
        end_hour (datetime): end time of class
        day (str): day of week when class takes place.
    
    Return:
        event prototype (json)
    """
    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_hour.isoformat(),
            "timeZone": timezone
        },
        "end": {
            "dateTime": end_hour.isoformat(),
            "timeZone": timezone
        },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;COUNT="+ count +";BYDAY=" + day[0:2].upper(),
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {'method': 'popup', 'minutes': 20},
            ]
        }   
    }
    return event

def main():
    # Argument maintainer
    parser = argparse.ArgumentParser(description="Automate schedule.\nConvert schedule file to google calendar.")
    parser.add_argument("--config", default="./config.yaml", help="Configuration file.")
    parser.add_argument("--input", default="./schedule.pdf", help="Input file.")
    args = parser.parse_args()
    
    # Loading configuration file
    with open(args.config) as fin:
        conf = yaml.load(fin, Loader=yaml.FullLoader)
    
    client = GoogleCalendarClient()
    client.load_calendar(conf['calendar-name'])
    
    # process
    timetable, course_info = read_pdf(args.input)
    
    description = {}
    for id in course_info.index:
        s = course_info['Mã môn'][id] + ' - ' + " ".join(course_info['Tên môn'][id].split('\r')) + '\n' + \
        'LT: ' + course_info['GV lý thuyết'][id] + '\n' + \
        ('TH: ' + '\n'.join(course_info['HDTH'][id].split('\r')) + '\n' if not course_info['HDTH'].isna()[id] else "") + \
        'email: ' + "\n".join(course_info['Email'][id].split('\r'))
        description[course_info['Mã môn'][id].split(' ')[0]] = s

    timetable = timetable.drop(['Ca', 'Giờ /Thứ'], axis=1)
    timetable = timetable.drop([2], axis=0)
    timetable.columns = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    period = int(conf['period'].split(' ')[0])
    week_count = conf['last'].split(' ')[0]

    for day in timetable.columns:
        for id in timetable.index:
            if not timetable[day].isna()[id]:
                summary = re.split(' |\r|\(', timetable[day][id])[0]
                location = re.split(' |\r', timetable[day][id])[-1]
                timezone ='Asia/Jakarta'
                start_hour = datetime.strptime(conf['start-date'] + " "
                        + conf['timeline'][id], "%Y.%m.%d %H:%M") + timedelta(days=timetable.columns.get_loc(day))
                end_hour = start_hour + timedelta(hours=period)
                result = client.insert_event(event_entry(
                    summary, description[summary], location, timezone, start_hour, end_hour, day, week_count
                ))
                print(summary, location, timezone, start_hour, end_hour, result,"", sep='\n');



if __name__ == "__main__":
	main()
