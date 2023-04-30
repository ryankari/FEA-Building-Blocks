# -*- coding: utf-8 -*-
"""
Created on Mon May 16 15:09:22 2022

This serves as the main executable to demonstrate a possible program flow
that ranges from creating a directory structure, loading in file paths,
loading in the parameters, creating a mesh in GMSH, configuring the mesh for FEA,
modifying an ELMER *.sif simulation file, storing the data, and then appending
the parameters used with a unique file_id (for use as a foreign key) into a 
SQLite database. A sample analysis connecting the parameters used to generate the
mesh to file FEA results are presented, as they might be used for optimization.

These pieces are well suited for building a GUI, Jupyter, 
File: ExecuteFEA.py
@author: Ryan Kari <ryan.j.kari@gmail.com>
Last Modified Date: April 29, 2023
Last Modified by: Ryan Kari
Description: Noted a few depracated functions specific to Pandas causing issues. 
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
    # Adding as will change working directory to project specific directory
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


if os.path.realpath(program_path) == os.path.realpath(cwd):
    proceed = input("You are in the CWD and not an experimental path. \n\
                    Do you wish to proceed in Building Block Study 1, or 2? 1 or 2\n")
    if not ((proceed == '1') or (proceed == '2')):
        sys.exit()
    elif (proceed == '1'):
        os.chdir("./Building Block Study 1")
        cwd = os.getcwd()
        print('Changing working directory')
    elif (proceed == '2'):
        os.chdir("./Building Block Study 2") 
        cwd = os.getcwd()
        print('Changing working directory')

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
    print('Making parameters direction. Need to add parameter spreadsheet into ./parameters. Quiting.')
    os.mkdir(os.path.join(cwd,parameters_subdir))    
    quit()

analysis_subdir = 'analysis'
if not os.path.isdir(os.path.join(cwd,analysis_subdir)):
    os.mkdir(os.path.join(cwd,analysis_subdir))  
    
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

analysis_filename = 'outLine.xlsx'
analysis_dict = {'filename':analysis_filename,\
           'filepath':os.path.join(cwd,analysis_subdir),\
           'path':os.path.join(os.path.join(cwd,analysis_subdir),analysis_filename)}

# Read in spreadsheet
importedParams = pd.read_excel(parameters_dict['path'])

body_id = {'coreBody':{'volume':3},'concentratorBody':{'volume':2},\
           'coilBody':{'volume':np.nan},'airBody':{'volume':1,'boundary':np.nan}}


        
        
for item in importedParams.iterrows():   
      dfActive = item[1]

      output,body_id = classGMSH.createMesh(dfActive,body_id,cwd,view_geo_only = False,view_mesh_only=False)

      if (output == "view only"):
          quit()
      
      class_elmer.convertToElmerMesh(cwd)  
      body_id = class_elmer.extract_ids_from_log(cwd,'elmer_grid_log.txt')    

      # Change names to update filename
      class_elmer.UpdateSIF(dfActive,body_id,cwd,filename = 'case_automate.sif')

      class_elmer.Execute_Solver(cwd,MPI=True,logFileName ='elmer_solver_log.txt')
      # If solver completed generate unique file designator
      dfActive['file_id']  = update_file_designator(project_type = 'CT',\
                            read_or_increment = 'increment',filename = file_id_dict['path'])
          
      dfActive['run_time'] = class_elmer.extract_runtime_from_fea(cwd,'elmer_solver_log.txt')
      dfActive['finish_time'] = class_elmer.extract_finishdate_from_fea(cwd,'elmer_solver_log.txt')
      
      # Store all parameters with unique file designator to SQLite database
      #dfActiveTrans = pd.DataFrame(dfActive).T.set_index('Index',drop=True)
      SQLclass.write_to_master_table(dfActive,db_dict)
      
      
# Carry about custom analysis - Where the fun begins
#Analysis.process_vtu_data(cwd,parameters_dict)    

meshDict = Analysis.import_vtu_data(parameters_dict,importedParams)

# Set endpoints to sample data over a line
a = [-.050, .02, 0]
b = [ .050, .02, 0]
lineOutput = Analysis.extractDatafromLine(meshDict,a,b)

ptOutput =  Analysis.extractSpecificPts(lineOutput, [0],'Field Z')

Analysis.createSamplePlots(ptOutput,lineOutput,importedParams)
    
with pd.ExcelWriter(analysis_dict['path']) as writer:
    ptOutput.to_excel(writer,sheet_name = 'pointData')
    lineOutput.to_excel(writer,sheet_name = 'lineData')