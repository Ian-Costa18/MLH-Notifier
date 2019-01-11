"""A script that finds new hackathons posted to 'https://mlh.io/seasons/na-2019/events'"""

import json
import requests
from bs4 import BeautifulSoup
from slackclient import SlackClient

# Create URL and headers for bs4
URL = "https://mlh.io/seasons/na-2019/events"
HEADERS = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                          + "AppleWebKit/537.36 (KHTML, like Gecko) "
                          + "Chrome/39.0.2171.95 Safari/537.36")}
RESPONSE = requests.get(URL, headers=HEADERS)

# Create a Beautiful Soup object to parse HTML
HTML = BeautifulSoup(RESPONSE.text, features="html.parser")

# Create a list of events, each item is of type bs4.element.tag
EVENT_LST = list(HTML.find_all("div", class_="event"))

# Copies old events to a list
with open("baseline.json", 'r') as file:
    BASELINE_LST = json.load(file)


class Event:
    """Holds information about each event"""

    def __init__(self, event_num):
        event_strings = []
        self.event_number = event_num

        # Get all strings for the event
        for information in EVENT_LST[self.event_number].stripped_strings:
            event_strings.append(information)

        # Assign variables
        # Sometimes title and string don't match, title is always accurate
        self.name = EVENT_LST[self.event_number].find("a")["title"]
        self.date = [event_strings[1],
                     EVENT_LST[self.event_number].find(itemprop="startDate")["content"],
                     EVENT_LST[self.event_number].find(itemprop="endDate")["content"]]
        self.location = ''.join(event_strings[2:])
        self.link = EVENT_LST[self.event_number].find("a")["href"]
        self.highschool = EVENT_LST[self.event_number].find("div", class_="ribbon-wrapper")

        # Fix name formatting
        if self.name[0] == " " or self.name[-1] == " ":
            self.name = self.name.strip()

        # Create json object
        self.json = {
            "Event number": self.event_number,
            "Name": self.name,
            "Date": self.date[0],
            "Start Date": self.date[1],
            "End Date": self.date[2],
            "Location": self.location,
            "Link": self.link,
            "HS only?": bool(self.highschool)
            }



# Create a object for each event
all_events, new_events = [], []

for count in range(len(EVENT_LST)):
    temp_event = Event(count)
    # Create object then append to all_events
    all_events.append(temp_event)
    print(f"Found event: {all_events[count].name}")

    # Find any new events and add them to new_events array
    if temp_event.name not in (i["Name"] for i in BASELINE_LST):
        print(f"{temp_event.name} is new!")
        new_events.append(temp_event)

# Write all events to JSON file
with open("baseline.json", 'w') as file:
    json.dump(list((event.json for event in all_events)), file, indent=4)

# Check if there are any new events
if new_events:
    # Create a list of information for each new event
    new_events_info = []
    for event in new_events:
        if event.highschool:
            new_events_info.append(', '.join([
                "*HS ONLY*",
                event.name,
                event.date,
                event.date[1][:4],
                event.location,
                event.link]))
        else:
            new_events_info.append(', '.join([
                event.name,
                event.date,
                event.date[1][:4],
                event.location,
                event.link]))

    # Create slack bot with token
    SLACK_TOKEN = "xoxp-462859149221-461928926352-521487611223-38de2124744a529dd081d455f8df4a72"
    SLACK_CLIENT = SlackClient(SLACK_TOKEN)

    # Craft slack message string and add "s" if applicable
    S = 's' if len(new_events) != 1 else ''
    SLACK_MESSAGE = f"{len(new_events_info)} new event{S} found!\n"
    for event in new_events_info:
        SLACK_MESSAGE += event + "\n"

    # Send slack message on channel
    CHANNEL = "#bottest"

    SLACK_CLIENT.api_call("chat.postMessage", channel=CHANNEL, text=SLACK_MESSAGE)
