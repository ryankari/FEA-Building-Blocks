# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 08:23:22 2021

File: Class_read_parameters.py
@author: Ryan Kari <ryan.j.kari@gmail.com>
Last Modified Date: May 23, 2022
Last Modified by: Ryan Kari

"""

    # =============================================================================
    # 
    # =============================================================================      

import os
from openpyxl import load_workbook
from itertools import islice    
import pandas as pd
import numpy as np

class ClassReadParameters: 
        def __init__(self):
            print("readFromXLS functions __init__")
            
            
        def read_parameters_from_xls(self,dir_path = '.',\
                                     dir_name = 'Simulation_A.xlsx',sheet_name='Sheet1'):
                
            Sim_File_Path = os.path.realpath(dir_path)
            
            try:
                wb = load_workbook(Sim_File_Path+'\\' + dir_name)
                print('Excel file loaded from current directory using {}'\
                      .format(dir_name))
            
                # Active worksheet expected to be Sheet1
                ws = wb[sheet_name]
                data = ws.values
                
                #Read in each column name 
                cols = next(data)[1:]
                
                #Read in the data
                data = list(data)
                idx = [r[0] for r in data]
                data = (islice(r, 1, None) for r in data)
                
                df = pd.DataFrame(data, index=idx, columns=cols)
                df = df[df.isnull().all(axis=1)==False]
                return(df)   
            
            except: 
                print('Unable to load using Simulation_A.xlsx')
                quit()
            
            
                  
           
if __name__ == "__main__":
    readInstance = readFromXLSclass()
    df = readInstance.read_parameters_from_xls()
    