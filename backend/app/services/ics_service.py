import datetime
from typing import List, Optional

def generate_interview_ics(
    summary: str,
    description: str,
    start_time: datetime.datetime,
    duration_minutes: int = 60,
    location: str = "Google Meet / Video Call"
) -> str:
    """
    Generates standard RFC 5545 iCalendar content with VALARM reminders
    at 3 days, 1 day, and 1 hour before the interview (Slide 13).
    """
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)
    
    # Format dates in UTC iCalendar style: YYYYMMDDTHHMMSSZ
    dtstamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_time.strftime("%Y%m%dT%H%M%SZ")
    dtend = end_time.strftime("%Y%m%dT%H%M%SZ")
    uid = f"coachpath-interview-{int(start_time.timestamp())}@coachpath.ai"
    
    clean_desc = description.replace("\n", "\\n")
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CoachPath AI//Interview Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{clean_desc}
LOCATION:{location}
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-P3D
ACTION:DISPLAY
DESCRIPTION:Reminder: Interview in 3 days - Review prep checklist!
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Reminder: Interview tomorrow - Final mock practice & company research!
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Reminder: Interview starts in 1 hour - Test audio/video and join link!
END:VALARM
END:VEVENT
END:VCALENDAR"""
    return ics_content
