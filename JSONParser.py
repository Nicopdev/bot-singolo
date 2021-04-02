#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 19:34:57 2020

@author: nico
"""

from json import load, dumps
from os import makedirs, remove
from os.path import exists
from pickle import load as pload, dump as pdump
# import pickle

class FileManager:
    
    def __init__(self, work_directory, utils):
        if not exists(work_directory):
            makedirs(work_directory)
        if not exists(work_directory + "/pickles"):
            makedirs(work_directory + "/pickles")
        
        self.work_directory = work_directory + "/"
        self.utils = utils
        self.utils.log("Parser initialized")
    
    def exists(self, file):
        return exists(self.work_directory + file)
    
    def create_file(self, file):
        with open(self.work_directory + file, "a+") as fnew:
            fnew.close()
    
    def delete(self, file, WD=True):
        try:
            if WD:
                remove(self.work_directory + "/" + file)
            else:
                remove(file)
        except Exception as e:
            self.utils.error(f"Could not delete file {file}. Error: {e}")
    
    # PICKLE
    def pickle_load(self, file):
        try:
            with open(self.work_directory + "pickles/" + file, "rb") as fin:
                return pload(fin)
        except:
            return None
    
    def pickle_store(self, file, data):
        try:
            with open(self.work_directory + "pickles/" + file, "wb") as fout:
                pdump(data, fout)
        except Exception as e:
            self.utils.error(f"Could not store picle file: {e}")
    
    # JSON decode and encode *************************************************
    
    def dumps_json(self, obj):
        return dumps(obj)
    
    def decodeJSON(self, file_name):
        try:
            with open(self.work_directory + file_name, "r") as fin:
                dic = load(fin)
                fin.close()
                return dic
        except:
            open(self.work_directory + file_name, "w")
            self.utils.error(f"Could not decode the dictionary from the json file {file_name}")
            return {}
        
    def encodeJSON(self, file_name, dic):
        try:
            with open(self.work_directory + file_name, "w") as fout:
                fout.write(dumps(dic))
                fout.close()
                return None
        except:
            self.utils.error(f"Could not encode the dictionary in the json file {file_name}")
    
    # ************************************************************************
    # ";\n" separated file encode and decode to array ************************
    
    def decode_to_array(self, file_name, separator=";\n"):
        try:
            with open(self.work_directory + file_name, "r") as fin:
                arr = fin.read().split(separator)
                fin.close()
                return arr                
        except Exception as e:
            open(self.work_directory + file_name, "w")
            self.utils.error(f"Could not decode the array from the file {file_name}. {e}")
            return []
        
    def encode_from_array(self, file_name, array, separator=";\n"):
        if len(array) == 0:
            return
        try:
            with open(self.work_directory + file_name, "w") as fout:
                if len(array) > 1:
                    fout.write(separator.join(array))
                else:
                    fout.write(f"{array[0]}{separator}")
                fout.close()
                return None
        except:
            self.utils.error(f"Could not encode the array in the file {file_name}")
            return "Error"
    
    def append_from_array(self, file_name, array, separator=";\n"):
        if len(array) == 0:
            return
        try:
            with open(self.work_directory + file_name, "a+") as fout:
                if len(array) > 1:
                    fout.write(separator.join(array))
                else:
                    fout.write(f"{array[0]}{separator}")
                return None
        except:
            self.utils.error(f"Could not append the array to the file {file_name}")
    
    # ************************************************************************
    # ";\n" separated file encode and decode value after value
    
    def encode_value(self, file_name, string, separator=";\n"):
        try:
            with open(self.work_directory + file_name, "a+") as fout:
                fout.write(f"{string}{separator}")
        except:
            self.utils.error(f"Could not add the value to the file {file_name}")
        
    def decode_array_double_separator(self, file_name, separator=";\n", separator2="-"):
        try:
            with open(self.work_directory + file_name, "r") as fin:
                arr = fin.read().split(separator)
                result = list()
                for element in arr:
                    res = element.split(separator2)
                    try:
                        res.replace(";", "")
                    except:
                        pass
                    result.append(res)
                return result
        except:
            self.utils.error(f"Could not decode file {file_name} to arrays")
            return []
    
    
    