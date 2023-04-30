# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:06:39 2021

File: Class_gmsh_Functions.py
@author: Ryan Kari <ryan.j.kari@gmail.com>
Last Modified Date: April 29, 2023
Last Modified by: Ryan Kari

"""


import gmsh
import sys
import numpy as np
import os

    
class gmshFunctions:
    
# =============================================================================
# =============================================================================
    def __init__(self):
        
        print("gmshFunctions __init__")

# =============================================================================
#   Extract Parameters from imported           
# =============================================================================
    def extractColumn(self,dfActive,columnName,columnType = 'float'):
        
        if columnType == 'float':
            output = float(dfActive[columnName])       
        elif columnType == 'boolean':
            enableIn = dfActive[columnName]
            enableType = type(enableIn)
            
            if isinstance(enableIn,bool):
                output = enableIn
            else:
                if type(enableIn) == str:
                    output = (enableIn == 'True')
                else:
                    print("Type Warning",type(enableIn),enableType)
        elif columnType == 'string':
            output = dfActive[columnName]
        else :
            output = np.nan
        
        return(output)
        
# =============================================================================
#     startGMSH
# =============================================================================
    def startGMSH(self):
        
        gmsh.initialize(sys.argv)
        gmsh.model.add("electromag space")
        
        # We can log all messages for further processing with:
        gmsh.logger.start()
          
        gmsh.option.setNumber("General.Terminal", 1)
# =============================================================================
#         
# =============================================================================
    def writeMesh(self,cwd):
        # Save file and wrap up
        gmsh.option.setNumber("Mesh.MshFileVersion", 2)
        gmsh.option.setNumber("Mesh.SaveAll",1)
        print('In gmshwrite mesh\n\n\n',cwd,os.getcwd())
        gmsh.write(os.path.join(cwd,"Input_Geometry.msh"))
        
# =============================================================================
#     
# =============================================================================
    def stopGMSH(self,cwd):
            
        # Inspect the log:
        log = gmsh.logger.get()
        print("Logger has recorded " + str(len(log)) + " lines")
        
        gmsh.logger.stop()
        
        logPath = os.path.join(cwd,'log')
        with open(os.path.join(logPath,'gmsh_log.txt'),'w') as filehandle:
            filehandle.writelines("%s\n" % place for place in log)  
        
        gmsh.finalize()


# =============================================================================
# 
# =============================================================================
    def createCore(self,dfActive,body_id):
        
        tag = int(body_id['coreBody']['volume'])
        print("Core enabled\n\n\n")
        if self.extractColumn(dfActive,columnName = 'Enable_Core_[gmsh]',columnType = 'boolean') == True:
            OD_tag = 42
            ID_tag = 44
            dims = 3
            Length = self.extractColumn(dfActive,'Core_Length_[gmsh]','float')
            OD = self.extractColumn(dfActive,'Core_OD_[gmsh]','float')
            ID = self.extractColumn(dfActive,'Core_ID_[gmsh]','float')
            
            XPos = self.extractColumn(dfActive,'Core_X_[gmsh]','float')
            YPos = self.extractColumn(dfActive,'Core_Y_[gmsh]','float')
            ZPos = self.extractColumn(dfActive,'Core_Z_[gmsh]','float')
            
            print(Length)
            
            if ID == 0: 
               print('ID = 0')
               gmsh.model.occ.addCylinder(-Length/2+XPos, YPos, ZPos, Length, 0, 0, OD/2,tag = tag)
    
            if ID > 0:
               gmsh.model.occ.addCylinder(-Length/2+XPos, YPos, ZPos, Length, 0, 0, OD/2,tag = OD_tag)
               gmsh.model.occ.addCylinder(-Length/2+XPos, YPos,  ZPos, Length, 0, 0, ID/2,tag = ID_tag)
               gmsh.model.occ.cut([(dims,OD_tag)],[(dims,ID_tag)],tag)
             
            gmsh.model.occ.synchronize() 
            
            physical = gmsh.model.addPhysicalGroup(dims, [body_id['coreBody']['volume']])
            gmsh.model.setPhysicalName(dims, physical, "coreBody")
            
            gmsh.model.occ.synchronize()   
            
        return(body_id)
        
        
# =============================================================================
#         
# =============================================================================
    def create_concentrator_study1(self,dfActive,body_id):
        print("create concentrator study1\n")
        tag = int(body_id['concentratorBody']['volume'])
        #print(dfActive['Enable_Concen_[gmsh]'],type(dfActive['Enable_Concen_[gmsh]']))

                
        if  self.extractColumn(dfActive,'Enable_Concen_[gmsh]'):

            if self.extractColumn(dfActive,'Core_Step_[gmsh]','boolean'):
                print("Create concentator from STEP")
                filename = dfActive['Concen_filename_[gmsh]'].values[0]
                z = gmsh.merge(filename)
                
            else:
                print('Create concentrator from geometry\n\n\n\n\n')

                C_X = self.extractColumn(dfActive,'Concen_X_[gmsh]','float')
                C_Y = self.extractColumn(dfActive,'Concen_Y_[gmsh]','float')
                C_Z= self.extractColumn(dfActive,'Concen_Z_[gmsh]','float')

                C_Xpos = self.extractColumn(dfActive,'Concen_Xpos_[gmsh]','float')
                C_Ypos = self.extractColumn(dfActive,'Concen_Ypos_[gmsh]','float')
                C_Zpos = self.extractColumn(dfActive,'Concen_Zpos_[gmsh]','float')
                
                
                gmsh.model.occ.addBox(C_Xpos,C_Ypos, C_Zpos ,\
                                      C_X,C_Y,C_Z, 30)
                    
                gmsh.model.occ.addCylinder(C_Xpos,0, 0, C_X, 0, 0, 4,tag=31)
                radius = self.extractColumn(dfActive,'Conce2_diam_[gmsh]','float')
                gmsh.model.occ.addCylinder(C_Xpos,20, 0,C_X, 0, 0, radius,tag=32)
                gmsh.model.occ.addSphere(C_Xpos, 20, 0, 9,tag=33)
                
                gmsh.model.occ.cut([(3, 30)], [(3,31),(3,32),(3,33)], \
                                    tag = tag,removeObject=True,removeTool=(True))    
                
                    
                    
                gmsh.model.occ.synchronize() 
                dims = 3
                physical = gmsh.model.addPhysicalGroup(dims, [body_id['concentratorBody']['volume']])
                gmsh.model.setPhysicalName(dims, physical, "concentrator")
                
                gmsh.model.occ.synchronize()   

            print('here in create concentrator')    
            return(body_id)
        else:
            print('here in create concentrator2') 
            return(0)

# =============================================================================
#     
# =============================================================================
    def createBoundary(self,dfActive,body_id):
            import math
            # Create sphere representing air
            air_volume_tag = 41
            dims=3
            air_final_tag = int(body_id['airBody']['volume'])
            Bounding_Size = self.extractColumn(dfActive,'Bounding_Size_[gmsh]','float') 
           
            if self.extractColumn(dfActive,'Bounding_Shape_[gmsh]','string') == 'Sphere':
                
                gmsh.model.occ.addSphere(0, 0, 0, radius=Bounding_Size,tag=air_volume_tag)
            elif self.extractColumn(dfActive,'Bounding_Shape_[gmsh]','string') == 'Cylinder':
                gmsh.model.occ.addCylinder(-Bounding_Size/2, 0, 0, Bounding_Size, 0, 0, Bounding_Size/2,tag = air_volume_tag)
                
            core = not math.isnan(body_id['coreBody']['volume'])
            concen = not math.isnan(body_id['concentratorBody']['volume'])
            print('\n\n\n CONCEN ',core,concen)
            if (core == True ) & (concen == False):
                
                gmsh.model.occ.cut([(dims, air_volume_tag)], [(dims,body_id['coreBody']['volume'])], \
                                    tag = air_final_tag,removeObject=True,removeTool=(False))
                    
            if (core == True) & (concen == True):
                gmsh.model.occ.cut([(dims, air_volume_tag)], [(dims,body_id['coreBody']['volume']), \
                                    (dims,body_id['concentratorBody']['volume'])],\
                                        tag = air_final_tag,removeObject=True,removeTool=(False))
            

            
            gmsh.model.occ.synchronize()      
  
            output_air = gmsh.model.getBoundary([(dims,air_final_tag)],combined = False,oriented=False,recursive=False)
            
            print("sphere surface = \n",output_air[0][1],type(output_air[0][1]))
            
            body_id['airBody']['boundary'] = output_air[0][1]
            
            physical = gmsh.model.addPhysicalGroup(dims, [body_id['airBody']['volume']])
            gmsh.model.setPhysicalName(dims, physical, "air")
            
            gmsh.model.occ.synchronize()   
            return(body_id)



# =============================================================================
# 
# =============================================================================
    def setMeshSizes(self,dfActive,body_id):

       dims=3      
       print('setMeshSizes\n')
       #for item in body_id:
       for item in reversed(list(body_id.keys())):   
            if (not np.isnan(body_id[item]['volume'])):
                # If its not NAN or the farSurface, apply a mesh size
                
                output = gmsh.model.getBoundary([(dims,body_id[item]['volume'])],combined = False,oriented=False,recursive=True)  
                
                
                if item == 'coreBody':
                    meshSize = self.extractColumn(dfActive,'MeshSize_Core_[gmsh]','float')
                    print(item,' output = ',output,' mesh size = ',meshSize)
                if item == 'airBody':
                    meshSize = self.extractColumn(dfActive,'MeshSize_Air_[gmsh]','float') 
                    print(item,' output = ',output,' mesh size = ',meshSize)
                if item == 'concentratorBody':
                    meshSize = self.extractColumn(dfActive,'MeshSize_Concen_[gmsh]','float') 
                    print(item,' output = ',output,' mesh size = ',meshSize)
                if item == 'coilBody':
                    meshSize = self.extractColumn(dfActive,'MeshSize_Coil_[gmsh]','float')                 
                    print(item,' output = ',output,' mesh size = ',meshSize)
                    
                gmsh.model.mesh.setSize(output, meshSize)
                gmsh.model.occ.synchronize() 
                gmsh.model.mesh.setSmoothing(dims, body_id[item]['volume'], 4)
                
       gmsh.model.mesh.setOrder(3)
       gmsh.model.occ.synchronize() 
       
       alg2D = self.extractColumn(dfActive,'Algorithm2D_[gmsh]','string') 
       alg3D = self.extractColumn(dfActive,'Algorithm3D_[gmsh]','string') 
       
       algorithm2D = {'MeshAdapt':1,'Automatic':2,'Initial mesh':3,'Delaunay':5,\
                      'Frontal-Delaunay':6,'BAMG':7,'Frontal-Delaunay for Quads':8,\
                          'Packing of Parallelograms':9,'Quasi-structured Quad':11}
           
       gmsh.option.setNumber("Mesh.Algorithm", algorithm2D[alg2D]);
       
       
       algorithm3D = {'Delaunay':1,'Initial Mesh Only':3,'Frontal':4,'MMG3D':7,'Rtree':9,'HXT':10}
       gmsh.option.setNumber('Mesh.Algorithm3D', algorithm3D[alg3D])
       
       gmsh.option.setNumber("Mesh.CharacteristicLengthMin", .01)
       
       gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 10)
       gmsh.option.setNumber("Mesh.ElementOrder",1)
       # Optimize quality of tetrhedral elements
       gmsh.model.mesh.optimize("Netgen")
       gmsh.model.occ.synchronize()
                    
        
# =============================================================================
#   main function with class
# =============================================================================
    def createMesh(self,dfActive,body_id,cwd,view_geo_only=False,view_mesh_only=False):
        """
        

        Parameters
        ----------
        dfActive : data series
            Contains a data series of the active parameters for the test.
        body_id : dict
            Contains the body and boundary information. If defined, this is used
            to create the geometry
        view_geo_only : boolean, optional
            DESCRIPTION. Only view the geometry file
        view_mesh_only : boolean, optional
            DESCRIPTION. Only view the geometry after meshing
        Returns Status
        """

        self.startGMSH()
        
        for item in body_id:
            
            if not np.isnan(body_id[item]['volume']):
                print(item)
                if item == 'coreBody':
                    body_id = self.createCore(dfActive,body_id)
                    
                if item == 'concentratorBody':
                    if  self.extractColumn(dfActive,'Enable_Concen_[gmsh]'):
                        body_id = self.create_concentrator_study1(dfActive,body_id)
                    else :
                        body_id[item]['volume'] = np.nan
                    
                if item == 'coilBody':
                    if  self.extractColumn(dfActive,'Enable_Coil_[gmsh]'):
                        body_id = self.createCoil(dfActive,body_id)
                    else: 
                        body_id[item]['volume'] = np.nan
                    
                if item == 'airBody':
                    body_id = self.createBoundary(dfActive,body_id)
                    
        self.setMeshSizes(dfActive, body_id) 
    
        if (view_geo_only == True):
            if '-nopopup' not in sys.argv:
                 gmsh.fltk.run()
                 return("view only",body_id)
                 
        print("Generating mesh")
        gmsh.model.mesh.generate(3)            
        if (view_mesh_only == True):
            if '-nopopup' not in sys.argv:
                 gmsh.fltk.run()
                 return("view only",body_id)
             
             
        self.writeMesh(cwd)
    
        self.stopGMSH(cwd)
        
        import json
        json.dump(body_id,open(os.path.join(cwd,'feature_identifiers.txt'),'w'))
        
        return("good",body_id)
  

# =============================================================================
#         
# =============================================================================


    

    

    
    

# =============================================================================
#         
# =============================================================================
if __name__ == "__main__":
    
    from Class_read_parameters import ClassReadParameters
    readInstance = ClassReadParameters()
    
    gmshFUNC = gmshFunctions()
    cwd = os.getcwd()
    dfAll = readInstance.read_parameters_from_xls(os.path.join(cwd,'parameters'))          

    
    dfActive =dfAll.iloc[0]

    
    body_id = {'coreBody':{'volume':3},'concentratorBody':{'volume':2},\
               'coilBody':{'volume':np.nan},'airBody':{'volume':1,'boundary':np.nan}}
        
    # Set working directory path relative to Python. Can be specific study path.   
    if '__file__' in globals():   
        cwd = os.path.dirname(__file__)
    else:
        cwd = os.getcwd()
        
    gmshFUNC.createMesh(dfActive,body_id,cwd,view_geo_only=True,view_mesh_only=False)
    

    

    

    
    