#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 11:03:26 2020

@author: nico
"""

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException, NoSuchWindowException
from random import randint, uniform
from time import time, sleep

OPTIONS_DIR = "instaBOT_options.json"

DEFAULT_IMPLICIT_WAIT = 10

class Element:
    def __init__(self, driver, tag, logger, locator="XPATH"):
        self.driver = driver
        self.tag = tag
        self.logger = logger
        self.locator = locator.upper()
    
    def click(self, times=1):
        try:
            if self.wait_for(3):
                x = self.get()
                if times == 1:
                    x.click()
                else:
                    for _ in range(0,times):
                        x.click()
            else: 
                self.find().click()
            return True
        except:
            self.log(f"Could not click on element with xpath {self.tag}")
            return False
    
    def read(self):
        return self.find().text
    
    def readValue(self):
        return self.find().get_attribute("value")
    
    def upload_image(self, path):
        self.find().send_keys(path)
    
    def m_send_keys(self, keys):
        self.find().clear()
        self.find().send_keys(f"{keys}")
    
    def type_slow(self, message, delete=True):
        """Type the given message"""
        
        try:
            self.wait_for()
            element = self.get()
            if delete:
                for _ in range(0, 35):
                    element.send_keys(Keys.BACKSPACE);
                        
            for s in message:
                element.send_keys(s)
                sleep(uniform(0.1, 0.3))
            
            return True
        
        except Exception as e:
            self.error(f'Exception when __typeSlow__ : {e}')
            # print(f'Exception when __typeSlow__ : {e}')
            return False
    
    def get(self):
        
        element_tag = self.tag
        locator = self.locator
        
        """Wait for element and then return when it is available"""
        try:
            locator = locator.upper()
            dr = self.driver
            if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_id(element_tag))
            elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_name(element_tag))
            elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_xpath(element_tag))
            elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTOR, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_css_selector(element_tag))
            else:
                pass
                # self.log(f"Error: Incorrect locator = {locator}")
        except Exception as e:
            self.error(e)
        self.log(f"Element not found with {locator} : {element_tag}")
        return None
    
    def find(self):
        element_tag = self.tag
        locator = self.locator
        
        try:
            locator = locator.upper()
            if locator == 'ID':
                return self.driver.find_element_by_id(element_tag)
            elif locator == 'NAME':
                return self.driver.find_element_by_name(element_tag)
            elif locator == 'XPATH':
                return self.driver.find_element_by_xpath(element_tag)
            elif locator == 'CSS':
                return self.driver.find_element_by_css(element_tag)
            else:
                self.error(f"Error: Incorrect locator = {locator}")
        except Exception as e:
            self.error(e)
        self.log(f"Element not found with {locator} : {element_tag}")
        return None
        
        return self.driver.find_element_by_xpath(self.tag)
    
    def wait_for(self, timeout=10):
        """Wait till element present. Max 30 seconds"""
        
        element_tag = self.tag
        locator = self.locator
        
        result = False
        self.driver.implicitly_wait(0)
        locator = locator.upper()
        for i in range(timeout):
            initTime = time()
            try:
                if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                    result = True
                    break
                elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                    result = True
                    break
                elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                    result = True
                    break
                elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTORS, element_tag):
                    result = True
                    break
            except WebDriverException as e:
                if "chrome not reachable" in e:
                    pass
                else:
                    self.error(e)
            except NoSuchWindowException:
                pass
            except Exception as e:
                self.error(f"Exception when __wait_for_element__ : {e}")
            try:
                sleep(1 - (time() - initTime))
            except:
                sleep(0.2)
        else:
            self.error(f"Timed out. Element not found with {locator} : {element_tag}")
        self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
        return result
    
    def is_element_present(self, how, what):
        """Check if an element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True
    
    def __random_sleep__(self, minimum=10, maximum=20, cout=False):
        t = randint(minimum, maximum)
        m = int(t/60)
        s = int(t%60)
        
        if cout:
            print(f"Waiting {m}.{s} minutes")
        
        # self.log(f'Wait {t} seconds')
        self.utils.sleep(t)

    # ************************************************************************
    # LOGGER *****************************************************************
    
    def log(self, message):
        self.logger.info(f"[BotSupport] {message}")
    
    def error(self, message):
        self.logger.error(f"[BotSupport] {message}")
        
class Bot:
    
    @property
    def proxy(self):
        try:
            return self._proxy.replace("http://", "")
        except:
            return self._proxy
    
    def toJSON(self):
        return {
                "username": self.username,
                "password": self.password,
                "proxy": self.proxy,
                "message": self.message,
                "should_run": self.should_run,
            }
    
    def __init__(self, username="", password="", proxy="", message="", should_run=True):
        self.username = username
        self.password = password
        self._proxy = proxy
        self.message = message
        self.should_run = should_run

class Options:
    
    def __init__(self, WD, utils):
        self.utils = utils
        self.parser = self.utils.parser
        
        self.host = ""
        self.message = ""
        self.target = ""
        self.accounts = list()
        self.avoid = list()
        self.run_count = 100
        self.inter_run_delay = 2*60
        self.inter_user_delay = 10
        self.user_per_run_count = 12
        self.debug = True
        self.show_images = False
    
    @property
    def n_users(self):
        return self.run_count*self.user_per_run_count*len(self.accounts)
    
    def _update(self):
        options = {
                "avoid": self.avoid,
                "message": self.message,
                "target": self.target,
                "host": self.host,
                "accounts": [account.toJSON() for account in self.accounts],
                "run_count": self.run_count,
                "inter_run_delay": self.inter_run_delay,
                "user_per_run_count": self.user_per_run_count,
                "inter_user_delay": self.inter_user_delay,
                "debug": self.debug,
                "show_images": self.show_images,
            }
                
        self._options = options
        return options
    
    def load(self):
        options = self.parser.decodeJSON(OPTIONS_DIR)
        
        try:
            self.message = options["message"]
            self.target = options["target"]
            
            for account in options["accounts"]:
                
                message = ""
                should_run = True
                
                try:
                    message = account["message"]
                except:
                    pass
                    
                try:
                    should_run = account["should_run"]
                except:
                    pass
                
                self.accounts.append(Bot(account["username"], account["password"], account["proxy"], message, should_run))
            
            self.debug = options["debug"]
            self.show_images = options["show_images"]
            self.host = options["host"]
            self.avoid = options["avoid"]
            self.run_count = options["run_count"]
            self.inter_run_delay = options["inter_run_delay"]
            self.inter_user_delay = options["inter_user_delay"]
            self.user_per_run_count = options["user_per_run_count"]
        except:
            pass
        
        return options
        
    def save(self):
        self._update()
        self.parser.encodeJSON(OPTIONS_DIR, self._options)