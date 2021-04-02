#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 17:25:38 2020
@author: nico
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.common.keys import Keys
from sqlite3 import connect
from botSupport import Element
import pyautogui as pgui
from os import system
from getpass import getuser
from selenium.webdriver import ActionChains

DEFAULT_IMPLICIT_WAIT = 30

class InstaDM(object):

    def __init__(self, utils, username, password, headless=True, proxy_string="", instapy_workspace=None, profileDir=None, generate_driver=False, show_images=False, mobile=True):
        
        self.username = username
        self.password = password
        self.proxy = proxy_string
        
        self.should_run = True
        self.utils = utils
        self.parser = self.utils.parser
        self.show_images = show_images
        
        if generate_driver:
            self.generate_driver(headless=headless, proxy_string=proxy_string, instapy_workspace=instapy_workspace, profileDir=profileDir, show_images=show_images, mobile=mobile)
        
        # Instapy init DB
        self.instapy_workspace = instapy_workspace
        self.conn = None
        self.cursor = None
        if self.instapy_workspace is not None:
            self.conn = connect(self.instapy_workspace + "InstaPy/db/instapy.db")
            self.cursor = self.conn.cursor()

            cursor = self.conn.execute("""
                SELECT count(*)
                FROM sqlite_master
                WHERE type='table'
                AND name='message';
            """)
            count = cursor.fetchone()[0]

            if count == 0:
                self.conn.execute("""
                    CREATE TABLE "message" (
                        "username"    TEXT NOT NULL UNIQUE,
                        "message"    TEXT DEFAULT NULL,
                        "sent_message_at"    TIMESTAMP
                    );
                """)

    def update_selectors(self):
        logger = self.utils.logger
        
        self.selectors = {
           "accept_cookies": Element(self.driver, "//button[text()='Accept']", logger),
           "home_to_login_button": Element(self.driver, "//button[text()='Log In']", logger),
           "username_field": Element(self.driver, "username", logger, "NAME"),
           "password_field": Element(self.driver, "password", logger, "NAME"),
           "button_login": Element(self.driver, "//button/*[text()='Log In']", logger),
           "login_check": Element(self.driver, "//*[@aria-label='Home'] | //button[text()='Save Info'] | //button[text()='Not Now']", logger),
           "search_user": Element(self.driver, '//*[@id="react-root"]/section/div[2]/div/div[1]/div/div[2]/input', logger),
           "select_user": Element(self.driver, "//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar']", logger),
           "name": Element(self.driver, "((//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar'])[1]//..//..//..//div[2]/div[2]/div)[1]", logger),
           "next_button": Element(self.driver, "//button/*[text()='Next']", logger),
           "textarea": Element(self.driver, "/html/body/div[1]/section/div[2]/div/div/div[2]/div/div/div/textarea", logger),
           "send": Element(self.driver, "/html/body/div[1]/section/div[2]/div/div/div[2]/div/div/div[2]/button", logger),
           "upload_image": Element(self.driver, "//*[@id='react-root']/section/div[2]/div/div/div[2]/div/div/form/input", logger),
           "email_field": Element(self.driver, "//*[@id='react-root']/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input", logger),
           "full_name_field": Element(self.driver, "//*[@id='react-root']/section/main/div/article/div/div[1]/div/form/div[4]/div/label/input", logger),
           "back_to_dm": Element(self.driver, '//*[@id="react-root"]/section/div[1]/header/div/div[1]/a', logger),
                                   
           "error_check": Element(self.driver, '/html/body/div[2]/div/div/div/div[3]/button[2]', logger),
           "error_check2": Element(self.driver, '/html/body/div[4]/div/div/div/div[3]/button[2]', logger),
           "error_check3": Element(self.driver, '/html/body/div[3]/div/div[2]/div/div[5]/button', logger),
           
           #Routine
           "first_thumbnail": Element(self.driver, '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div', logger),
           "follow_button": Element(self.driver, '/html/body/div[5]/div[2]/div/article/header/div[2]/div[1]/div[2]/button', logger),
           "like_button": Element(self.driver, '/html/body/div[3]/div/div[2]/div/article/div[2]/section[1]/span[1]/button/span', logger),
           "save_button": Element(self.driver, 'AAAAAAAAA', logger),
           "enter_comment": Element(self.driver, '/html/body/div[3]/div/div[2]/div/article/div[2]/section[1]/span[2]/button/span', logger),
           "comment_input": Element(self.driver, '/html/body/div[3]/div/div[2]/div/article/div[2]/section[3]/div/form/textarea', logger),
           
           # New method
           "explore": Element(self.driver, '/html/body/div[1]/section/nav[2]/div/div/div[2]/div/div/div[2]', logger),
           "search_input": Element(self.driver, '//*[@id="react-root"]/section/nav[1]/div/header/div/h1/div/div/div/div[1]/label/input', logger),
           "first_res": Element(self.driver, '//*[@id="react-root"]/section/main/div/div/ul/li[1]', logger),
           "shared_post": Element(self.driver, '//*[@id="react-root"]/section/main/div/div[4]/article/div[1]/div/div[1]/div[1]/a/div[1]/div[2]', logger),
           "share_button": Element(self.driver, '//*[@id="react-root"]/section/main/div/div/article/div[3]/section[1]/button', logger),
           "username_input": Element(self.driver, '/html/body/div[4]/div/div/div/div[1]/div/div[2]/input', logger),
           "first_user_res": Element(self.driver, '/html/body/div[4]/div/div/div/div[2]/div', logger),
           "send_button": Element(self.driver, '/html/body/div[4]/div/div/header/div/div[2]/button', logger),
           
           # Account creation
           "sms_username": Element(self.driver, '//*[@id="username"]', logger),
           "sms_password": Element(self.driver, '//*[@id="password"]', logger),
           "sms_login": Element(self.driver, '//*[@id="form"]/div/button', logger),
           "sms_only_code": Element(self.driver, '/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[1]/div/ul/li[2]/div/div', logger),
           # "sms_login_check": Element(self.driver, '/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[1]/div[1]/div/div/div/div[2]/span/div[11]/button', logger),
           "sms_login_check": Element(self.driver, '/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[1]/div[1]/div/div/div/div[2]/span/div[1]/button', logger),
           "change_lang": Element(self.driver, '//*[@id="react-root"]/section/main/div[2]/div/div[2]/div[3]/div/label/div/button', logger),
           "search_lang": Element(self.driver, '/html/body/div[4]/div/div/div[2]/div[1]/label/input', logger),
           "correct_lang": Element(self.driver, '/html/body/div[4]/div/div/div[2]/div[2]/div/div/button', logger),
           "phone_input": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/form/div[3]/div/label/input', logger),
           "fullname_input": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/form/div[4]/div/label/input', logger),
           "sms_username_input": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/form/div[5]/div/label/input', logger),
           "password_input": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/form/div[6]/div/label/input', logger),
                                                
           "new_voip": Element(self.driver, '/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/ul[1]/li[1]/button', logger),
           "current_voip": Element(self.driver, '/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[1]/div[2]/h6/span[1]/span[1]', logger),
           "next_p_creation": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/form/div[7]/div/button', logger),
           "next_p_creation_2": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/div[6]/button', logger),
           "code_input": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/div/div/form/div[1]/div/label/input', logger),
           "sms_refresh": Element(self.driver, '//*[@id="operations"]/div/div[1]/h6/button', logger),
           
           "month_select": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/div[4]/div/div/span/span[1]/select', logger),
           "day_select": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/div[4]/div/div/span/span[1]/select', logger),
           "year_select": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/div[4]/div/div/span/span[1]/select', logger),
           "accept_cookies_sms": Element(self.driver, '/html/body/div[2]/div/div/div/div[2]/button[1]', logger),
           "confirm_code": Element(self.driver, '/html/body/div[1]/section/main/div/div/div[1]/div/div/div/form/div[2]/button', logger),
           "delete_voip": Element(self.driver, '/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[1]/div[3]/button', logger),
           
           "received_codes": [
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[1]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[2]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[3]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[4]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[5]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[6]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[7]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[8]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[9]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[10]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[11]/div[2]/code", logger),
                            Element(self.driver, "/html/body/div[1]/div[2]/div/div[2]/div/div[4]/div[2]/div[2]/div/div[3]/div/div[1]/div/div[2]/div[12]/div[2]/code", logger),
               ],
           
           "upload_profile_pic": Element(self.driver, "/html/body/div[1]/section/main/section/div/div[3]/div[2]/form/input", logger),
           
           "to_follow": [
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[1]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[2]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[3]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[4]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[5]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[6]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[7]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[8]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[9]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[10]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[11]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[12]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[13]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[14]/div[3]/button", logger),
               Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div/div/div/div[15]/div[3]/button", logger),
               ],
           
           "init_account": Element(self.driver, "/html/body/div[1]/section/main/section/div/div[2]/div[2]/button", logger),
           "reload_username": Element(self.driver, "//*[@id='react-root']/section/main/div/div/div[1]/div/form/div[5]/div/div/div/button", logger),
           "logout": Element(self.driver, "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[5]/div[2]/div[2]/div[2]/div[2]", logger),
           "open_profile": Element(self.driver, "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[5]/span", logger),
           "register": Element(self.driver, "/html/body/div[1]/section/main/article/div[2]/div[2]/div/p/a/span", logger),
        }

    def login(self):
        
        try:
            self.driver.get(f"http://{self.username}")
        except:
            try:
                self.driver.get("https://www.bing.com")
            except:
                self.utils.terminal.show_message(f"La proxy di {self.username} potrebbe non funzionare, controlla che il tuo IP non sia cambiato")
        
        self.driver.execute_script("window.open('', '_blank');")
        
        self.next_tab()
        
        self.driver.get('https://instagram.com/?hl=en')
        
        # Load and upload COOKIES
        cookies = self.utils.parser.pickle_load(f"{self.username}_" + "driver_session.pkl")
        if cookies != None:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
        
        if self.selectors["login_check"].wait_for(20):
                self.log("Login successful")
                return True
                
        self.__random_sleep__(3, 5)
                
        if self.selectors["accept_cookies"].wait_for(20):
            self.selectors["accept_cookies"].click()
            self.__random_sleep__(1,2)
        
        if self.selectors["home_to_login_button"].wait_for(20):
            self.selectors["home_to_login_button"].click()
            self.__random_sleep__(1,2)

        # login
        self.log(f'Login with {self.username}')
        self.__scrolldown__(400)
        
        if not self.selectors['username_field'].wait_for(20):
            self.utils.log('Login Failed: username field not visible')
            return False
        else:
            self.selectors['username_field'].m_send_keys(self.username)
            self.selectors['password_field'].m_send_keys(self.password)
            self.selectors['button_login'].click()
                        
            self.__random_sleep__()
            
            if self.selectors["login_check"].wait_for(120):
                self.log("Login successful")
                
                self.utils.parser.pickle_store(f"{self.username}_" + "driver_session.pkl", self.driver.get_cookies())
                
            else:
                if not self.show_images:
                    self.error("Login failed")
                    return False
            self.__random_sleep__()
            return True
        
    def start_routine(self, image_paths):
        self.follow_like_comment()
    
    def proxies_only(self):
        self.driver.get("https://mail.rediff.com/cgi-bin/login.cgi")
        self.driver.execute_script("window.open('', '_blank');")
        self.next_tab()
        self.login()
    
    def create_accounts(self):
        self.new_accounts = list()
        self.voips = list()
        self.driver.get('https://www.instagram.com/accounts/emailsignup/')
        self.driver.execute_script("window.open('', '_blank');")
        self.next_tab()
        self.driver.get('https://onlinesim.ru/en/auth/login?redirect=https%3A%2F%2Fonlinesim.ru%2Fv2%2Freceive%2Fsms%3F')
        
        # Load and upload COOKIES
        cookies = self.utils.parser.pickle_load("sms_generator_driver_session.pkl")
        if cookies != None:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            
        # Login in the Receive-SMS Website
        if self.selectors["sms_login_check"].wait_for(20):
            self.selectors["sms_login_check"].click()
        else:
            self.selectors["sms_username"].type_slow("Jamescurly")
            self.selectors["sms_password"].type_slow("David2003")
            self.utils.sleep(60)
            self.selectors["sms_login"].click()
            self.utils.parser.pickle_store("sms_generator_driver_session.pkl", self.driver.get_cookies())
            self.selectors["sms_login_check"].click()
        self.__scrolldown__(0, 800)
        self.selectors["sms_only_code"].click()
        
        accounts_count = 0
        current_index = 0
        current_number = ""
        
        self.codes = list()
        for i in range(0,20):
            if accounts_count % 1 == 0:
                self._change_vpn()
                
            
            if accounts_count % 2 == 0:
                current_index = 0
                if i == 0:
                    current_number = self.generate_voip(True)
                else:
                    current_number = self.generate_voip(True)
            
            success = self.full_registration(current_number, current_index, i)
            current_index += 1
            accounts_count += 1
            
            if success == "ERROR 1":
                current_number = self.generate_voip(True)
                self._change_vpn()
            
            if not success and success != "ERROR 1":
                if self.selectors["open_profile"].wait_for(5):
                    self.selectors["open_profile"].click()
                    self.selectors["logout"].click()
                    self.selectors["register"].click()
                else:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.driver.get('https://www.instagram.com/accounts/emailsignup/')
                self._change_vpn()
        
        self.utils.parser.append_from_array("new_accounts.txt", self.new_accounts)
    
    def generate_voip(self, delete_existing):
        
        self.codes = list()
        self.driver.switch_to.window(self.driver.window_handles[1])
        n = "+7 (901) 456-7891"
        self.__scrolldown__(0, 800)
        if delete_existing:
            if self.selectors["delete_voip"].wait_for(10):
                self.selectors["delete_voip"].click()
                if self.selectors["delete_voip"].wait_for(10):
                    self.selectors["delete_voip"].click()
                 
                self.selectors["sms_refresh"].click()
                self.utils.sleep(20)
                self.selectors["sms_refresh"].click()
                self.utils.sleep(5)
        
        if (not delete_existing) and self.selectors["current_voip"].wait_for(10):
            n = self.selectors["current_voip"].read()
        else:
            self.__scrolldown__(0, 0)
            self.selectors["new_voip"].click()
            self.__scrolldown__(0, 800)
            self.utils.sleep(2)
            self.selectors["sms_refresh"].click()
            if self.selectors["current_voip"].wait_for(60):
                n = self.selectors["current_voip"].read()
                
                if n in self.voips:
                    n = self.generate_voip(False)
            else:
                print("An error occurred: could not generate a VOIP")
                self.driver.quit()
                self.utils.sleep(5)
                # self.utils, "Creazione account", "", proxy_string="", headless=(not self.options.debug), generate_driver=True, show_images=True, mobile=False
                self.generate_driver(headless=False, mobile=False, show_images=self.show_images)
                self.create_accounts()
                
                # raise BaseException("Could not get any VOIP")
        
        if n not in self.voips:
            self.voips.append(n)
        
        return n
    
    def delete_cache(self):
        print("Deleting cache")
        self.driver.execute_script("window.open('');")
        self.utils.sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.utils.sleep(1)
        self.driver.get('chrome://settings/clearBrowserData') # for old chromedriver versions use cleardriverData
        self.utils.sleep(1)
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3) # send right combination
        actions.perform()
        self.utils.sleep(1)
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER) # confirm
        actions.perform()
        self.utils.sleep(15)
        self.driver.close() # close this tab
        self.driver.switch_to.window(self.driver.window_handles[0]) # switch back
                
    def typeMessage(self, user, message):
        # Go to page and type message
        self.getDMPage(user)
        
        if self.selectors["textarea"].wait_for():
            self.selectors["textarea"].m_send_keys(message)
            self.__random_sleep__(0.2,1)
        
        if self.selectors["send"].wait_for():
            self.selectors["send"].click()
            self.log("Message sent successfully")
            self.__random_sleep__(1,3)
    
    def getDMPage(self, user):
        if self.selectors["next_button"].wait_for():
            self.selectors["next_button"].click()
            self.__random_sleep__(1,2)
    
    def sharePost(self, username, users, message, options, index, file, done_file):
        self.index = index
        # self.driver.get("https://www.instagram.com/?hl=en")
        
        if self.selectors["error_check2"].wait_for(5):
            self.selectors["error_check2"].click()
            self.__random_sleep__(3,5)
        
        self.selectors["explore"].click()
        self.selectors["search_input"].type_slow("kimkardashian")
        self.__random_sleep__(3,5)
        self.selectors["first_res"].click()
        self.selectors["shared_post"].click()
        self.selectors["share_button"].click()
        
        for run in range(0, options.run_count):
            for index in range(0, options.user_per_run_count):
                
                if users[index] != "" and users[index] != " ":
                    try:
                        self.selectors["username_input"].type_slow(users[index])
                        self.__random_sleep__(1,2)
                        self.selectors["first_user_res"].click()
                        self.parser.encode_value(done_file, users[index])
                    except:
                        print("ERROR!")
                        self.parser.encode_value(done_file, users[index])

            self.selectors["send_button"].click()
            del users[0:options.user_per_run_count]
            self.__random_sleep__(options.inter_run_delay, options.inter_run_delay*1.5)
        
    def sendMultipleMessages(self, username, message, options, index, file, done_file):
        
        self.index = index
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        
        try:
            for _ in range(0, options.run_count):
                users = self.utils.parser.decode_to_array("target.txt")
                self.utils.parser.encode_from_array("target.txt", users[options.user_per_run_count:])
                users = users[:options.user_per_run_count]
                
                for inx in range(0, options.user_per_run_count):
                    
                    self.__random_sleep__(options.inter_user_delay, options.inter_user_delay*1.5)
                    if users[inx] != "" and users[inx] != " ":
                        if self.sendMessage(users[inx], message):
                            self.parser.encode_value(done_file, users[inx])
                    else:
                        print("USER WAS NULL. SKIPPING.")
                self.__random_sleep__(options.inter_run_delay, options.inter_run_delay*1.5)
        except KeyboardInterrupt as e:
            self.utils.error(f"[{self.username}] - Interrupted by user: {e}")
        except Exception as e:
            self.utils.error(f"[{self.username}] - An error occurred: {e}")
            
    def sendMessage(self, user, message):
        self.log(f'Sending message to {user}')

        try:
            result = self.selectors['search_user'].type_slow(f"{user}")
            if result == False:
                print("RESULT IS FALSE")
                if self.selectors["error_check"].wait_for(10):
                    self.selectors["error_check"].click()
                if self.selectors["error_check2"].wait_for(10):
                    self.selectors["error_check2"].click()
                if self.selectors["error_check3"].wait_for(10):
                    self.selectors["error_check3"].click()
                self.driver.get('https://www.instagram.com/direct/new/?hl=en')
            
            self.__random_sleep__(5,8)
            # Select user from list
            elements = self.driver.find_elements_by_xpath("//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar']")
            if elements and len(elements) > 0:
                elements[0].click()
                
                self.typeMessage(user, message)
                self.__random_sleep__(3,5)
                self.selectors["back_to_dm"].click()
                return True

            # In case user has changed his username or has a private account
            else:
                self.log(f'User {user} not found! Skipping.')
                return False
            
        except Exception as e:
            self.error(e)
            return False

    def log(self, message):
        self.utils.logger.info(message)
        
    def error(self, message):
        self.utils.logger.error(message)

    def sendImage(self, user, image_path):
        self.log(f'Sending image from {image_path} to {user}')
        
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(0, 1)

        try:
            self.selectors['search_user'].wait_for()
            self.selectors['search_user'].type_slow(user)
            self.__random_sleep__(0, 1)
            
            # Select user from list
            elements = self.selectors["select_user"].find()
            if elements and len(elements) > 0:
                elements[0].click()
                self.__random_sleep__(0,1)
                self.getDMPage(user)
                
                if self.selectors["upload_image"].wait_for():
                    el = self.selectors["upload_image"].get()
                    el.send_keys(image_path)
                    self.__random_sleep__(1,3)
                
                self.__random_sleep__(0,1)

                return True
            
            else:
                print(f'User {user} not found! Skipping.')
                return False
            
        except Exception as e:
            self.error(e)
            return False

    def sendGroupMessage(self, users, message):
        self.log(f'Send group message to {users}')
        print(f'Send group message to {users}')
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(5, 7)

        try:
            usersAndMessages = []
            for user in users:
                if self.conn is not None:
                    usersAndMessages.append((user, message))

                self.selectors['search_user'].wait_for()
                self.selectors['search_user'].m_send_keys(user)
                self.__random_sleep__()

                # Select user from list
                elements = self.driver.find_elements_by_xpath(self.selectors['select_user'])
                if elements and len(elements) > 0:
                    elements[0].click()
                    self.__random_sleep__()
                else:
                    print(f'User {user} not found! Skipping.')

            self.typeMessage(user, message)

            if self.conn is not None:
                self.cursor.executemany("""
                    INSERT OR IGNORE INTO message (username, message) VALUES(?, ?)
                """, usersAndMessages)
                self.conn.commit()
            self.__random_sleep__(50, 60)

            return True
        
        except Exception as e:
            self.error(e)
            return False

    def __random_sleep__(self, minimum=10, maximum=20):
        if minimum == 0 and maximum == 0:
            return
        
        t = self.utils.random_num(minimum, maximum)
        m = int(t/60)
        s = int(t%60)
        
        self.log(f'Wait {m}:{s} minutes')
        self.utils.sleep(t)

    def __scrolldown__(self, amount=0, precise_value=None):
        if precise_value != None:
            self.driver.execute_script(f"window.scrollTo(0, {precise_value})")
            return
            
        try:
            self.scroll_down_index += 1
        except:
            self.scroll_down_index = 1
            
        self.driver.execute_script(f"window.scrollTo(0, {amount})")

    def teardown(self):
        self.driver.close()
        self.driver.quit()
    
    # *****************************************
            
    def generate_driver(self, headless=True, proxy_string="", instapy_workspace=None, profileDir=None, show_images=False, mobile=True):
        print(proxy_string)
        # Selenium config
        options = webdriver.ChromeOptions()
        
        if profileDir:
            options.add_argument("user-data-dir=profiles/" + profileDir)
        
        mobile_emulation = {
            # "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36"
            # "userAgent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 11.4 like Mac OS X) AppleWebKit/595.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/602.1'
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1"
        }
        
        if mobile:
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if not show_images:
            prefs = {"profile.managed_default_content_settings.images":2}
            options.add_experimental_option("prefs", prefs)
        options.add_argument("--enable-javascript")
        options.add_argument('--disable-extensions')
        options.add_argument('--profile-directory=Default')
        # options.add_argument("--incognito")
        options.add_argument("--disable-plugins-discovery");
        options.add_argument("--start-maximized")

        if headless:
            options.add_argument("--headless")
        
        if proxy_string != "":
            options.add_argument(f"--proxy-server={proxy_string}")
        
        options.add_argument("ignore-certificate-errors")
        
        try:
            self.driver = webdriver.Chrome(executable_path=CM().install(), options=options)
        except Exception as e:
            self.utils.terminal.show_message(f"[{self.username}] - Il tuo IP potrebbe essere cambiato. Aggiungilo al sito per continuare. Se il problema persiste, potresti dover aggiornare Chrome.")
            print(e)
            return
        
        self.driver.delete_all_cookies()
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except:
            pass
        
        if not mobile:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        
        try:
            self.driver.set_window_position(0, 0)
        except:
            pass
        try:
            self.driver.set_window_size(414, 1000)
        except:
            pass
        
        self.update_selectors()
    
    def next_tab(self):
        #get current window handle
        current = self.driver.current_window_handle
            
        #get first child window
        chwd = self.driver.window_handles
        
        for w in chwd:
        #switch focus to child window
            if(w!=current):
                self.driver.switch_to.window(w)
                break
