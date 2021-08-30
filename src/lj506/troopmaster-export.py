#
# Use Selenium to download export files from TroopMaster
#
import argparse
import datetime
import sys
import time
from pathlib import Path

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from lj506 import __version__


class TMFailure(Exception):
    ...


import os

PASSWORD = os.getenv('TM_506_PASSWORD')

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def select_site(b):
    """Select the Troops website. Note necessary if the mysite/Troop506 address is given """

    try:
        drop = Select(b.find_element_by_id('States'))
        drop.select_by_value("CA")
        time.sleep(2)
        drop = Select(b.find_element_by_id('UnitNums'))
        drop.select_by_value("506")
        time.sleep(2)
    except NoSuchElementException as e:
        pass


def login(b):
    try:
        b.find_element_by_id("userid").send_keys("eric.busboom")
        b.find_element_by_id("password").send_keys(PASSWORD)
        b.find_element_by_class_name('btn-primary').click()
        logger.info(f'Logged in')
    except NoSuchElementException as e:
        logger.info(f'Not logging in: {e}')
        pass


def download_adult_report(b):
    # These might be required to get the right cookies, but
    # it does seem to work without it, at least occassionally.
    # WebDriverWait(b, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Reports"))).click()
    # WebDriverWait(b, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Custom Reports"))).click()
    # WebDriverWait(b, 10).until(EC.presence_of_element_located((By.XPATH,"(//a[contains(text(),'Adults')])[4]"))).click()

    s = requests.Session()
    s.cookies.update({c['name']: c['value'] for c in b.get_cookies()})

    d = '{"title":"Auto Adult List","memberFilter":"All Adults","includeRemarks":false,"includeMedications":false,"includeAllergies":false,"doubleSpace":false,"list11":"Name","list12":"Cell Phone","list13":"Email","list14":"BSA ID#","list15":"Leadership Position","list16":"Became Leader","list21":"","list22":"","list23":"","list24":"","list25":"","list26":"","list31":"","list32":"","list33":"","list34":"","list35":"","list36":""}'

    h = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
        "Content-Type": "application/json",
    }

    r = s.post('https://tmweb.troopmaster.com/Reports/RepCustomAdults', data=d, headers=h)
    r.raise_for_status()

    c = r.json()
    if not c.get('success'):
        raise TMFailure(str(c))

    r = s.get("https://tmweb.troopmaster.com/Reports/DownloadExport?fileName=CustomExport.CSV")
    r.raise_for_status()

    logger.info(f'Fetched custom report for adults, len={len(r.content)}')

    return r.content


def download_scout_report(b):
    s = requests.Session()
    s.cookies.update({c['name']: c['value'] for c in b.get_cookies()})

    d = '{"title":"Auto Scout List","separatePage":false,"memberFilter":"All Scouts",' \
        '"includeRemarks":false,"includeMedications":false,"includeAllergies":false,' \
        '"doubleSpace":false,"sortBy":"DOB",' \
        '"list11":"BSA ID#","list12":"Age","list13":"Phone","list14":"School","list15":"Parent1 Name","list16":"Parent2 Email",' \
        '"list21":"Name","list22":"Gender","list23":"Leadership Position","list24":"Parent2 Name","list25":"","list26":"",' \
        '"list31":"Email","list32":"Rank","list33":"Patrol","list34":"Parent1 Email","list35":"","list36":""}'

    h = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
        "Content-Type": "application/json",
    }

    r = s.post('https://tmweb.troopmaster.com/Reports/RepCustomScouts', data=d, headers=h)
    r.raise_for_status()

    c = r.json()
    if not c.get('success'):
        raise TMFailure(str(c))

    r = s.get("https://tmweb.troopmaster.com/Reports/DownloadExport?fileName=CustomExport.CSV")
    r.raise_for_status()

    logger.info(f'Fetched custom report for scouts, len={len(r.content)}')

    return r.content


def download_export(b):
    """Get the TroopLedge export"""

    s = requests.Session()
    s.cookies.update({c['name']: c['value'] for c in b.get_cookies()})

    # Wait for the page to load; looking for the File menu
    WebDriverWait(b, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "File"))
    )

    b.get('https://tmweb.troopmaster.com/Export/ledger')

    # Click the button to generate the report
    WebDriverWait(b, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "btn-sm"))
    ).click()

    # Wait until download link appears
    WebDriverWait(b, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Click here to download Ledger Export File."))
    )

    # Directly download the file.
    r = s.get("https://tmweb.troopmaster.com/Export/DownloadFile?fName=Ledger.txt")

    r.raise_for_status()

    logger.info(f'FetchedLedge export, len={len(r.content)}')

    return r.content


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version="lj506 {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    parser.add_argument('--dir', '-d', help="Download directory", default=Path.cwd())

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)

    dpath = Path(args.dir)

    if not dpath:
        dpath = Path.cwd()

    dt = datetime.datetime.now().replace(microsecond=0, second=0, minute=0).isoformat()

    dtpath = dpath.joinpath(dt)

    if not dtpath.exists():
        dtpath.mkdir(parents=True)

    logger.info(f'Writing files to {dtpath}')

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    b = webdriver.Chrome(options=options)

    b.get('https://tmweb.troopmaster.com/mysite/Troop506')
    login(b)


    exp = download_export(b)

    fp = dtpath.joinpath('ledger.txt')
    with fp.open('wb') as f:
        f.write(exp)

    logger.info(f'Wrote {len(exp)} to {fp}')

    a_rep = download_adult_report(b)
    fp = dtpath.joinpath('adults.csv')
    with fp.open('wb') as f:
        f.write(a_rep)

    logger.info(f'Wrote {len(exp)} to {fp}')

    s_rep = download_scout_report(b)
    fp = dtpath.joinpath('scouts.csv')
    with fp.open('wb') as f:
        f.write(s_rep)

    logger.info(f'Wrote {len(exp)} to {fp}')

    b.quit()


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
