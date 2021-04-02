#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 14:37:02 2020

@author: nico
"""

from requests import get
from logging import getLogger, FileHandler, Formatter, DEBUG
from os import makedirs
from JSONParser import FileManager
# from TerminalHandler import TerminalHandler
from os.path import exists
from platform import platform
from time import sleep
from users_scraper import Loader
from processes_handler import ProcessesHandler
from numpy.random import randint, seed

TARGET_ACCOUNTS_DIR = "target.txt"

class Utils:
    
    @property
    def os(self):
        sy = platform().lower()
        self.log(f"OS: {sy}")
        if "windows" in sy:
            return (True, "windows")
        elif "macos" in sy:
            return (True, "macos")
        else:
            self.error("Machine is not running MacOS or Windows")
            return (False, sy)
    
    def __init__(self, WD, logger_name):
        
        seed()
        
        if not exists(WD):
            makedirs(WD)
        if not exists(WD + "/images"):
            makedirs(WD + "/images")
        
        self.WD = WD
        self.logger = self._get_logger(logger_name)
        self.parser = FileManager(WD, self)
        self.phandler = ProcessesHandler(self)
    
    def random_num(self, mn, mx):
        return randint(mn, mx)
    
    def _get_logger(self, name): 

        logger = getLogger(name)
        hdlr = FileHandler(self.WD + "/instaBOT_logs" + ".log")
        formatter = Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(DEBUG)
        
        logger.info("\n\n\nLogger initiated")
        self.logger = logger
        return logger
        
    def raise_exception(self, exception):
        self.error(exception)
        raise ValueError(exception)
    
    def log(self, message):
        self.logger.info(message)
        
    def error(self, message):
        self.logger.error(message)
    
    def sleep(self, n):
        try:
            sleep(n)
        except KeyboardInterrupt:
            self.error("Could not sleep. Keyboardinterrupt")
        except:
            self.error(f"Could not sleep: {n} may not be a number")
            sleep(n)
            
    def has_permission(self):
        try:
            permission_ob = get("http://nicolopadovan.altervista.org/BOT/instaBOT_permissions.json")
            result = permission_ob.json()
            
            sy = self.os
            if sy[0] == True:
                return result[f"should_run_{sy[1]}"]
            else:
                return result["should_run"]
        except Exception as e:
            self.error(f"Couldn't load permissions: {e}")
            return False
        
    def scrape(self, options):
        self.loader = Loader(self, options, options.accounts[0].proxy)
        
        try:
            res = self.loader.scrape(options.accounts[0].username, options.accounts[0].password, options.n_users)
            return res[1]
        except Exception as e:
            self.error(f"Could not scrape users. Error: {e}")
            return list()