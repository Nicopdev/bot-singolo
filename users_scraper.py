#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 21:47:06 2020

@author: nico
"""

from instaloader import Profile, Instaloader#, RateController
from instaloader import save_structure_to_file
from instaloader import load_structure_from_file

WD = "BOT_WD/scraper_wd/"
SESSION_DIR = "session"
DONE_ACCOUNTS_DIR = "done.txt"
ITERATOR_DIR = "iterator.json"
TARGET_ACCOUNTS_DIR = "target.txt"

class Loader:
    
    def __init__(self, utils, options, proxy):
        self.utils = utils
        self.options = options
        self.logged = False
        self.account = Instaloader(proxy=f"{proxy}")

    def login(self, username, password):
        
        self.username = username
        self.password = password
        self.utils.log(f"Now logging into {self.username}")
        
        if not self.logged:
            try:
                self.account.load_session_from_file(self.username, WD + f"{self.username}_" + SESSION_DIR)
                self.logged = True
                self.utils.log("Successfully logged in")
            except:
                try:
                    self.account.login(self.username, self.password)
                    self.logged = True
                    try:
                        self.account.save_session_to_file(WD + f"{self.username}_" + SESSION_DIR)
                    except:
                        pass # Couldn't save session. NO WORRIES
                except Exception as e:
                    self.utils.error(f"Could not login: {e}")
                    print(f"Could not login into scraper with error: {e}")
    
    def save_remaining(self, username, remaining_users):
        if len(remaining_users) > 0:
            self.utils.parser.append_from_array(f"{username}_" + TARGET_ACCOUNTS_DIR)
    
    # Returns False if failed
    def scrape(self, username, password, n):
        
        users = list()
        for i in range(0,500):
            if not self.utils.parser.exists(f"stored_users_{i}.txt"):
                break
            else:
                u = self.utils.parser.decode_to_array(f"stored_users_{i}.txt")
                # print(f"{i} contained {len(u)} users")
                users.extend(u)
        
        old = self.utils.parser.decode_to_array(TARGET_ACCOUNTS_DIR)                                                
        users.extend(old)
        
        users = self.filter_done(users)[1]
        
        n = n - len(users)
        
        if n < 1:
            return (len(users), users)
        
        self.login(username, password)
        
        if not self.logged:
            return (0, [])
        
        try:
            profile = Profile.from_username(self.account.context, self.options.target)
        except Exception as e:
            self.utils.error(f"Could not find the target user: {e}")
            print(f"Could not find the target user {self.options.target} with error: {e}")
            return (0, [])  
      
        self.utils.log(f"Now scraping {self.options.target} from {self.username}. Want to load {n} users and only have {self.filter_done(users)}")
        
        try:
            iterator = profile.get_followers()
            iterator.thaw(load_structure_from_file(self.account.context), ITERATOR_DIR)
        except:
            iterator = profile.get_followers()
        
        try:
            for jx, follower in enumerate(iterator):
                users.append(follower.username)
                
                if jx%500 == 0 and jx != 0:
                    fn = self.filter_done(users)
                    
                    if fn[0] > n:
                        self.utils.log("Exiting...")
                        save_structure_to_file(iterator.freeze(), ITERATOR_DIR)
                        return fn
        except KeyboardInterrupt:
            self.filter_done(users)
            save_structure_to_file(iterator.freeze(), ITERATOR_DIR)
        except Exception as e:
            fn = self.filter_done(users)
            save_structure_to_file(iterator.freeze(), ITERATOR_DIR)
            self.utils.error(f"Error while scraping: {e}")
            return fn
        self.utils.parser.delete(ITERATOR_DIR, WD=False)
        print("Target finished. Please change target FOR THE NEXT SESSION (this session should be OK!)")
        return self.filter_done(users)
        
    def filter_done(self, users):
        done = self.utils.parser.decode_to_array(DONE_ACCOUNTS_DIR)
        
        result = [user for user in users if user not in done]
        self.utils.parser.encode_from_array(TARGET_ACCOUNTS_DIR, result)
        self.utils.log(f"Users: {len(result)}")
        return (len(result), result)
        
        
        
        
        
        
        
        
        