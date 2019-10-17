from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from AppKit import NSSound
import speech_recognition as sr
import pyttsx3
import os
import time
import pytz
import subprocess
#GOOGLE CALENDAR API SOURCE = https://developers.google.com/calendar/quickstart/python
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january','february','march','april','may','june','july','august','september','october','november','december']
DAYS = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
EXTENTIONS = ['rd','nd','st','th']

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        what_I_said = ""
        try:
            what_I_said = r.recognize_google(audio)
            print(what_I_said)
        except:
            print("I can not hear what you are saying")
    return what_I_said.lower()

def authenticate_googleCal():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

#def get_GoogleEvents(day, service):
#The above code is basically for credentials so I do not need to revalidate and go back to web broswers to sign in
#IT automatically creates a picke file of all my information
def get_GoogleEvents(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end = end.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('You have no events, boring ass')
    else:
        speak(f"You have {len(events)} on this day")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1] #include minute aspect too
                start_time = start_time + "pm"
            speak(events['summary'] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)

# text = get_audio().lower()
# print(get_date(text))

wake_call = "hey sexy"
SERVICE = authenticate_googleCal()
print("Start Speaking")

while True:
    print("LISTENING.....")
    text = get_audio()

    if text.count(wake_call) > 0:
        speak("I am hearing your sexy voice, what do you need")
        text = get_audio()
        CALENDAR_CALLS = ["what do I have", "do I have plans", "events", "am I busy","Google Calendar"]
        for phrase in CALENDAR_CALLS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_GoogleEvents(date,SERVICE)
                else:
                    speak("I do not understand you")
        QUIT_CALLS = ['peace','bye','quit']
        for phrase in QUIT_CALLS:
            if phrase in text:
                exit()
        SPOTIFY = ['open spotify']
        for phrase in SPOTIFY:
            if phrase in text:
                subprocess.call()
