# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 15:18:20 2020

@author: AdilDSW
"""

# Importing system libraries
import os
import json

class HITKSoupConfig:
    
    def __init__(self):
        self.config = None
        self.sem_type = "INVALID"
        self.config_validation_fields = [
            "url",
            "roll_tb_name",
            "sem_dd_name",
            "submit_bt_name",
            "name_id",
            "reg_id",
            "roll_id",
            "sgpao_id"
            ]
    
    def load_config(self, sem, sem_year):
        sem = str(sem)
        sem_year = str(sem_year)
        
        if sem.isdigit() is False:
            sem_type = "INVALID"
        elif int(sem) < 1 or int(sem) > 8:
            sem_type = "INVALID"
        else:
            sem_type = "EVEN" if int(sem) % 2 == 0 else "ODD"
            
        self.sem_type = sem_type
        
        if len(sem_year) != 4 or sem_year.isdigit() is False:
            print("ERROR: Invalid configuration definition.")
        elif sem_type != "EVEN" and sem_type != "ODD":
            print("ERRPR: Invalid configuration definition")
        else:
            config_dir = "configs/{}_{}.json".format(sem_year, sem_type)
            if os.path.exists(config_dir):
                with open(config_dir) as config_file:
                    config = json.load(config_file)
                    if self.validate_config(config):
                        self.config = config
                    else:
                        self.config = None
                        print("ERROR: Invalid configuration file.")
            else:
                self.config = None
                print("ERROR: Configuration file missing for {} {} semester."
                      .format(sem_year, sem_type))
    
    def validate_config(self, config):
        for field in self.config_validation_fields:
            if field not in config:
                print("ERROR: Invalid configuration file.")
                return False
            
        if "sgpae_id" in config and "ygpa_id" not in config:
            print("ERROR: Invalid configuration file.")
            return False
        
        if config['url'].startswith("http") is False:
            print("ERROR: Invalid configuration file.")
            return False
        
        return True
