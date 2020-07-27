# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 12:25:17 2020

@author: AdilDSW
"""

# Importing system libraries
import os
import sys
import csv
import math
import traceback

# Importing 3rd-party libraries
from tqdm import tqdm
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

# Importing local libraries
from config import HITKSoupConfig

class HITKSoup:
    
    def __init__(self):
        self._config = HITKSoupConfig()
        self._browser = None
        self._roll_error_msg = "No such student exists"
        self._result_fields = ["name", "roll", "reg", "sgpao", "sgpae", "ygpa"]
        
    def _init_browser(self):
        """
        Initializes selenium with a headless Firefox webdriver.
        """
        options = Options()
        options.headless = True
        self._browser = webdriver.Firefox(options=options)
        
        
    def _pipeline(self, roll, sem, sem_year):
        """
        Pipeline for retrieving semester results.

        Parameters
        ----------
        roll : str
            Contains the roll number of an individual student.
        sem : str
            Contains the semester for which the result is required.
        sem_year : str
            Contains the year in which the semester was attended.

        Returns
        -------
        res : dict
            Contains the retrieved result along with the student's information.

        """
        roll = str(roll)
        sem = str(sem)
        sem_year = str(sem_year)
        
        res = {}
        for field in self._result_fields:
            res[field] = "-"
        res["roll"] = roll
        res['success'] = False
        
        self._config.load_config(sem, sem_year)
        config = self._config.config
        
        if config == False:
            print("ERROR: Configuration not loaded.")
            sys.exit()
        else:
            try:
                # Loading url
                self._browser.get(config['url'])
                
                # Inputting roll number
                roll_tb = self._browser.find_element_by_name(
                    config['roll_tb_name'])
                roll_tb.send_keys(roll)
                
                # Selecting semester
                sem_dd = Select(self._browser.find_element_by_name(
                    config['sem_dd_name']))
                sem_dd.select_by_visible_text(sem)
                
                # Submitting form
                submit_bt = self._browser.find_element_by_name(
                    config['submit_bt_name'])
                submit_bt.click()
                
                # Retrieving and cleaning information from webpage
                page_src = self._browser.page_source
                if self._roll_error_msg in page_src:
                    print("ERROR: Result missing for Roll {}.".format(roll))
                else:
                    try:
                        # Fetching roll number
                        res['name'] = self._browser.find_element_by_id(
                            config['name_id'])
                        res['name'] = res['name'].text.replace("Name", "")
                        res['name'] = res['name'].strip()
                        
                        # Fetching roll number
                        res['roll'] = self._browser.find_element_by_id(
                            config['roll_id'])
                        res['roll'] = res['roll'].text.split(" ")[2]
                        
                        # Fetching registration number
                        res['reg'] = self._browser.find_element_by_id(
                            config['reg_id'])
                        res['reg'] = res['reg'].text.split(" ")[2]
                        
                        # Fetching odd semester SGPA
                        res['sgpao'] = self._browser.find_element_by_id(
                            config['sgpao_id'])
                        res['sgpao'] = res['sgpao'].text.split(" ")[3]
                        
                        # Fetching even semester information if available
                        if self._config.sem_type == "EVEN":
                            # Fetching even semester SGPA
                            res['sgpae'] = self._browser.find_element_by_id(
                                config['sgpae_id'])
                            res['sgpae'] = res['sgpae'].text.split(" ")[3]
                            
                            # Fetching YGPA
                            res['ygpa'] = self._browser.find_element_by_id(
                                config['ygpa_id'])
                            res['ygpa'] = res['ygpa'].text.split(" ")[3]
                        
                        res['success'] = True
                        
                    except NoSuchElementException:
                        res['success'] = False
                        print("ERROR: Invalid configuration file.")
                        sys.exit()
                        
            except WebDriverException:
                print("ERROR: Cannot reach URL.")
                sys.exit()
            except NoSuchElementException:
                print("ERROR: Invalid configuration file.")
                sys.exit()
            except:
                traceback.print_exc()
                print("ERROR: An unexpected error has occurred.")
                sys.exit()
        
        return res
    
    def _generate_head(self, sem):
        """
        Generates the header of the result table.

        Parameters
        ----------
        sem : str
            Contains the semester for which the results are requested.

        Returns
        -------
        head : list
            Contains the headerof the result table.

        """
        sem = int(sem)
        osem = sem if sem % 2 == 1 else (sem - 1)
        esem = osem + 1
        year = math.ceil(sem / 2)
        head = [
            "Roll Number", 
            "Name", 
            "Registration Number", 
            "SGPA Odd (Sem {})".format(osem), 
            "SGPA Even (Sem {})".format(esem), 
            "YGPA (Year {})".format(year)
            ]
        
        return head
    
    def _display_result(self, sem, result):
        """
        Displays the result in a tabulated manner.

        Parameters
        ----------
        sem : str
            Contains the semester for which the results are requested.
        result : list
            Contains the retrieved results tabulated in a list.

        """
        print()
        print(tabulate(result, headers=self._generate_head(sem), 
                       colalign=("center", "left", "center", "center", 
                                 "center", "center")))
        print()
        print("STATUS: Operation Completed Successfully.")
    
    def _save_result(self, sem, result, save_dir, file_name):
        """
        Saves the fetched results into a CSV file.

        Parameters
        ----------
        sem : str
            Contains the semester for which the results are requested.
        result : list
            Contains the fetched results in a tabulated format.
        save_dir : str
            Contains the directory in which the file is to be saved.
        file_name : str
            Contains the name which will be used to save the file.

        Returns
        -------
        success : bool
            Contains True if saved successfully, False otherwise.

        """
        path = os.path.join(save_dir, file_name)
        if os.path.isdir(save_dir) is False:
            print("ERROR: Directory does not exist.")
            success = False
        elif os.path.exists(path):
            print("ERROR: File already exists in the given directory.")
            success = False
        else:
            head = self._generate_head(sem)
            try:
                with open(path, 'w') as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    writer.writerow(head)
                    writer.writerows(result)
                success = True
                print("STATUS: Result saved successfully at {}".format(path))
            except:
                success = False
                traceback.print_exc()
                print("ERROR: An unexpected error occurred.")
            
        return success
        
    
    def get_student_result(self, roll, sem, sem_year):
        """
        Fetches semester results for an individual student.

        Parameters
        ----------
        roll : str
            Contains the roll number of an individual student.
        sem : str
            Contains the semester for which the result is required.
        sem_year : str
            Contains the year in which the semester was attended.

        Returns
        -------
        result : list
            Contains the retrieved results tabulated in a list.

        """
        result = []
        print("STATUS: Fetching Results...")
        self._init_browser()
        res = self._pipeline(roll, sem, sem_year)
        result.append([
            res['roll'], 
            res['name'], 
            res['reg'],
            res['sgpao'], 
            res['sgpae'], 
            res['ygpa']
            ])
        self._browser.quit()
        
        self._display_result(sem, result)
        
        return result
        
    def get_batch_result(self, batch_csv_dir, sem, sem_year):
        """
        Fetches semester results for a batch of students.

        Parameters
        ----------
        batch_csv_dir : str
            Contains the directory for the file containing a batch of roll 
            numbers stored as comma separated values.
        sem : str
            Contains the semester for which the result is required.
        sem_year : str
            Contains the year in which the semester was attended.

        Returns
        -------
        result : list
            Contains the retrieved results tabulated in a list.

        """
        result = []
        print("STATUS: Fetching Results...")
        self._init_browser()
        if os.path.exists(batch_csv_dir) == False:
            print("ERROR: Batch CSV file does not exist.")
            sys.exit()
        else:
            with open(batch_csv_dir) as batch_csv_file:
                batch_data = csv.reader(batch_csv_file)
                for rolls in batch_data:
                    for roll in tqdm(rolls):
                        res = self._pipeline(roll, sem, sem_year)
                        result.append([
                            res['roll'], 
                            res['name'], 
                            res['reg'],
                            res['sgpao'], 
                            res['sgpae'], 
                            res['ygpa']
                            ])
        self._browser.quit()
        
        self._display_result(sem, result)
        
        return result
    
    def run(self):
        """
        Driver function.
        """
        print("-----------------------------")
        print("HITKSoup v1.0")
        print("by adildsw")
        print("-----------------------------")
        mode = input("Mode (Individual/Batch): ")
        mode = mode.upper()
        if mode not in ["INDIVIDUAL", "I", "BATCH", "B"]:
            print("ERROR: Invalid mode selected.")
            sys.exit()
        mode = mode[0]
            
        if mode == "I":
            roll = input("Roll Number: ")
            sem = input("Semester: ")
            sem_year = input("Semester Year: ")
            print()
            result = self.get_student_result(roll, sem, sem_year)
        else:
            batch_csv_dir = input("Roll Batch CSV Path: ")
            sem = input("Semester: ")
            sem_year = input("Semester Year: ")
            print()
            result = self.get_batch_result(batch_csv_dir, sem, sem_year)
        
        save_loop = True
        while save_loop:
            to_save = input("Do you want to save the results? (Yes/No): ")
            to_save = to_save.upper()
            if to_save not in ["YES", "Y", "NO", "N"]:
                print("ERROR: Invalid choice.")
            else:
                to_save = to_save[0]
                if to_save == "N":
                    save_loop = False
                else:
                    save_dir = input("Save Directory: ")
                    file_name = input("File Name: ")
                    print()
                    s_res = self._save_result(sem, result, save_dir, file_name)
                    save_loop = not s_res
            

if __name__ == "__main__":
    soup = HITKSoup()
    soup.run()

            