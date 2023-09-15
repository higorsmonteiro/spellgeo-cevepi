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


class ZipCollector:
    def __init__(self):
        self.url = 'https://listacep.com/'
        self.driver = None

        self.valid_ufs = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 
                          'df', 'es', 'go', 'ma', 'mt', 'ms', 
                          'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 
                          'rj', 'rn', 'rs', 'ro', 'rr', 'sc', 
                          'sp', 'to']

    def open_browser(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    def close_browser(self):
        self.driver.close()
        self.driver = None

    def get_cities(self, uf):
        '''
            Get the name of all cities within a given state provided by the argument 'uf'.
            Valid UF string should be a two-character string pointing to a given Brazilian
            state. For instance, 'ce' refers to the state of Ceará. 

            Args:
            -----
                uf:
                    String. Two-character string referring to a Brazilian state.

            Return:
                city_lst:
                    List of String. Lowercase names of the cities from 'uf' provided.
        '''
        uf = uf.lower()
        if uf in self.valid_ufs:
            self.driver.get(self.url)
        else:
            raise Exception("UF string parsed is not valid.")

        # -- Click on the UF state buttom.
        uf_buttom = WebDriverWait(self.driver, 20.0).until(EC.presence_of_element_located((By.XPATH, '//a[@href="'+f'{self.url+uf}'+'"]')))
        try:
            self.driver.execute_script('arguments[0].click()', uf_buttom)
        except Exception as err:
            self.driver.close()
            raise err

        # -- Find the list of municipalities 
        element = WebDriverWait(self.driver, 20.0).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'list__list')))[0]
        cities_html = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
        cities_lst = [ (li.get_text().lower(), li.find('a').attrs['href']) for li in cities_html.find_all('li') ]
        return cities_lst
    
    def get_bairros(self, city_href):
        '''
            Get the name of all neighborhoods within a given city. Valid UF string should be 
            a two-character string referring to a given Brazilian state, while city name should be 
            decoded to not include special characters.

            Args:
            -----
                uf:
                    String. Two-character string referring to a Brazilian state.
                city:
                    String. ...

            Return:
                city_lst:
                    List of String. Lowercase names of the cities from 'uf' provided.
        '''
        self.driver.get(city_href)
        # -- Find the list of municipalities 
        elements = WebDriverWait(self.driver, 20.0).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'list__list')))
        if len(elements)==1:
            bairros_info = []
        else:
            bairros_html = BeautifulSoup(elements[0].get_attribute('outerHTML'), 'html.parser')
            bairros_info = [ (li.get_text().lower(), li.find('a').attrs['href']) for li in bairros_html.find_all('li') ]
        return bairros_info
    
    def get_zips(self, bairro_href):
        '''
        
        '''
        self.driver.get(bairro_href)
        zip_elements = WebDriverWait(self.driver, 20.0).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'list__list')))
        if len(zip_elements)==1:
            zip_lst = []
        else:
            zip_html = BeautifulSoup(zip_elements[0].get_attribute('outerHTML'), 'html.parser')
            zip_lst = [ (li.get_text().lower().replace("\n", "")[:8], li.get_text().lower().replace("\n", "")[8:]) for li in zip_html.find_all('li') ]
        return zip_lst
    
    def extract_all_city(self, city_href):
        '''
        
        '''
        bairros = self.get_bairros(city_href)

        zips_info = []
        for bairro_name, bairro_href in bairros:
            cur_zips = self.get_zips(bairro_href)
            zips_info += [ (bairro_name, cur_zip[0], cur_zip[1]) for cur_zip in cur_zips ]
        return zips_info



