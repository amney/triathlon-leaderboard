"""
    Fundcheck - Return a CSV of sport relief fundraisers with less
    than a specfied amount matched against known email addresses
"""
import argparse
import csv
import re
import sqlite3

from scraper import TotalScraper


__author__ = 'tigarner'
__email__ = 'tigarner@cisco.com'


class FundCheck(object):
    """
        Compares a list of fundraisers scraped from the sport relief website against a static list of known
        team names and emails.
    """

    def __init__(self, database='fundcheck.db', update_funds=False, input_csv=None, output_csv='fundcheck.csv'):
        self.database = database
        self.update_funds = update_funds
        self.input_csv = input_csv
        self.output_csv = output_csv

    def _create_tables(self):
        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            try:
                c.execute('''CREATE TABLE funds (name text, isgroup text, total real, url text)''')
                c.execute('''CREATE TABLE ss (fullname text, teamname text, email text)''')
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def _update_funds(self):
        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            ts = TotalScraper()
            total, participants = ts.scrape_totals()
            funds = [(p['name'], p['group'], p['total'], p['url']) for p in participants]
            c.execute('DELETE FROM funds WHERE 1=1')
            c.executemany('INSERT INTO funds VALUES (?, ?, ?, ?)', funds)
            conn.commit()

    def _update_ss(self):
        with open(self.input_csv, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            participants = []
            for row in reader:
                full_name = ("{} {}".format(row[0].strip(), row[1].strip())).lower()
                team_name = (row[3]).lower().strip()
                team_name = re.sub(r'\bthe\b', '', team_name)
                #team_name = "Team %s" % team_name
                if team_name != '':
                    if not team_name.startswith('team'):
                        team_name = "team %s" % team_name
                email = row[2]
                participants.append((full_name, team_name, email))

        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM ss WHERE 1=1')
            c.executemany('INSERT INTO ss (fullname, teamname, email) VALUES (?, ?, ?)', participants)
            conn.commit()

    def execute(self):
        """Returns a list of tuples containing fundraiser details"""
        self._create_tables()
        if self.update_funds:
            self._update_funds()
        if self.input_csv:
            self._update_ss()

        with sqlite3.connect(self.database) as conn:
            c = conn.cursor()
            c.execute(
                """SELECT s.fullname, s.teamname, s.email, f.total FROM ss as s INNER JOIN funds as f ON
                    s.fullname LIKE '%' || f.name || '%'  OR
                    s.teamname LIKE '%' || f.name || '%'  WHERE
                    f.total < 100
                    ORDER BY f.total DESC;""")
            return c.fetchall()

    def write_csv(self, records):
        """Writes a list of tuples to disk"""
        with open(self.output_csv, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=FundCheck.__doc__)
    parser.add_argument('-db', '--database', help='Database to store known values', default='fundcheck.db')
    parser.add_argument('-f', '--funds', help='Update funds table', action='store_true')
    parser.add_argument('-s', '--spreadsheet', help='Update spreadsheet table based on input CSV')
    parser.add_argument('-o', '--output', help='Output spreadsheet', default='fundcheck.csv')
    args = parser.parse_args()
    print args
    fc = FundCheck(database=args.database, update_funds=args.funds, input_csv=args.spreadsheet, output_csv=args.output)
    fc.write_csv(fc.execute())