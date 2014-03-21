# Triathlon Leaderboard

Provides a set of command line tools to interact with the sportrelief/comicrelief leaderboards.

### scraper.py

`scraper.py` is the backend that deals with scraping through the \*relief website and returning a dictionary of fundraisers. Additionally it contains a class to output the results into a static HTML file

Command line usage

    usage: scraper.py [-h] [-v] [-w WORKERS] [-t TEAM] [-o OUTPUT_FILE]
                      [--extra-participants team:group [team:group ...]]

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Log verbosely to stdout
      -w WORKERS, --workers WORKERS
                            Maximum amount of concurrent workers. Defaults to 30
      -t TEAM, --team TEAM  Name of master sport relief team. Defaults to
                            greenparktriathlon
      -o OUTPUT_FILE, --output-file OUTPUT_FILE
                            Name of the file to output to
      --extra-participants team:group [team:group ...]
                            A list of extra participants that are not connected to
                            the master team. Provided in the format name:team e.g.
                            mightymags:Yes

### namecheck.py

`namecheck.py` can be used to correlate the fundraiser names in a spreadsheet against names on the \*relief website. This is useful for finding fundraising pages that might have been missed

### fundcheck.py

`fundcheck.py` can be used to correlate fundraiser email addresses against \*relief pages that have a certain value or less funds in their balance. This is useful for chasing up those who have not started fundraising yet

Command line usage

    usage: fundcheck.py [-h] [-db DATABASE] [-f] [-s SPREADSHEET] [-o OUTPUT]

    Compares a list of fundraisers scraped from the sport relief website against a
    static list of known team names and emails.

    optional arguments:
      -h, --help            show this help message and exit
      -db DATABASE, --database DATABASE
                            Database to store known values
      -f, --funds           Update funds table
      -s SPREADSHEET, --spreadsheet SPREADSHEET
                            Update spreadsheet table based on input CSV
      -o OUTPUT, --output OUTPUT
                            Output spreadsheet
