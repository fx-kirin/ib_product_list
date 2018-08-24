#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 zenbook <zenbook@zenbook-XPS>
#
# Distributed under terms of the MIT license.

"""

"""
import requests
import fire
import time
import re
import os,sys
import csv
import logging
from mkdir_p import mkdir_p
from bs4 import BeautifulSoup

SLEEP_TIME = 0.5

def main(company_id, root_path=None):
    session = requests.Session()
    
    adapters = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("http://", adapters)
    session.mount("https://", adapters)
    result = session.get('https://www.interactivebrokers.com/en/index.php?f=2222&exch=%s'%(company_id))
    soup = BeautifulSoup(result.content, 'lxml')
    categories = [a.get('id') for a in soup.find(class_='btn-selectors').find_all('a')]
    
    time.sleep(SLEEP_TIME)
    for category in categories:
        result = session.get('https://www.interactivebrokers.com/en/index.php?f=2222&exch=%s&showcategories=%s'%(company_id, category))
        mkdir_p('./result/%s/'%(company_id))
        if root_path:
            output_path = '%s/result/%s/%s.csv'%(root_path, company_id, category)
        else:
            output_path = './result/%s/%s.csv'%(company_id, category)
        f = open(output_path, 'w')
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        
        time.sleep(SLEEP_TIME)
        soup = BeautifulSoup(result.content, 'lxml')
        
        table = soup.find_all('table')[2]
        thead = table.find('thead')
        ths = thead.find_all('th')
        columns = [re.sub(' \n.*$', '', th.getText()) for th in ths]
        writer.writerow(columns)
        
        if soup.find(class_='pagination'):
            page_size = int(soup.find(class_='pagination').find_all('a')[-2].getText())
            for i in range(page_size):
                logging.info('getting %s %s %s/%s'%(company_id, category, i+1, page_size))
                result = session.get('https://www.interactivebrokers.com/en/index.php?f=2222&exch=%s&showcategories=%s&page=%s'%(company_id, category, i+1))
                time.sleep(SLEEP_TIME)
                soup = BeautifulSoup(result.content, 'lxml')
                table = soup.find_all('table')[2]
                tbody = table.find('tbody')
                trs = tbody.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')
                    row = [td.getText() for td in tds]
                    writer.writerow(row)
        else:
            logging.info('getting %s %s %s/%s'%(company_id, category, 1, 1))
            table = soup.find_all('table')[2]
            tbody = table.find('tbody')
            trs = tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                row = [td.getText() for td in tds]
                writer.writerow(row)
        f.close()
    
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s|%(threadName)s|%(levelname)s : %(message)s', level=logging.INFO)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fire.Fire(main)
