import requests
from bs4 import BeautifulSoup
from slackclient import SlackClient
import json

# Create URL and headers for bs4
URL = "https://mlh.io/seasons/na-2019/events"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
response = requests.get(URL, headers=HEADERS)

# Create a Beautiful Soup object to parse HTML
HTML = BeautifulSoup(response.text, features="html.parser")

# Create a list of events, each item is of type bs4.element.tag
event_lst = list(HTML.find_all("div", class_="event"))

# Copies old hackathons to a list
with open("baseline.json", 'r') as file:
	baseline_lst = json.load(file)


class Event:
	"""Holds information about each event"""

	def __init__(self, event_num):
		self.info = []
		self.event_number = event_num

		# Get all strings for the event
		for information in event_lst[self.event_number].stripped_strings:
			self.info.append(information)

		# Assign variables
		self.name = event_lst[self.event_number].find("a")["title"] # Sometimes title and string don't match, title is always accurate
		self.date = self.info[1]
		self.start_date = event_lst[self.event_number].find(itemprop="startDate")["content"]
		self.end_date = event_lst[self.event_number].find(itemprop="endDate")["content"]
		self.location = ''.join(self.info[2:])
		self.link = event_lst[self.event_number].find("a")["href"]
		self.highschool = event_lst[self.event_number].find("div", class_="ribbon-wrapper")

		# Fix name formatting
		if self.name[0] == " " or self.name[-1] == " ":
			self.name = self.name.strip()

		# Create json object
		self.json = {
					"Event number": self.event_number,
					"Name": self.name,
					"Date": self.date,
					"Start Date": self.start_date,
					"End Date": self.end_date,
					"Location": self.location,
					"Link": self.link,
					"HS only?": True if self.highschool else False
			}



# Create a object for each event
all_events, new_events = [], []

for count in range(len(event_lst)):
	temp_event = Event(count)
	# Create object then append to all_events
	all_events.append(temp_event)
	print(f"Found event: {all_events[count].name}")

	# Find any new events and add them to new_events array
	if temp_event.name not in (i["Name"] for i in baseline_lst):
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
				event.start_date[:4],
				event.location,
				event.link]))
		else:
			new_events_info.append(', '.join([
				event.name,
				event.date,
				event.start_date[:4],
				event.location,
				event.link]))

	# Create slack bot with token
	slack_token = "xoxp-462859149221-461928926352-521487611223-38de2124744a529dd081d455f8df4a72"
	slack_client = SlackClient(slack_token)
	
	# Craft slack message string
	slack_message = f"{len(new_events_info)} new event(s) found!\n"
	for event in new_events_info:
		slack_message += event + "\n"

	# Send slack message on channel
	channel = "#bottest"

	slack_client.api_call("chat.postMessage",channel=channel,text=slack_message)
