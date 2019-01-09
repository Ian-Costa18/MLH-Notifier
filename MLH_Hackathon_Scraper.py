import requests
from bs4 import BeautifulSoup

# Create URL and headers for bs4
url = "https://mlh.io/seasons/na-2019/events"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
response = requests.get(url, headers=headers)

# Create a Beautiful Soup object with all the HTML
html = BeautifulSoup(response.text, features="html.parser")
# Create a list of events, each item is of type bs4.element.tag
events = list(html.find_all("div", class_="event"))

# Create a debug file to view HTML manually
html_file = open("C:\\Users\\Ian\\source\\repos\\MLH Hackathon Scraper\\html_file.txt", "w")
html_file.write(str(html))
html_file.close()

# Opens baseline and copies it to an array
baseline = open("C:\\Users\\Ian\\source\\repos\\MLH Hackathon Scraper\\baseline.txt", "r")
baseline_lst = (baseline.read()).split("\n")
baseline.close()

class Event:
	"""Holds the name, date, and location for each event"""

	def __init__(self, event_num):
		self.info = []
		self.event_number = event_num

		# Get all strings for the event
		for information in events[self.event_number].stripped_strings:
			self.info.append(information)

		# Assign each string to a variable
		self.name = events[self.event_number].find("a")['title'] # Sometimes title and string don't match, title is always accurate
		self.date = self.info[1]
		self.location = ''.join(self.info[2:])
		# Fix name formatting
		if self.name[0] == " ":
			self.name = self.name[1:]

# Create a class for each event
all_events = []

for event in range(len(events)):
	all_events.append(Event(event))

# Find any new events and add them to new_events array
new_events = []

for event in all_events:
	if event.name not in baseline_lst:
		print(f"{event.name} is new!")
		new_events.append(event)

# Create a file that will store what events aren't new *MUST BE AFTER CHECK*
baseline = open("C:\\Users\\Ian\\source\\repos\\MLH Hackathon Scraper\\baseline.txt", "w")

# Write all events to baseline file
baseline.write("".join(str(i.name)+"\n" for i in all_events))
baseline.close()
print("Finished writing to baseline")