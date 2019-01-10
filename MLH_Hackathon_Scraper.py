import requests
from bs4 import BeautifulSoup
from slackclient import SlackClient

# Create URL and headers for bs4
URL = "https://mlh.io/seasons/na-2019/events"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
response = requests.get(URL, headers=HEADERS)

# Create a Beautiful Soup object with all the HTML
HTML = BeautifulSoup(response.text, features="html.parser")

# Create a list of events, each item is of type bs4.element.tag
event_lst = list(HTML.find_all("div", class_="event"))

# Create a debug file to view HTML manually DEBUG
html_file = open("html_file.txt", "w")
html_file.write(str(HTML))
html_file.close()

# Copies old hackathons to an array
baseline = open("baseline.txt", "r")
baseline_lst = (baseline.read()).split("\n")
baseline.close()

class Event:
	"""Holds the name, date, and location for each event"""

	def __init__(self, event_num):
		self.info = []
		self.event_number = event_num

		# Get all strings for the event
		for information in event_lst[self.event_number].stripped_strings:
			self.info.append(information)

		# Assign variables
		self.name = event_lst[self.event_number].find("a")['title'] # Sometimes title and string don't match, title is always accurate
		self.date = self.info[1]
		self.location = ''.join(self.info[2:])
		self.link = event_lst[self.event_number].find("a")['href']
		# TODO Create a variable for if the hackathon is high school only, might use ribbon tag

		# Fix name formatting
		if self.name[0] == " " or self.name[-1] == " ":
			self.name = self.name.strip()


# Create a object for each event
all_events, new_events = [], []


for count in range(len(event_lst)):
	temp_event = Event(count)
	# Create object then append to all_events
	all_events.append(temp_event)
	print(f"Found event: {all_events[count].name}")

	# Find any new events and add them to new_events array
	if temp_event.name not in baseline_lst:
		print(f"{temp_event.name} is new!")
		new_events.append(temp_event)

print("Finished creating events")

## Create a file that will store what events aren't new *MUST BE AFTER CHECK*
baseline = open("baseline.txt", "w")
baseline.write("".join(str(i.name)+"\n" for i in all_events))
baseline.close()
print("Finished writing to baseline")

# TODO alert for new events

# Create things for slack bot
slack_token = ""
slack_client = SlackClient(slack_token)

# Craft the message if there are new events
if new_events:
	new_events_info = []
	for event in new_events:
		new_events_info_temp = []
		new_events_info_temp.append(event.name)
		new_events_info_temp.append(event.date)
		new_events_info_temp.append(event.location)
		new_events_info_temp.append(event.link)
		new_events_info.append(', '.join(new_events_info_temp))
	
	text = f"{len(new_events_info)} new events found!\n"
	for event in new_events_info:
		text += event + "\n"
	
	# Channel IDs: bottest=CF9LTRCSU, 

	slack_client.api_call(
        "chat.postMessage",
        channel="CF9LTRCSU",
        text=text)
