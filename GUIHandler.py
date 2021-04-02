#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 16:13:46 2021

@author: nico
"""

#!/usr/bin/env python3
# -*- coding_ utf-8 -*-
"""
Created on Tue Jan 12 18:01:27 2021

@author: nico
"""

# InstaBOT Network
# GUIHandler.py

from tkinter import Tk, Button, Label, Entry, StringVar, IntVar, messagebox, Listbox

class GUIHandler:
    
    def __init__(self, *menu):
        root = Tk()
        root.title("InstaBOT")
        root.geometry("400x400")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root = root
        
        self.visible_views = list()
        self.selected_index = IntVar()        
        self.gate = StringVar()
        self.is_gate_closed = False
        self.menu_index = 0
        self.prev_index = 0
        self.menu_titles = list()
        self.menu_methods = list()
        for m in menu:
            # print(m)
            self.menu_titles.append(m[0])
            self.menu_methods.append(m[1])
        
        self.show_menu(0)
        self.change_colors = {}
    
    def on_closing(self):
        if messagebox.askokcancel("Chiudi", "Vuoi davvero chiudere il programma?"):
            self.is_gate_closed = True
            self.gate.set(self.gate.get())
            self.root.eval('::ttk::CancelRepeat')
            self.root.destroy()
            self.root.quit()
    
    def askokcancel(self, message, title="InstaBOT"):
        return messagebox.askokcancel(title, message)
    
    def mainloop(self):
        self.root.mainloop()
    
    def show_menu(self, menu):
        self.prev_index = self.menu_index
        self.menu_index = menu
        self.clear()
        
        l = Label(self.root, text="MENU PRINCIPALE")
        l.pack()
        self.visible_views.append(l)
        
        for index, title in enumerate(self.menu_titles[self.menu_index]):
            b = Button(self.root, text=title, command=lambda index=index:self.menu_button_tapped(index))
            b.pack()
            self.visible_views.append(b)
        
        if self.menu_index != 0:
            b = Button(self.root, text="Indietro", command=lambda:self.home())
            b.pack()
            self.visible_views.append(b)
    
    def clear(self):
        self.visible_views = list()
        for element in self.root.winfo_children():
            element.destroy()
    
    def home(self):
        self.show_menu(0)
    
    def get_input(self, message, is_int=False):
        self.gate.set("")
        self.prev_index = self.menu_index
        self._get_input(message, is_int)
        self.visible_views[-1].wait_variable(self.gate)
        if not self.is_gate_closed:
            
            g = self.gate.get()
            
            self.prev_menu()
            if g == "":
                return None
            else:
                return g
        
    def _get_input(self, message, is_int):
        self.clear()
        undo = Button(self.root, text="Annulla", command=self.prev_menu)
        undo.pack()
        l = Label(self.root, text=message)
        l.pack()
        e = Entry(self.root)
        e.pack()
        b = Button(self.root, text="Conferma", command=lambda e=e:self._confirm_input(e, is_int))
        b.pack()
        
        self.visible_views.extend([undo, l, e, b])
    
    def change_color_row(self, index, newTitle):
        
        try:
            menu = self.change_colors[self.menu_index]
            direction = menu[index]
            if direction:
                self.change_colors[self.menu_index][index] = False
                self.visible_views[index+1].config(text=self.menu_titles[self.menu_index][index])
            else:
                print("White")
                self.change_colors[self.menu_index][index] = True
                self.visible_views[index+1].config(text=newTitle)
        except:
            try:
                self.change_colors[self.menu_index][index] = True
                self.visible_views[index+1].config(text=newTitle)
            except:
                self.change_colors[self.menu_index] = {index : True}
                self.visible_views[index+1].config(text=newTitle)
                
    def show_menu_delete_selected(self, titles, completion):
        self.prev_index = self.menu_index
        self.menu_index = 10
        self.clear()
        undo = Button(self.root, text="Annulla", command=self.prev_menu)
        undo.pack()
        
        listbox = Listbox(self.root,
                          relief='sunken', 
                          borderwidth=1, 
                          selectmode='SINGLE', 
                          exportselection=False,
                          activestyle = 'dotbox',
                          width=45,
                          )
        
        for index, title in enumerate(titles):
            listbox.insert(index+1, f"{index+1} - {title}")
        
        listbox.pack()
        delete = Button(self.root, text="Elimina", command=lambda:self.delete_last(completion))
        delete.pack()
        
        self.visible_views.extend([undo, listbox, delete])
        
    def delete_last(self, completion):
        i = self.visible_views[1].curselection()
        
        self.visible_views[1].selection_clear(0, "end")
        
        self.visible_views[1].delete(i)
        
        if i == (self.visible_views[1].size(),):
            self.visible_views[1].selection_set("end")
        else:
            print(i)
            self.visible_views[1].selection_set(i)
    
        completion(i[0])
        
        if self.visible_views[1].size() == 0:
            self.prev_menu()
        
    def prev_menu(self):
        self.clear()
        self.gate.set("")
        self.show_menu(self.prev_index)
    
    def _confirm_input(self, entry, is_int):
        res = entry.get()
        if not res.isspace() and res:
            if is_int:
                try: 
                    int(res)
                    self.gate.set(res)
                except:
                    pass
            else:
                self.gate.set(entry.get())
    
    def menu_button_tapped(self, index):
        obj = self.menu_methods[self.menu_index][index]
        
        try:
            if type(obj) is int:
                m = int(self.menu_methods[self.menu_index][index])
                self.show_menu(m)
            elif type(obj) is tuple:
                # do stuff
                pass
            else:
                self.menu_methods[self.menu_index][index]() # Can add here generic params
        except Exception as e:
            print(f"Error: {e}")
            return
        
    def show_message(self, message):
        messagebox.showinfo("ERRORE", message)