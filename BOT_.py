#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 16:44:51 2020

@author: nico
"""

# Interactive Menu

from sys import exit
from botSupport import Options, Bot
from utils import Utils
from GUIHandler import GUIHandler
from bot import InstaDM
# from processes_handler import ProcessesHandler

PROXIES_DIR = "instaBOT_proxies.txt"
OPTIONS_DIR = "instaBOT_options.json"
TARGET_ACCOUNTS_DIR = "instaBOT_target_accounts.txt"
DONE_ACCOUNTS_DIR = "done_users.txt"
WD = "instaBOT_working_directory"

class InstaBOT:
    
    def __init__(self):
        terminal = GUIHandler(
                (["Avvia", "Crea account", "Avvia routine", "Pubblica post e storia", "Modifica messaggio generico", "Modifica target", "Modifica pagina host", "Modifica gli account", "Opzioni", "Disabilita debug", "Abilita immagini", "Ferma tutti i bot", "Esci"], 
                 [self.start, self.start_new_method, self.start_routine, self.publish, self.change_message, self.change_target, self.change_host, 1, 2, self.toggle_debug, self.toggle_images, self.stop_all, self.shutdown]),
                
                (["Aggiungi profilo", "Elimina profilo", "Attiva/Disattiva profilo", "Modifica parametri profilo"],
                 [self.add_profile, self.remove_profile, self.add_profile, self.remove_profile]),
                
                (["Conteggio run", "Conteggio utenti per run", "Delay tra run", "Delay tra utenti"],
                 [self.change_run_count, self.change_users_per_run_count, self.change_inter_run_delay, self.change_inter_user_delay])
            )
            
        self.utils = Utils(WD, "instaBOT_logs", terminal)
        self.terminal = terminal
        self.phandler = self.utils.phandler                    
        self.options = Options(WD, self.utils)
        self.options.load()
            
        if self.options.show_images == True:
            self.terminal.change_color_row(10, "Disabilita immagini")
                    
        if self.options.debug == False:
            self.terminal.change_color_row(9, "Abilita debug")
            
        if not self.utils.has_permission():
            self.terminal.show_message("Non hai le autorizzazioni necessarie per accedere. Contatta il team di sviluppo per ottenre un'autorizzazione valida.")
            exit()
            raise "FatalError"
            
        self.init_menu()
        return
        try:
            
            terminal = GUIHandler(
                (["Avvia", "Crea account", "Avvia routine", "Pubblica post e storia", "Modifica messaggio generico", "Modifica target", "Modifica pagina host", "Modifica gli account", "Opzioni", "Disabilita debug", "Abilita immagini", "Ferma tutti i bot", "Esci"], 
                 [self.start, self.start_new_method, self.start_routine, self.publish, self.change_message, self.change_target, self.change_host, 1, 2, self.toggle_debug, self.toggle_images, self.stop_all, self.shutdown]),
                
                (["Aggiungi profilo", "Elimina profilo", "Attiva/Disattiva profilo", "Modifica parametri profilo"],
                 [self.add_profile, self.remove_profile, self.add_profile, self.remove_profile]),
                
                (["Conteggio run", "Conteggio utenti per run", "Delay tra run", "Delay tra utenti"],
                 [self.change_run_count, self.change_users_per_run_count, self.change_inter_run_delay, self.change_inter_user_delay])
            )
            
            self.utils = Utils(WD, "instaBOT_logs", terminal)
            self.terminal = terminal
            self.phandler = self.utils.phandler                    
            self.options = Options(WD, self.utils)
            self.options.load()
            
            if self.options.show_images == True:
                self.terminal.change_color_row(10, "Disabilita immagini")
                    
            if self.options.debug == False:
                self.terminal.change_color_row(9, "Abilita debug")
            
            if not self.utils.has_permission():
                self.terminal.show_message("Non hai le autorizzazioni necessarie per accedere. Contatta il team di sviluppo per ottenre un'autorizzazione valida.")
                self.terminal.on_closing()
                exit()
                raise "FatalError"
            
            self.init_menu()
        except KeyboardInterrupt:
            self.utils.log("Stopping...")
            self.shutdown()
        except Exception as e:
            print(f"Errore: {e}")
            self.utils.error(f"ERROR: {e}")
            self.utils.terminal.show_message(f"[Errore] - {e}. Contatta uno sviluppatore.")
            self.shutdown()
    
    def init_menu(self):
        self.terminal.mainloop()

    def stop_all(self):
        if len(self.phandler.processes) > 0:
            
            if self.terminal.askokcancel("Vuoi fermare tutti i bot? Questo processo potrebbe impiegare fino a 30 secondi"):
                self.phandler.stop_all(False)
    
    def shutdown(self):
        self.terminal.on_closing()
    
    def change_host(self):
        new = self.terminal.get_input("Inserisci l'username della host")
    
        if new != None:
            self.options.host = new
            self.options.save()
    
    def toggle_debug(self):
        self.terminal.change_color_row(9, "Abilita debug")
        self.options.debug = not self.options.debug
        self.options.save()

    def toggle_images(self):
        self.terminal.change_color_row(10, "Disabilita immagini")
        self.options.show_images = not self.options.show_images
        self.options.save()
    
    def start_routine(self):
        self.phandler.start()
        for index in range(0, len(self.options.accounts)):
            _ = self.phandler.new(index, self.options, only_proxy=True)

    def publish(self):
        
        username = self.options.accounts[0].username
        password = self.options.accounts[0].password
        proxy = self.options.accounts[0].proxy
        
        insta = InstaDM(self.utils, username, password, proxy_string=proxy, headless=(not self.options.debug), generate_driver=True, show_images=self.options.show_images, mobile=True)
        insta.login()
        insta._publish_story()
        insta._publish_post()

    def start(self):
                
        if self.phandler.get_active > 0 or len(self.options.accounts) < 1 and not self.options.show_images:
            return
        
        if self.scrape():
            self.phandler.start()
            for index in range(0, len(self.options.accounts)):
                _ = self.phandler.new(index, self.options, True) # True quando recupero account
    
    def scrape(self):
        # Get the list of all the scraped users
        users = self.utils.scrape(self.options)
        n = len(users)
        # users = self.utils.parser.decode_to_array(TARGET_ACCOUNTS_DIR) # Other method
        
        for i, _ in enumerate(self.options.accounts):
            
            # Create a file for every account
            to_append = users[:self.options.run_count*self.options.user_per_run_count]            
            self.utils.parser.encode_from_array(f"stored_users_{i}.txt", to_append)
            
            users = users[self.options.run_count*self.options.user_per_run_count:]
        
        # Save the remaining users back into the target accounts file
        self.utils.parser.encode_from_array(TARGET_ACCOUNTS_DIR, users)
        print(n)
        print(n >= self.options.run_count*self.options.user_per_run_count*len(self.options.accounts))
        
        return n >= self.options.run_count*self.options.user_per_run_count*len(self.options.accounts)
    
    def start_new_method(self):
        
        insta = InstaDM(self.utils, "Creazione account", "", proxy_string="", headless=(not self.options.debug), generate_driver=True, show_images=True, mobile=False)
        
        # return
        insta.create_accounts()
    
    ##########################################################################
    # GUI 
    
    def change_run_count(self):
        new = int(self.terminal.get_input("Inserisci il nuovo conteggio run", True))
        
        if new != None:
            self.options.run_count = new
            self.options.save()
    
    def change_users_per_run_count(self):
        
        new = int(self.terminal.get_input("Inserisci il nuovo conteggio utenti per run", True))
        
        if new != None:
            self.options.user_per_run_count = new
            self.options.save()
    
    def change_inter_run_delay(self):
        new = int(self.terminal.get_input("Inserisci il nuovo delay tra run", True))
        
        if new != None:
            self.options.inter_run_delay = new*60
            self.options.save()
    
    def change_inter_user_delay(self):
        new = int(self.terminal.get_input("Inserisci il nuovo delay tra utenti", True))
        
        if new != None:
            self.options.inter_user_delay = new
            self.options.save()
      
    def change_message(self):
        new = self.terminal.get_input("Inserisci il nuovo messaggio (usa \ per andare a capo)")
        
        if new != None:
            self.options.message = new.replace("\\", "\n")
            self.options.save()
        
    def change_target(self):
        new = self.terminal.get_input("Inserisci il nuovo username target")
        
        if new != None:
            self.options.target = new
            self.options.save()
    
    def _show_all_accounts(self, secondary, individual_func, should_update_index, *handlers):
        menu = list()
        for account in self.options.accounts:
            menu.append(f"{account.username}  {account.proxy}")
            
        if len(menu) != 0:
            self.terminal.show_menu(menu, secondary, individual_func, should_update_index, *handlers)
    
    def edit_username(self):
        self._show_all_accounts(True, True, True, self._edit_username)
        
    def _edit_username(self, index):
        new = self.terminal.get_input("Inserisci il nuovo username")
        
        if new != None:
            self.options.accounts[index] = Bot(new, self.options.accounts[index].password, self.options.accounts[index].proxy, self.options.accounts[index].message)
        self.options.save()
    
    def edit_password(self):
        self._show_all_accounts(True, True, True, self._edit_password)
    
    def _edit_password(self, index):
        new = self.terminal.get_input("Inserisci la nuova password")
        
        if new != None:
            self.options.accounts[index] = Bot(self.options.accounts[index].username, new, self.options.accounts[index].proxy, self.options.accounts[index].message)
        self.options.save()

    def edit_proxy(self):
        self._show_all_accounts(True, True, True, self._edit_proxy)
    
    def _edit_proxy(self, index):
        new = self.terminal.get_input("Inserisci la nuova proxy")
        
        if new != None:
            self.options.accounts[index] = Bot(self.options.accounts[index].username, self.options.accounts[index].password, new, self.options.accounts[index].message)
        self.options.save()
            
    def edit_message(self):
        self._show_all_accounts(True, True, True, self._edit_message)
    
    def _edit_message(self, index):
        new = self.terminal.get_input("Inserisci il nuovo messaggio")
        
        self.utils.log(index)
        
        if new != None:
            self.options.accounts[index] = Bot(self.options.accounts[index].username, self.options.accounts[index].password, self.options.accounts[index].proxy, new)
        self.options.save()
            
    def remove_profile(self):
        
        menu = list()
        for account in self.options.accounts:
            menu.append(f"{account.username}  {account.proxy}")
        
        if len(menu) != 0:
            self.terminal.show_menu_delete_selected(menu, self.remove_account)
    
    def remove_account(self, position):
        del self.options.accounts[position]
        self.options.save()
    
    def add_profile(self):
        
        run = True
        while run:
            run = False
            new = self.terminal.get_input("Inserisci il profilo con la seguente forma:\nusername password proxy messaggio (facoltativo)")
            
            if new != None:
                new = new.split(" ")
                if len(new) < 3:
                    run = True
                    self.terminal.show_message("Usa l'ordine corretto': username password proxy")
                elif len(new) == 3:
                    if new[2] == "noproxy":
                        bot = Bot(new[0], new[1], "", "") 
                    else:
                        bot = Bot(new[0], new[1], new[2], "")
                    
                    run = False
                    self.options.accounts.append(bot)
                    self.options.save()
                else:
                    run = False
                    msg = " ".join(new[3:])
                    
                    if new[2] == "noproxy":
                        bot = Bot(new[0], new[1], "", msg.replace("\\", "\n"))
                    else:
                        bot = Bot(new[0], new[1], new[2], msg.replace("\\", "\n"))
                    self.options.accounts.append(bot)
                    self.options.save()
    
InstaBOT()









