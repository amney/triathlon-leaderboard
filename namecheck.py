import re

__author__ = 'tigarner'
__email__ = 'tigarner@cisco.com'

from scraper import TotalScraper
import csv

total_scraper = TotalScraper()
total, participants = total_scraper.scrape_totals()



names = [participant['name'].lower() for participant in participants]
found_full_name = []
found_team_name = []
not_found = []

with open('participants3.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        full_name = ("{} {}".format(row[0].strip(), row[1].strip())).lower()
        team_name = (row[2]).lower().strip()
        team_name = re.sub(r'\bthe\b', '', team_name)
        if any(full_name in name for name in names):
            found_full_name.append("found {} in names".format(full_name))
        elif team_name != "" and any(team_name in name for name in names):
            found_team_name.append("found {} in teams".format(team_name))
        else:
            not_found.append("can't find {} - {}".format(full_name, team_name))

print "Full list of participants"
print "--------------------"
for name in names: print name

print "Found Full Name"
print "--------------------"
for name in found_full_name: print name

print "Found Team Name"
print "--------------------"
for name in found_team_name: print name

print "Not Found Full Name"
print "--------------------"
for name in not_found: print name
