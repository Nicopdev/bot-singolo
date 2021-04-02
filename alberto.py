#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 17:01:05 2021

@author: nico
"""

import argparse
from botSupport import Options, Bot
from utils import Utils
from bot import InstaDM
# DIRECTORIES

DONE_DIR = "done.txt"
TARGET_DIR = "target.txt"
WD = "BOT_WD"

class BOT(object):
    def __init__(self, headless=False):
    
        parser = argparse.ArgumentParser(description="usenrame")
        parser.add_argument('--username')
        parser.add_argument("--password")
        parser.add_argument("--target")
        
        parser.add_argument("--count")
        parser.add_argument("--users_delay")
        parser.add_argument("--user_per_run_count")
        parser.add_argument("--run_delay")
        
        args = parser.parse_args()
        
        self.username = args.username
        self.password = args.password
        
        print(self.password)
        
        self.utils = Utils(WD, "instaBOT_logs")
        
        show_images = False
        debug = True
        insta = InstaDM(self.utils, self.username, self.password, headless= not debug, generate_driver=True, show_images=False)
        
        options = Options(WD=WD, utils=self.utils)
        
        options.accounts = [Bot(username=self.username, password=self.password)]
        options.message = "Ciao, questo è un test"
        options.target = args.target
        options.avoid = [""]
        options.run_count = 1
        
        options.inter_run_delay = int(args.run_delay)
        options.user_per_run_count = int(args.user_per_run_count)
        options.inter_user_delay = int(args.users_delay)
        options.run_count = int(int(args.count) / int(args.user_per_run_count))
        options.debug = debug
        options.show_images = show_images
        
        self.options = options
        if self.scrape():
            insta.login()
            insta.sendMultipleMessages(self.username, options.message, options, 0, TARGET_DIR, DONE_DIR)
        
    def scrape(self):

        users = self.utils.scrape(self.options)
        n = len(users)
        self.utils.parser.encode_from_array(TARGET_DIR, users)
        print(n)
        print(n >= self.options.run_count*self.options.user_per_run_count*len(self.options.accounts))
        
        return n >= self.options.run_count*self.options.user_per_run_count*len(self.options.accounts)
        
if __name__ == "__main__":
    bot = BOT()