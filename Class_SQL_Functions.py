# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 09:36:09 2021

@author: RKari
"""

import sqlite3 as sql
from sqlalchemy import create_engine
import os
from pathlib import Path
import pandas as pd

#remember to instantiate the class as follows: 

#from SQL_functions import SQL_definitions
#SQL = Class_SQL_definitions()
#SQL.write_to_master_table(df)


class classSQL:
    
        def __init__(self):
            print("SQL_functions __init__")
        
        

        # =============================================================================
        """ 
        readSqlConfigCSV
        # Description: Uses pandas to read in the configuration file containing the config info
        """ 
        # =============================================================================
        def readSqlConfigCSV(self,File_Path = "sqlConfig.csv"):

            
            dir_path_python = os.path.dirname(os.path.realpath(__file__))
            Config_File_Path = dir_path_python+"\\"+File_Path
            #Check to see if file exists
            try:
                programPaths = pd.read_csv(Config_File_Path,names = ['description','path'])
                
            except FileNotFoundError:
                print("--- Error --- \n" + Config_File_Path + "not found in Paths")
                print("or unable to read csv file")
            
            #Convert into a dictionary
            programPaths = programPaths.set_index('description')
            temp = programPaths.T.to_dict(orient='records')
            dictionary = temp[0]
            return(dictionary)
                

        # =============================================================================
        #     
        # =============================================================================
        def file_handling(self,table = 'test',\
                          filename = r'C:\Temp\sql_database1.db'):

            
            my_file = Path(filename)
            
            if ( my_file.is_file() ):
                if (os.path.getsize(filename) != 0):
                    #File exists and is not empty
                    print('{} exists'.format(my_file.name))
                    
                    conn = sql.connect(filename)
                    cursor = conn.cursor()
                    # Get all tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    if table in tables:
                        print("table {} in {} exists. appending".format(table,my_file.name))
                        table_status = True
                    else:
                        print("table {} does not exist.".format(table))
                        table_status = False
                    
                else:
                    #File exists and is empty
                    print('{} empty'.format(my_file.name))
                    conn = sql.connect(filename)
                    table_status = False
                    
            else:
                #File does not exist. Check if folder exists
                if os.path.isdir(filename) == False:
                    print('Directory does not exist - Need to create directory')
                    return(0)
                
                #File does not exist but folder does. Create a new file with default entry
                print('{} does not exist - creating'.format(my_file.name))
                conn = sql.connect(filename)
                table_status = False
            
            conn.close()
            return(table_status)
            
        
        
# =============================================================================
#      Write to SQL Table  
# =============================================================================
     
        def write_to_master_table(self,dfInput,db_dict):
            table = db_dict['table']
            filename = db_dict['path']
            table_status = self.file_handling(table,filename)

            df = dfInput.to_frame().T
            
            
            if 'file_id' in df:
                print('file_id location as {}\n'.format(df['file_id']))
            
                if 'index' in df:
                    print('Dropping index')
                    df = df.drop(columns = 'index')

                if 'Index' in df:
                    print('Dropping Index')
                    df = df.drop(columns = 'Index')
                    
                if 'Output Dir' in df:
                    print('Dropping Output Dir')
                    df = df.drop(columns = 'Output Dir')
                    
                if df.columns.is_unique == False:
                    print("Columns in df not unique. Forcing to be unique.")
                    df = df.loc[:,~df.columns.duplicated()]    
                    
                try:
                    print("Writing to dB at {} \ntable = {}\n".\
                          format(filename,table))
                        
                    conn = sql.connect(filename)
                    
                    df2 = df.astype('str')
                    if table_status == True:
                        
                        cursor = conn.execute('select * from {}'.format(table))
                        colnames = cursor.description
                        rowArray = []
                        for row in colnames:
                            rowArray.append(row[0])
                            
                        import collections
                        if collections.Counter(rowArray) == collections.Counter(df.index):
                            print("Data and SQL have same columns")
                            df2.to_sql(table,conn,if_exists='append')

                        else:
                            print("Data and SQL do not have same columns. Best to create new table\n")
                            print("Closing connection\n\n")

                        
                    else:
                   
                        df2.to_sql(table,conn,if_exists='append')
                    
                    
                    conn.close()
                    
                except:
                    print(df)
                    print("\nUnable to write to database\n")
            else:
                print('No file_id. Unable to write to table {}'.format(table))
            
            
# =============================================================================
#             return_specific_file_id
# =============================================================================
        def return_specific_file_id(self,file_id):
            
            sqlConfig = self.readSqlConfigCSV()
                        
            engine = create_engine(sqlConfig['databaselocation'], echo=False)          
            output = engine.execute("SELECT * FROM file_list_name").fetchall()
            print(output)