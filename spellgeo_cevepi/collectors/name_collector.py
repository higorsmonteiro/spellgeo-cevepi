# -*- coding: utf-8 -*-

'''

'''
import os
import time
import numpy as np
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import select, insert, update, text
from sqlalchemy import Table, MetaData
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Sequence, ForeignKey

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CollectorCorreios:
    def __init__(self, engine, url) -> None:
        '''
        
        '''
        self.engine = engine
        self.url = url
        self.driver = None

    def connect_db(self):
        '''
        
        '''
        self.metadata = MetaData()
        self.geoname = Table('geonames', self.metadata, autoload=True, autoload_with=self.engine)
        self.geoname_log = Table('geonames_log', self.metadata, autoload=True, autoload_with=self.engine)


    def collect_names(self, query, max_page=None):
        '''
        
        '''
        # --> It seems CORREIOS only paginate up to 20 pages, so 100 bounds the navigation with certainty. 
        if max_page is None:
            max_page = 100 

        # --> Open driver
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

        # --> Search adress based on the string provided and press ENTER
        endereco_form = self.driver.find_element(By.ID, 'endereco')
        endereco_form.send_keys(query, Keys.ENTER)

        npage = 1
        while npage<=max_page:
            # --> Extract table of addresses
            try:
                tbody_block = WebDriverWait(self.driver, 20.0).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
            except:
                print("<tbody> not located")
                self.driver.close()
        
            sleep_time = np.random.uniform()*2
            time.sleep(sleep_time)
    
            # --> Extract HTML table and read structured data into list
            html_table = tbody_block.get_attribute("outerHTML")
            bs4_parser = BeautifulSoup(html_table, "html.parser")
            tb_rows = bs4_parser.find_all("tr")
    
            rows = []
            for current_row in tb_rows:
                cell_blocks = current_row.find_all("td")
                rows.append( [ cell.get_text() for cell in cell_blocks ] )
        
            # --> Structure the data
            fdata = [
                {"QUERY": query, "NUMERO_PAGINA": npage, "LOGRADOURO/NOME": n[0],
                "BAIRRO/DISTRITO": n[1], "LOCALIDADE/UF": n[2],
                "CEP": n[3]} for n in rows
            ]

            msg = f"Page {npage}: {len(rows)} extracted\nLast row extracted: {fdata[-1]}"
            fdata_log = [
                {"QUERY": query, "MENSAGEM": msg }
            ]
    
            # --> Insert data in DUCKDB database
            ins = self.geoname.insert()
            with self.engine.connect() as conn:
                rp = conn.execute(ins, fdata)
                conn.commit()

            # --> Insert log data in DUCKDB database
            ins_log = self.geoname_log.insert()
            with self.engine.connect() as conn:
                rp = conn.execute(ins_log, fdata_log)
                conn.commit()
        
            # --> Find next button
            botao_proximo = WebDriverWait(self.driver, 20.0).until(EC.presence_of_element_located((By.XPATH, '//a[@href="javascript:pesquisarProximo()"]')))
            try:
                botao_proximo.click()
                npage+=1
            except:
                print("Next buttom not iteractable - End of search")
                self.driver.close()
                break

    def close_driver(self):
        '''
            If closing is needed manually.
        '''
        self.driver.close()



