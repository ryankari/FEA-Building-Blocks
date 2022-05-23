# -*- coding: utf-8 -*-
"""
Created on Mon May 16 15:09:22 2022

@author: RKari
"""

# Load External packages
import numpy as np
import os
import pandas as pd
import sys

# Set working directory path relative to Python. Can be specific study path.   
if '__file__' in globals():   
    program_path = os.path.dirname(__file__)
    print(program_path)
    if program_path not in sys.path:
        sys.path.insert(0,program_path)

cwd = os.getcwd()
print('Curent working directory = ',cwd)


# Classes
from Class_VTU_Functions import classVTUImport
VTU = classVTUImport()

from Class_Elmer_Functions import ClassElmer
class_elmer = ClassElmer()

from Class_read_parameters import ClassReadParameters
readInstance = ClassReadParameters()

from Class_gmsh_Functions import gmshFunctions
classGMSH = gmshFunctions()

from Class_SQL_Functions import classSQL
SQLclass = classSQL()

from absolute_file_number import update_file_designator

from Class_FEA_AnalysisV1 import ClassFEAAnalysis
Analysis = ClassFEAAnalysis()

       

# Make log, db,and file_id directories if don't exist
if not os.path.isdir(os.path.join(cwd,'log')):
    os.mkdir(os.path.join(cwd,'log'))

db_subdir = 'db'
if not os.path.isdir(os.path.join(cwd,db_subdir)):
    os.mkdir(os.path.join(cwd,db_subdir))
    
file_id_subdir = 'file_id'
if not os.path.isdir(os.path.join(cwd,file_id_subdir)):
    os.mkdir(os.path.join(cwd,file_id_subdir))    

parameters_subdir = 'parameters'
if not os.path.isdir(os.path.join(cwd,parameters_subdir)):
    print('Making parameters direction. Need to add parameter spreadsheet')
    os.mkdir(os.path.join(cwd,parameters_subdir))    
    quit()
   
    
# Make dictionaries with path information   
db_filename = 'sql_database_study1.db'
db_dict = {'filename':db_filename,\
           'filepath':os.path.join(cwd,db_subdir),\
           'path':os.path.join(os.path.join(cwd,db_subdir),db_filename)\
           ,'table':'study1'}

file_id_filename = 'abs_file_id.txt'
file_id_dict = {'filename':file_id_filename,\
           'filepath':os.path.join(cwd,file_id_subdir),\
           'path':os.path.join(os.path.join(cwd,file_id_subdir),file_id_filename)}

parameters_filename = 'Simulation_A.xlsx'
parameters_dict = {'filename':parameters_filename,\
           'filepath':os.path.join(cwd,parameters_subdir),\
           'path':os.path.join(os.path.join(cwd,parameters_subdir),parameters_filename)}
    

# Read in spreadsheet
df_all = pd.read_excel(parameters_dict['path'])

body_id = {'coreBody':{'volume':3},'concentratorBody':{'volume':2},\
           'coilBody':{'volume':np.nan},'airBody':{'volume':1,'boundary':np.nan}}


for item in df_all.T.iteritems():
    
      df_active = pd.DataFrame(item[1]).T.squeeze()

      output,body_id = classGMSH.createMesh(df_active,body_id,cwd,view_geo_only = False)

      if (output == "view only"):
          quit()
      
      class_elmer.convertToElmerMesh(cwd)  
      body_id = class_elmer.extract_ids_from_log(cwd,'elmer_grid_log.txt')    

      # Change names to update filename
      class_elmer.UpdateSIF(df_active,body_id,cwd,filename = 'case_automate.sif')

      class_elmer.Execute_Solver(cwd,MPI=True,logFileName ='elmer_solver_log.txt')
      # If solver completed generate unique file designator
      df_active['file_id']  = update_file_designator(project_type = 'CT',\
                            read_or_increment = 'increment',filename = file_id_dict['path'])
          
      df_active['run_time'] = class_elmer.extract_runtime_from_fea(cwd,'elmer_solver_log.txt')
      df_active['finish_time'] = class_elmer.extract_finishdate_from_fea(cwd,'elmer_solver_log.txt')
      
      # Store all parameters with unique file designator to SQLite database
      SQLclass.write_to_master_table(df_active,db_dict)
      
      
# Carry about custom analysis - Where the fun begins
Analysis.process_vtu_data(cwd,parameters_dict)    