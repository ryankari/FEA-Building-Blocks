# -*- coding: utf-8 -*-
"""
Created on Wed May 11 20:15:37 2022

File: Class_Elmer_Functions.py
@author: Ryan Kari <ryan.j.kari@gmail.com>
Last Modified Date: May 23, 2022
Last Modified by: Ryan Kari

"""
import os
from pathlib import Path

class ClassElmer:
    
    
    
    # =============================================================================
    #     Initialize
    # =============================================================================
    def __init__(self):
        print("Initializing Elmer - Load in program paths")
            
        #self.elmer_self.path_dict = self.readProgramPathsCSV('ElmerFEAFilePaths.csv')    
        import pandas as pd
        File_Path = "ElmerFEAFilePaths.csv"
        
        dir_path_python = os.path.dirname(os.path.realpath(__file__))
        Config_File_Path = dir_path_python+"\\"+File_Path
        #Check to see if file exists
        try:
            programPaths = pd.read_csv(Config_File_Path,names = ['description','path'])
            
        except FileNotFoundError:
            print("--- Error --- \n" + Config_File_Path + " not found in Paths")
        
        #Check each file path, ensuring the file exists 
        for item in programPaths.iterrows():
            if not os.path.exists(item[1]['path']):
                print("--- Error ---\nUnable to find " + item[1]['path'] + "\n" )
                FileNotFoundError
            else:
                print("Found ",item[1]['path'])
        
        #Convert into a dictionary
        programPaths = programPaths.set_index('description')
        self.path_dict = programPaths.T.to_dict(orient='records')[0]


        
               
    
    
# =============================================================================
#   Make ELMER files
# =============================================================================
    def convertToElmerMesh(self,cwd,Variable_Name='Input_Geometry',outputDirName = "Output"):


        #Load into Elmer Format and Store in Output Folder
        #Make sure to inspect as can change boundary names
        cmd = [self.path_dict['elmerGridPath'],"14","2",Variable_Name+".msh","-autoclean","-out","Output"]
        print(cmd)
        output = (self.Execute_CMD(cmd))
        logPath = os.path.join(cwd,'log')
        with open(os.path.join(logPath,'std_mesh_log.txt'),'w') as filehandle:
                filehandle.writelines("%s\n" % place for place in output)
                
        #Change to directory Output to place Elmer Files.  
        
        os.chdir(outputDirName)

        #Write to Elmer mesh format
        cmd = [self.path_dict['elmerGridPath'],"2","4","mesh"]
        output += (self.Execute_CMD(cmd))       
        
        #Change directory back
        os.chdir("..")
        cwd = os.getcwd()
        print("Current Working Directory is:",cwd)

        #Also create partitioned out for MPI in outputDir
        cmd = [self.path_dict['elmerGridPath'],"14","2",Variable_Name+".msh",\
               "-autoclean","-out",outputDirName,"-partition","4","1","1","0"]
        (self.Execute_CMD(cmd))
        
        logPath = os.path.join(cwd,'log')
        with open(os.path.join(logPath,'elmer_grid_log.txt'),'w') as filehandle:
            filehandle.writelines("%s\n" % place for place in output)  
            
# =============================================================================
# 
# =============================================================================
    def extract_ids_from_log(self,cwd,elmerLogName = 'elmer_grid_log.txt'):
        


        
       # body_id_ext = pd.read_csv('feature_identifiers.txt', header=None, index_col=0, squeeze=True).to_dict()
        import json
        body_id_ext = json.load(open(os.path.join(cwd,'feature_identifiers.txt')))

                
        
        logPath = os.path.join(cwd,'log')
        file1 = open(os.path.join(logPath,elmerLogName),"r")
        f1 = file1.readlines()
        Variable_Info = []
        #Read in the file appending into variable_info
        for item in f1:
            Variable_Info.append(item)
        
        
        
        str_subset = 'boundary index changed ' + str(body_id_ext['airBody']['boundary'])
        for item in Variable_Info:
            if (item.find(str_subset) >= 0):
                value = item
                start = value.find('-> ')
                end = value.find(' in ')
                
                output = int(value[start+3:end])
                body_id_ext['airBody']['boundary'] = int(output)

           
        # Need to change to only look for valid bodies, and once one found, stop looking
        body_id_ext_copy = body_id_ext.copy()
        for item in Variable_Info:
            
            for key in body_id_ext.keys():
                str_subset = 'body index changed ' + str(body_id_ext[key]['volume'])
                line_in_var = item
                if (line_in_var.find(str_subset) >= 0):
                    value = item
                    start = value.find('-> ')
                    end = value.find(' in ')
                    print(str_subset,line_in_var,'key = ',key)
                    output = int(value[start+3:end])
                    body_id_ext_copy[key]['volume'] = int(output)
 
        body_id_ext = body_id_ext_copy      
        
     #   with open('feature_identifiers_Elmer.txt','w') as f:
     #       for key,value in body_id_ext.items():
     #           f.write(key+','+str(value)+'\n')
        json.dump(body_id_ext,open(os.path.join(cwd,'feature_identifiers_Elmer.txt'),'w'))
        
        return(body_id_ext)
    

    # =============================================================================
    # Function: Execute_Solver(MPI=False)
    # =============================================================================
    def Execute_Solver(self,cwd,MPI=False,logFileName = 'elmer_solver_log.txt'):
        from subprocess import call
        
        if MPI == False:
            print("MPI = False")
            call([self.path_dict['elmerSolverPath'] ,"case.sif"])
            
        elif MPI == True:
            print("MPI == True")
            # Check if ELMERSOLVER_STARTINFO exists
            startinfo_filepath = os.path.join(cwd,'ELMERSOLVER_STARTINFO')
            my_file = Path(startinfo_filepath)
            if not my_file.is_file():
                print('Warning - need to create ELMERSOLVER_STARTINFO')
                with open('ELMERSOLVER_STARTINFO', 'w') as f:
                    f.write('case_automate.sif')
                    print('Created ELMERSOLVER_STARTINFO listing case_automate.sif')
            
            cmd = [self.path_dict['mpiExecPath'],"-np","4",self.path_dict['elmerSolverMPIPath'] ]
            print(cmd)
            
            logPath= os.path.join(cwd,'log')
            
            # Make a file with the direct command to be executed for command prompt (for debugging)
            with open(os.path.join(logPath,'direct_cmd.txt'),'w') as handle:
                string = ' '.join([str(item) for item in cmd])
                handle.write(str(string))
                
            output = self.Execute_CMD(cmd)
            

            with open(os.path.join(logPath,logFileName),'w') as filehandle:
                filehandle.writelines("%s\n" % place for place in output)
                
    
    def UpdateSIF(self,dfActive,body_id,cwd,filename = 'case_automate.sif'):
            sif_filepath = os.path.join(cwd,filename)
            
            my_file = Path(sif_filepath)
            if my_file.is_file():
                file1 = open(my_file,"r")
            else:
                print('\n\Error - need to place {} in working directory\n\n'.format(filename))
                quit()
            f1 = file1.readlines()
            Variable_Info = []
            #Read in the file appending into variable_info
            for item in f1:
                Variable_Info.append(item)
            file1.close()
            
            file = dfActive['Filename']
            Variable_Info[0] = '$ Output_Name = "{}.vtu"\n'.format(file)
            
            Variable_Info[2] = '$ airBody = {}\n'.format(body_id['airBody']['volume'])
            Variable_Info[3] = '$ coreBody = {}\n'.format(body_id['coreBody']['volume'])
            import math
            if not math.isnan(body_id['concentratorBody']['volume']):
                Variable_Info[4] = '$ concentratorBody = {}\n'.format(body_id['concentratorBody']['volume'])
            else:
                Variable_Info[4] = ''
            with open(os.path.join(cwd,"case_automate.sif"),'w') as f:
                for value in Variable_Info:
                    f.write(value)
                
            

    # =============================================================================
    # function - Execute_CMD(cmd,use_end_string=True,end_string='ELMER SOLVER 
    # FINISHED AT')
    #
    # Description - pass in command and executed using subprocess.
    # The output is printed live, with the output returned as a string array.
    #
    # Note - To handle overflow conditions, uses for loop and allows custom
    #        string to be provided to allow exit
    # =============================================================================
    def Execute_CMD(self,cmd,use_end_string=True,end_string='ELMER SOLVER FINISHED AT'):
        import subprocess
        
        process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=None,bufsize=1)
        items = []
          
        
        for line in iter(process.stdout.readline, b''):
            
            item = str(line.decode('utf-8'))
            items.append(item)
            print(item)
            
            if ((use_end_string) & (not item.find(end_string) == -1)):
                
                return(items)
                break
    
        return(items)
    
# =============================================================================
#     
# =============================================================================
    def extract_runtime_from_fea(self,cwd,logFileName="std_mesh_log.txt"):
        runtime = []
        logPath = os.path.join(cwd,'log')
        file1 = open(os.path.join(logPath,logFileName),"r")
        f1 = file1.readlines()
        
        #Read in the file appending into variable_info
        str_subset = 'SOLVER TOTAL TIME(CPU,REAL):'
        for item in f1:
            line_in_var = item
            if (line_in_var.find(str_subset) >= 0):
                runtimeline = line_in_var.replace(str_subset,'')
                for item in runtimeline.split(' '):
                    try:
                        runtime = float(item)
                    except:
                        pass
        return(runtime)
    
# =============================================================================
# 
# =============================================================================
    def extract_finishdate_from_fea(self,cwd,logFileName="std_mesh_log.txt"):
        logPath = os.path.join(cwd,'log')
        file1 = open(os.path.join(logPath,logFileName),"r")
        f1 = file1.readlines()
        
        #Read in the file appending into variable_info
        str_subset = 'ELMER SOLVER FINISHED AT:'
        for item in f1:
            line_in_var = item
            if (line_in_var.find(str_subset) >= 0):
                runtimeline = line_in_var.replace(str_subset,'')
                runtimeline = runtimeline.replace('\n','')[1:]
        return(runtimeline)
    
# =============================================================================
#     
# =============================================================================
if __name__ == "__main__":
    
    #from ReadandConfigureFEA import readProgramPathsCSV
    elmerFUNC = ClassElmer()
    #if 'self.path_dict' not in locals():
    #    self.path_dict = readProgramPathsCSV('ElmerFEAFilePaths.csv')
        
    elmerFUNC.convertToElmerMesh(os.getcwd())  
    
    elmerFUNC.extract_ids_from_log(os.getcwd(),'elmer_grid_log.txt')    
    
    elmerFUNC.Execute_Solver(os.getcwd(),MPI=True)
    
    
