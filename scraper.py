# coding=utf-8
import argparse
import re

__author__ = 'tigarner'
'''
Scrape all participants for a particular comic relief fundraising team. Builds up a list of dictionaries for
every user. Will then sort by highest total, and then calculate top 3 teams and top 3 single participants.
Also scrapes the full total. Produces a HTML page using a Jinja2 Template. Scraping is provided by BeautifulSoup4
'''
import urllib2
import itertools
from operator import itemgetter
from datetime import datetime
import logging
import os

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from concurrent.futures import ThreadPoolExecutor


class TotalRender(object):
    @staticmethod
    def output_html(participants, total, path, outfile):
        # Create a jinja2 environment based on where the script currently resides
        env = Environment(loader=FileSystemLoader(path))

        # Sort the particpants based on total and name, descending
        participants.sort(key=itemgetter('total', 'name'), reverse=True)

        # Create a few seperate lists and totals depending on whether this is a group entry or not
        group = filter(lambda a: a['group'] == 'Yes', participants)
        group_total = sum(item['total'] for item in group[:3])
        single = filter(lambda a: a['group'] == 'No', participants)
        single_total = sum(item['total'] for item in single[:3])

        # Load the template and render using calculated values, save to stats.php
        template = env.get_template('template.html')

        with open(os.path.join(path, outfile), 'wb') as stats:
            stats.write(template.render(participants=participants, total=total, group=group[:3], single=single[:3],
                                        group_total=group_total, single_total=single_total, now=datetime.now()))


class TotalScraper(object):
    def __init__(self, base_url='http://my.rednoseday.com/sponsor/', team_name='green-park-triathlon',
                 extra_sponsors=None, max_workers=30):
        self.base_url = base_url
        self.team_name = team_name
        self.full_team_name = base_url + team_name
        self.extra_sponsors = extra_sponsors
        self.participants = []
        self.total = 0
        self.pool = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def scrape_totals(self):
        #Scrape the first page
        logging.info('Scrape starting at: '.format(datetime.now()))
        response = urllib2.urlopen(self.full_team_name)
        soup = BeautifulSoup(response.read())

        #Grap the total from the first page
        total = soup.find('div', {'class': 'gauge'})
        self.total = int(total.get('data-donation-total').decode("ascii"))

        #While 'next' button appears on page, follow the link and scrape all participants
        for soup in self._scrape_all_valid_team_members():
            self._process_page_of_members_from_soup(soup)

        [logging.debug(fut.result()) for fut in self.futures]

        #Get any extra sponsors that are not linked with the parent team
        additional_total = self._get_extra_sponsors(self.extra_sponsors)

        logging.info("Original Total: {} , Additional Total: {}".format(str(self.total), str(additional_total)))
        self.total += additional_total
        logging.info("New Total: " + str(self.total))
        logging.info('Scraping finished at: {}'.format(datetime.now()))

        return self.total, self.participants

    def _scrape_all_valid_team_members(self):
        """
        Generator that returns a list of all beautiful soup objects with valid team members. Will stop when no team
        more team members can be found.
        """
        for page_id in itertools.count(start=1):
            logging.info('Checking page {} contains team members'.format(page_id))
            url = self.full_team_name + "?page[members-ranked]={}".format(page_id)
            s = BeautifulSoup(urllib2.urlopen(url).read())
            if s.find('div', {'class': 'member'}):
                logging.info('Page {} contains team members. Scraping team member totals'.format(page_id))
                yield s
            else:
                logging.info('Page {} contains no team members. Stopping search'.format(page_id))
                raise StopIteration

    def _process_page_of_members_from_soup(self, soup):
        """
        Returns: A beautifulsoup object bound to the original response

        Find all divs with the class 'member'. Will execute further scraping of individual members in parallel Threads.
        """
        logging.debug("processing page of members with soup ".format(soup))
        for div in soup.find_all('div', {'class': 'member'}):
            self.futures.append(self.pool.submit(self._process_individual_member, div))

    def _process_individual_member(self, div):
        """
        Take a beautiful soup div object and scrape all pertinent data. If it is a normal profile (has a link to
        profile page) follow that link and get detailed information about member. If not (private page) leave some
        information blank. Will catch and deal with any 'placeholder' members.
        """
        logging.debug("processing member with div {}".format(div))
        div = div.div
        if div.a:
            url = div.a.get('href')
            str(url).replace('https', 'http')
            s = BeautifulSoup(urllib2.urlopen(url).read())
            name = s.find('div', {'class': 'profile-head'})
            name = name.h3.get_text().encode("ascii", "ignore")
            group = 'Yes' if "Team" in name else 'No'
            amount_raised = div.a.p.get_text()
            amount_raised = float(re.findall(u'Amount raised £([\d\.]+)', amount_raised)[0])
            self.participants.append(
                {'name': name, 'total':amount_raised, 'group': group,
                 'url': url})
        elif div.h6 and div.p:
            amount_raised = div.p.get_text()
            amount_raised = float(re.findall(u'Amount raised £([\d\.]+)', amount_raised)[0])
            self.participants.append(
                {'name': div.h6.get_text().encode("ascii", "ignore"),
                 'total': amount_raised, 'group': '?',
                 'url': '#'})
        else:
            logging.warning('Could not find ANY data to scrape: probably a placeholder portrait on last page.')


    def _get_extra_sponsors(self, sponsors):
        """
        Take a list of sponsor tuples in format (sponsorname, group). Returns an additional total while adding any
        scrapped participants to the instances list of participants.
        """
        additional_total = 0
        if sponsors:
            for sponsor in sponsors:
                url = self.base_url + sponsor[0]
                response = urllib2.urlopen(url)
                s = BeautifulSoup(response)
                name = s.find('div', {'class': 'profile-head'})
                name = name.h3.get_text()
                total = s.find('div', {'class': 'gauge'})
                total = total.get('data-donation-total').decode("ascii").replace(',', '')
                additional_total += float(total)
                self.participants.append(
                    {'name': name, 'total': float(total), 'group': sponsor[1], 'url': url})
        return additional_total


def main():
    # Set the timezone to London
    os.environ['TZ'] = 'Europe/London'
    # Get the local path of the script
    path = os.path.dirname(os.path.realpath(__file__))
    # Start Logging
    logging.basicConfig(filename=path + '/scraper.log', level=logging.INFO)

    parser = argparse.ArgumentParser(description=TotalScraper.__doc__)
    parser.add_argument('-v', '--verbose', help='Log verbosely to stdout', action='store_false')
    parser.add_argument('-w', '--workers', help='Maximum amount of concurrent workers. Defaults to 30', default='30')
    parser.add_argument('-t', '--team', help='Name of master sport relief team. Defaults to greenparktriathlon',
                        default='green-park-triathlon')
    parser.add_argument('-o', '--output-file', help='Name of the file to output to', default='stats.php')
    parser.add_argument('--extra-participants', nargs='+', metavar='team:group',
                        help='''A list of extra participants that are not connected to the master team.
                                Provided in the format name:team e.g. mightymags:Yes''')
    args = parser.parse_args()
    print args
    extra_participants = []
    if args.extra_participants:
        for extra_participant in args.extra_participants:
            extra_participants.append(tuple(extra_participant.split(':')))

    print extra_participants

    total_scraper = TotalScraper(team_name=args.team, extra_sponsors=extra_participants, max_workers=args.workers)
    total, participants = total_scraper.scrape_totals()
    TotalRender.output_html(participants, total, path, args.output_file)


if __name__ == '__main__':
    main()