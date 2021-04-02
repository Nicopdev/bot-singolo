#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 14:46:01 2020

@author: nico
"""

from threading import Thread, Event
from bot import InstaDM
# from sys import exit
# from os import listdir

TARGET_ACCOUNTS_DIR = "instaBOT_target_accounts.txt"
DONE_USERS_DIR = "done_users.txt"

class ProcessesHandler:
    
    def __init__(self, utils):
        
        self.utils = utils
        self.processes = list()
        self.routines = list()
        self.routines_instas = list()
        self.instas = list()
        self.options = {}
        
    def new_base(self, func, daemon=False, *args):
        p = Thread(target=func, args=args)
        p.daemon = daemon
        p.start()
        return p

    def new_routine(self, index, options):
        p = Thread(target=self._new_routine, args=[index, options])
        p.daemon = True
        p.start()
        self.routines.append(p)
        self.utils.sleep(2.5)
    
    def _new_routine(self, index, options):
        
        username = options.accounts[index].username
        password = options.accounts[index].password
        proxy = options.accounts[index].proxy
        
        insta = InstaDM(self.utils, username, password, proxy_string=proxy, headless=(not options.debug), generate_driver=True, show_images=options.show_images, mobile=False)
        
        if insta.login() == False:
            self.utils.error(f"{username} routine couldn't login")
            return
        
        insta.like_comment()
    
    def new_nm(self, index, options):
        
        self.options = options
        users = self.utils.parser.decode_to_array(TARGET_ACCOUNTS_DIR)
        
        if len(users) < options.run_count*options.user_per_run_count:
            self.utils.error(f"{options.accounts[0].username}: not enough users ({len(users)} instead of {options.run_count*options.user_per_run_count})")
            return False
        
        self.utils.parser.encode_from_array(TARGET_ACCOUNTS_DIR, users[options.user_per_run_count*options.run_count:])
        users = users[:options.user_per_run_count*options.run_count]
        
        p = Thread(target=self._actual_start_nm, args=[index, options, users])
        p.daemon = True
        
        self.utils.log("New process started")
        p.start()
        self.processes.append(p)
        return True
    
    def _actual_start_nm(self, index, options, users):
        self.utils.log("Bot started")
        
        username = options.accounts[index].username
        password = options.accounts[index].password
        proxy = options.accounts[index].proxy
        message = options.accounts[index].message
        
        if message == "":
            message = options.message
                
        insta = InstaDM(self.utils, username, password, proxy_string=proxy, headless=(not options.debug), generate_driver=True, show_images=options.show_images)
        self.instas.append(insta)
        try:
            if insta.login() == False:
                self.utils.log(f"{username} will now stop")
                self.parser.append_from_array(f"{username}_" + TARGET_ACCOUNTS_DIR, users)
                self.utils.error("Could not login")
                self.stop_at(index)
                return
        except Exception as e:
            self.utils.error(f"Could not login: {e}")
            self.stop_at(index)
            return
        
        if not options.show_images:
            self.utils.log("Now spamming...")
            insta.sharePost(username, users, message, options, index, TARGET_ACCOUNTS_DIR, DONE_USERS_DIR)
    
    def start(self):
        self.run_event = Event()
        self.run_event.set()
    
    def new(self, index, options, only_proxy=False):
        
        p = Thread(target=self._actual_start_, args=[index, options, self.run_event, only_proxy])
        p.daemon = True
        
        self.utils.log("New process started")
        p.start()
        self.processes.append(p)
        return True
    
    def stop_all(self, ex=False):
        self.run_event.clear()
        
        for process in self.processes:
            process.join()
        self.utils.log(f"Will try to stop all the bots, {len(self.instas)}")
        try:
            for i, thread in enumerate(self.processes):
                try:
                    self.utils.log(f"Stopping {self.instas[i].username}")
                    # self.instas[i].should_run = False
                except IndexError as e:
                    self.utils.log(f"IndexError: {e}")
                    break
                except Exception as e:
                    self.utils.log(f"An error occurred: {e}")
            
            for thread in self.processes:
                thread.join()
            self.processes = list()
            self.utils.log("All threads have been killed")
        except Exception as e:
            self.utils.error(f"Error while stopping the bots: {e}")
    
    def stop_at(self, index):
        self.utils.log(f"Will try to stop bot at {index}")
        try:
            self.utils.log("Trying to stop...")
            try:
                self.instas[index].should_run = False
            except IndexError:
                pass
        except Exception as e:
            self.utils.error(f"Error while stopping the bots: {e}")
    
    def _actual_start_(self, index, options, run_event, only_proxy=False):
        self.utils.log("Bot started")
        
        username = options.accounts[index].username
        password = options.accounts[index].password
        proxy = options.accounts[index].proxy
        message = options.accounts[index].message
        
        if message == "":
            message = options.message
        
        insta = InstaDM(self.utils, username, password, proxy_string=proxy, headless=(not options.debug), generate_driver=True, show_images=options.show_images)
        self.instas.append(insta)
        
        if only_proxy:
            insta.proxies_only()
        
        try:
            if insta.login() == False:
                self.utils.error("Could not login")
                self.stop_at(index)
                return
        except Exception as e:
            self.utils.error(f"Could not login: {e}")
            self.stop_at(index)
            return
        
        if not options.show_images:
            self.utils.log("Now spamming...")
            insta.sendMultipleMessages(username, message, options, index, TARGET_ACCOUNTS_DIR, DONE_USERS_DIR, run_event)
    
    @property
    def get_active(self):
        return len(self.processes)
