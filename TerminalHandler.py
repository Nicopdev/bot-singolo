#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 20:03:31 2020

@author: nico
"""
import curses as cr

class TerminalHandler:
    def __init__(self, utils, screen):
        
        self.utils = utils
        self.utils.log("Terminal initialized")
        
        self.current_index = 0
        self.should_change = True
        self.colors = list()
        self.newtext = list()
        self.wait_clear = True
        
        self.screen = screen
        
        cr.curs_set(0)
        cr.init_pair(1, cr.COLOR_BLACK, cr.COLOR_WHITE)
        cr.init_pair(2, cr.COLOR_BLACK, cr.COLOR_RED)
        cr.init_pair(3, cr.COLOR_WHITE, cr.COLOR_RED)
        
        for _ in range(0,100):
            self.colors.append(1)
            self.newtext.append("")
            
        self.screen.refresh()
    
    # ************************************************************************
    # High level curses ******************************************************
    
    def reset_colors(self):
        self.colors = list()
        self.newtext = list()
        
        for _ in range(0,100):
            self.colors.append(1)
            self.newtext.append("")
    
    @property
    def wait_clear_(self):
        return self.wait_clear
    
    def clear(self, wait=False):
        if wait:
            self.wait_clear = False
        self.screen.clear()
        self.screen.refresh()
    
    def show_menu(self, titles, secondary, individual_func=False, should_update_index=False, *handlers):
                
        should_run = True
        selection = None
        self.current_index = 0        
        if secondary:
            titles.append("BACK")
        
        while should_run:
            if secondary:
                self.should_change = False
            else:
                self.should_change = True
            
            _ = self.update_dims()
            # Print menu
            self.screen.clear()
            for inx, row in enumerate(titles):
                x = self.w//2 - len(max(titles, key=len))//2
                y = self.h//2 - len(titles)//2 + inx
                
                if self.colors[inx] == 2 and self.should_change:
                    text = self.newtext[inx]
                    if text == "":
                        text = row
                    if inx == self.current_index:
                        self.screen.attron(cr.color_pair(3))
                        self.screen.addstr(y, x, " > " + text + " ")
                        self.screen.attroff(cr.color_pair(3))
                    else:
                        self.screen.attron(cr.color_pair(2))
                        self.screen.addstr(y, x, text)
                        self.screen.attroff(cr.color_pair(2))
                else:
                    if inx == self.current_index:
                        self.screen.attron(cr.color_pair(1))
                        self.screen.addstr(y, x, " > " + row + " ")
                        self.screen.attroff(cr.color_pair(1))
                    else:
                        self.screen.addstr(y, x, row)
            self.screen.refresh()
            # Menu printed
            
            # Wait for input
            selection = self.wait_for_input(len(titles))
            
            if selection != None:
                if not individual_func:
                    if secondary:
                        if selection == len(titles) - 1:
                            self.current_index = 0
                            break
                        else:
                            if should_update_index:
                                handlers[selection](selection)
                            else:
                                handlers[selection]()
                    else:
                        handlers[selection]()
                else:
                    if selection == len(titles) - 1:
                            self.current_index = 0
                            # self.reset_colors()
                            break
                    else:
                        if should_update_index:
                            handlers[0](selection)
                        else:
                            handlers[0]()
    
    def show_menu_delete_selected(self, titles, secondary, *handlers):
        
        should_run = True
        selection = None
        self.current_index = 0        
        if secondary:
            titles.append("BACK")
        
        while should_run:
            if secondary:
                self.should_change = False
            else:
                self.should_change = True
            _ = self.update_dims()
            # Print menu
            self.screen.clear()
            for inx, row in enumerate(titles):
                x = self.w//2 - len(max(titles, key=len))//2
                y = self.h//2 - len(titles)//2 + inx
                
                if self.colors[inx] == 2 and self.should_change:
                    if inx == self.current_index:
                        self.screen.attron(cr.color_pair(3))
                        self.screen.addstr(y, x, " " + self.newtext[inx] + " ")
                        self.screen.attroff(cr.color_pair(3))
                    else:
                        self.screen.attron(cr.color_pair(2))
                        self.screen.addstr(y, x, self.newtext[inx])
                        self.screen.attroff(cr.color_pair(2))
                else:
                    if inx == self.current_index:
                        self.screen.attron(cr.color_pair(1))
                        self.screen.addstr(y, x, " " + row + " ")
                        self.screen.attroff(cr.color_pair(1))
                    else:
                        self.screen.addstr(y, x, row)
            self.screen.refresh()
            # Menu printed
            
            # Wait for input
            selection = self.wait_for_input(len(titles))
            
            if selection != None:
                if selection == len(titles) - 1:
                    self.current_index = 0
                    # self.reset_colors()
                    break
                else:                    
                    try:
                        handlers[0](selection)
                    except:
                        handlers[0]()
                    del titles[selection]
                    if len(titles) <= 1:
                        # self.reset_colors()
                        break
    
    def get_input(self, message):
        
        answer = self.raw_input(message)        
        
        if answer != None:
            self.screen.clear()
            self.screen.addstr(0, 0, f"You entered: {answer}. Press any key to continue")
            self.wait_any_key()
            return answer
    
    def change_color_row(self, row, newtext=""):
        if self.colors[row] == 1 and self.should_change:
            self.colors[row] = 2
            if newtext != "":
                self.newtext[row] = newtext
        else:
            self.colors[row] = 1
    
    def get_int_input(self, message):
        answer = self.raw_input(message)
        
        if answer != None:
            try:
                self.screen.clear()
                self.screen.addstr(0, 0, f"You entered: {answer}. Press any key to continue.")
                self.wait_any_key()
                return int(answer)
            except:
                self.screen.clear()
                self.screen.addstr(0, 0, "You didn't enter a number. Press any key to continue.")
                self.wait_any_key()
                return None
    
    def show_message(self, message, wait=True, wait_clear=False, func=None):
        self.screen.clear()
        if not wait_clear:
            if wait:
                self.screen.addstr(0, 0, f"{message} Press any key to continue.")
            else:
                self.screen.addstr(0, 0, f"{message}")
            self.screen.refresh()
            if wait:
                self.wait_any_key()
        else:
            self.screen.addstr(0, 0, f"{message}")
            self.screen.refresh()
            while self.wait_clear_ == True:
                func()
    
    def tprint(self, message):
        self.screen.clear()
        self.screen.addstr(0, 0, f"{message}")
        self.screen.refresh()
        
    # ************************************************************************
    # Low level curses *******************************************************
    
    def wait_any_key(self):
        cr.flushinp()
        
        key = self.screen.getch()
        while key == None:
            key = self.screen.getch()
            pass
        # else:
        #     self.utils.log(key)
        
    def raw_input(self, message):
        cr.curs_set(1)
        self.screen.clear()
        cr.echo()
        h, w = self.update_dims()
        
        self.screen.addstr(0, 0, message)
        self.screen.addstr(h-1, 0, "Enter without typing anything or enter U or u to undo.")
        answer = self.screen.getstr(2+len(message)//w, 0, 2000).decode()
        
        cr.curs_set(0)
        if answer == "U" or answer == "" or answer == "u":
            return None
        
        return answer
    
    def update_dims(self):
        h, w = self.screen.getmaxyx()
        self.h, self.w = h, w
        return (h, w)
        
    def wait_for_input(self, menu_len):
        key = self.screen.getch()
        self.screen.clear()
        
        if key == cr.KEY_UP: # and self.current_index > 0:
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = menu_len - 1
            return None
        elif key == cr.KEY_DOWN: # and self.current_index < len(self.current_menu) - 1:
            self.current_index += 1
            if self.current_index > menu_len - 1:
                self.current_index = 0
            return None
                
        elif key == cr.KEY_ENTER or key in [10, 13]:
            return self.current_index
    