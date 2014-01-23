__author__ = 'tigarner'
'''
Scrape all participants for a particular comic relief fundraising team. Builds up a list of dictionaries for
every user. Will then sort by highest total, and then calculate top 3 teams and top 3 single participants.
Also scrapes the full total. Produces a HTML page using a Jinja2 Template. Scraping is provided by BeautifulSoup4
'''
import urllib2
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from operator import itemgetter
from ftplib import FTP
from datetime import datetime
import logging
import os
import grapher
os.environ['TZ'] = 'Europe/London'

def get_members(response):
    """
    Args: response is a response object from urllib2.open
    Returns: A beautifulsoup object bound to the original response

    Find all divs with the class 'portrait'. If it is a normal profile (has a link to profile page) follow that link
    and get detailed information about member. If not (private page) leave some information blank. Will catch and deal
    with any 'placeholder' members.
    """
    soup = BeautifulSoup(response.read())
    if soup:
        for div in soup.find_all('div',{'class':'member'}):
            div = div.div
            if div.a:
                url = div.a.get('href')
                str(url).replace('https','http')
                s = BeautifulSoup(urllib2.urlopen(url).read())
                name = s.find('div', {'class':'profile-head'})
                name = name.h3.get_text()
                group = 'Yes' if "Team" in name else 'No'
                participants.append({'name':name,'total':float(div.a.p.get_text().replace(u"\xa3","")), 'group' : group, 'url' : url})
            elif div.h6 and div.p:
                participants.append({'name':div.h6.get_text(),'total':float(div.p.get_text().replace(u"\xa3","")), 'group' : '?', 'url':'#'})
            else:
                pass
                logging.warning('Could not find ANY data to scrape: probably a placeholder portrait on last page.')
        return soup
    else:
        print 'Seems there was a problem loading the page'
        exit(1)


def get_extra_sponsors(sponsors):
    additional_total = 0
    for sponsor in sponsors:
        url = u'http://my.sportrelief.com/sponsor/' + sponsor[0]
        response = urllib2.urlopen(url)
        s = BeautifulSoup(response)
        total = s.find('div',{'class':'gauge'})
        total = total.get('data-donation-total').decode("ascii")
        additional_total += int(total)
        split_total = additional_total / 2
        name = s.find('div', {'class':'profile-head'})
        name = name.h1.get_text()
        participants.append({'name': 'Too INcredible*', 'total': float(split_total), 'group': sponsor[1], 'url': url})
        participants.append({'name': 'Even More INcredible*', 'total': float(split_total), 'group': sponsor[1], 'url': url})

    return additional_total

def check_next(soup):
    '''
    Args: soup is a beautifulsoup object
    Returns: True if another page is available to scrape
    '''
    global next_url
    for a in soup.find_all('a', {'class':'pagination_button'}):
        if a.get('title') == 'Next':
            logging.info('Found next page, continuing...')
            next_url = 'http://my.sportrelief.com/sponsor/greenparktriathlon' + a.get('href')
            return True
    logging.info('No next button, must be the final page')
    return False


def move_page():
    ''' Return the response object for the next page '''
    return urllib2.urlopen(next_url)

#Get Path
_path = os.path.dirname(os.path.realpath(__file__))

#Start Logging
logging.basicConfig(filename=_path + '/scraper.log',level=logging.DEBUG)

#Globals
env = Environment(loader=FileSystemLoader(_path))
participants = []
#extra_sponsors = [('intermecgreenparktriathlon2013', 'Yes')]
next_url = ''
page = 1

#Scrape the first page
logging.info('Scrape starting at: ' + str(datetime.now()))
logging.info('Scraping Page: ' + str(page))
response = urllib2.urlopen('http://my.sportrelief.com/sponsor/greenparktriathlon')
soup = get_members(response)

#While we're here may as well grab the total
total = soup.find('div',{'class':'gauge'})
total = int(total.get('data-donation-total').decode("ascii"))

#While 'next' button appears on page, follow the link and scrape all participants
while check_next(soup):
    page += 1
    logging.info('Scraping Page: ' + str(page))
    soup = get_members(move_page())

#Get any extra sponsors
additional_total = 0 #get_extra_sponsors(extra_sponsors)

logging.info("Original Total: {} , Additional Total: {}".format(str(total), str(additional_total)))
total += additional_total
logging.info("New Total: " + str(total))

#Sort the particpants based on total and name, descending
participants.sort(key=itemgetter('total','name'), reverse=True)

#Create a few seperate lists and totals depending on whether this is a group entry or not
group = filter(lambda a: a['group'] == 'Yes', participants)
group_total = sum(item['total'] for item in group[0:3])
single = filter(lambda a: a['group'] == 'No', participants)
single_total = sum(item['total'] for item in single[0:3])

#Load the template and render using calculated values, save to stats.php
template = env.get_template('template.html')
stats = open(_path + '/stats.php','w+')
stats.write(template.render(participants=participants, total=total, group=group[0:3],single=single[0:3],group_total=group_total,single_total=single_total,now=datetime.now()))
stats.close()

#Upload the final file to the server
ftp = FTP('ftp.greenparktriathlon.co.uk', 'greenparktriathlon.co.uk', 'kC!9Eybts')
ftp.storlines('STOR /public_html/stats.php', open(_path + '/stats.php','r'))

logging.info('Scraping finished at: ' + str(datetime.now()))

logging.info('Updating Graph')
grapher.create_graph(values=
                    {
                        'total':total,
                        'total_compt': (252,306),
                        'sprint_indv': (117, 76),
                        'funathon_indv': (28, 39),
                        'sprint_team': (29, 44),
                        'funathon_team': (9, 22)
                    }
                    )