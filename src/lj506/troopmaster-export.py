
import time
import pickle
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests

from selenium.webdriver.chrome.options import Options

class TMFailure(Exception):
    ...

def select_site(b):
    """Select the Troops website. Note necessary if the mysite/Troop506 address is given """

    try:
        drop = Select(b.find_element_by_id('States'))
        drop.select_by_value("CA")
        time.sleep(3)
        drop = Select(b.find_element_by_id('UnitNums'))
        drop.select_by_value("506")
        time.sleep(2)
    except NoSuchElementException as e:
        pass

def login(b):

    try:
        b.find_element_by_id("userid").send_keys("eric.busboom")
        b.find_element_by_id("password").send_keys("62fIJg25")
        b.find_element_by_class_name('btn-primary').click()
    except NoSuchElementException as e:
        pass

def download_adult_report(b):

    # These might be required to get the right cookies, but
    # it does seem to work without it, at least occassionally.
    #WebDriverWait(b, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Reports"))).click()
    #WebDriverWait(b, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Custom Reports"))).click()
    #WebDriverWait(b, 10).until(EC.presence_of_element_located((By.XPATH,"(//a[contains(text(),'Adults')])[4]"))).click()

    s = requests.Session()
    s.cookies.update({c['name']: c['value'] for c in b.get_cookies()})

    d = '{"title":"Auto Adult List","memberFilter":"All Adults","includeRemarks":false,"includeMedications":false,"includeAllergies":false,"doubleSpace":false,"list11":"Name","list12":"Cell Phone","list13":"Email","list14":"BSA ID#","list15":"Leadership Position","list16":"Became Leader","list21":"","list22":"","list23":"","list24":"","list25":"","list26":"","list31":"","list32":"","list33":"","list34":"","list35":"","list36":""}'

    h = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
        "Content-Type": "application/json",
    }

    r = s.post('https://tmweb.troopmaster.com/Reports/RepCustomAdults',data=d, headers=h)
    r.raise_for_status()

    c = r.json()
    if not c.get('success'):
        raise TMFailure(str(c))

    r = s.get("https://tmweb.troopmaster.com/Reports/DownloadExport?fileName=CustomExport.CSV")
    r.raise_for_status()

    return r.content


def download_export(b):
    """Get the TroopLedge export"""

    s = requests.Session()
    s.cookies.update({c['name']: c['value'] for c in b.get_cookies()})

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

    return r.content

b = webdriver.Chrome()
b.get('https://tmweb.troopmaster.com/mysite/Troop506')
login(b)

download_adult_report(b)
#with open('AdultsReport.csv', 'wb') as f:
#    c = r.content
#    f.write(c)
#    print(len(c))