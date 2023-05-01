# -*- coding: utf-8 -*-
"""
Created on Thu May 19 21:06:57 2022

File: Class_FEA_AnalysisV1.py
@author: Ryan Kari <ryan.j.kari@gmail.com>
Last Modified Date: May 23, 2022
Last Modified by: Ryan Kari

"""
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib import cm  
import sys

from Class_VTU_Functions import classVTUImport
VTU = classVTUImport()

from Class_curve_Estimation import curveEstimation
CE = curveEstimation()
        
class ClassFEAAnalysis:

    def __init__(self):
          print("ClassFEAAnalysis __init__")   
          
# =============================================================================
#         
# =============================================================================
    def import_vtu_data(self,parameters_dict,importedParams):
        cwd=os.getcwd()
        vtufullfiles = []
        vtufiles = []
        var1 = []
        var2 = []
        var3 = []

        vtuPath = os.path.join(cwd,'output')
        for item in importedParams.iterrows():
            # Extract each pvtu file associated with the test in the spreadsheet
            # Alternatively, can extract from SQL
            vtufiles.append(item[1]['Filename'] + '_t0001.pvtu')
            vtufullfiles.append(os.path.join(vtuPath,item[1]['Filename'] + '_t0001.pvtu'))
            
            # Extract values associated with each file for analysis
            var1.append(float(item[1]['Concen_Z_[gmsh]']))
            var2.append(float(item[1]['Conce2_diam_[gmsh]']))
            var3.append(item[1]['Concen_X_[gmsh]'])
        
        var1 = np.array(var1)
        var2 = np.array(var2)
        # Store each mesh into a dictionary
        meshDict = VTU.ReadVTUArray(vtufullfiles)
        
        if len(meshDict) != len(vtufiles):
            print('Warning - same file name likely present in multiple rows')
            
        return(meshDict)

# =============================================================================
#         
# =============================================================================

    def extractDatafromLine(self,meshDict,a= [-.050, .02, 0],b=[ .050, .02, 0]):
        

        lineOutput = pd.DataFrame({})

        # Sample over the line and store results in data frame
        
        for index,mesh in enumerate(meshDict):
            output = mesh.sample_over_line(a,b,resolution=100)
            dfOutput = pd.DataFrame({'Pt X':output.points[:,0],'Pt Y':output.points[:,1],\
                                     'Pt Z':output.points[:,2],\
                                     'Field X':output.point_data['magnetic field strength'][:,0],\
                                     'Field Y':output.point_data['magnetic field strength'][:,1],\
                                     'Field Z':output.point_data['magnetic field strength'][:,2]})
                
            dfOutput['File'] = index
            lineOutput = pd.concat([lineOutput,dfOutput])
  
        return(lineOutput)
    
# =============================================================================
#         
# =============================================================================
    
    def extractSpecificPts(self,lineOutput,Pts = [0],Field_Dir= 'Field Z'):
        
        cE = curveEstimation()
        ptOutput = pd.DataFrame({})
        
        for item in lineOutput.groupby(by='File'):  
            
            for pt in Pts:

                output = cE.returnPts(item[1], pt,fit ='2nd order',inputRange=[-0.005,0.005],\
                                      channelNames = ['Pt X',Field_Dir]) 
                
                outdf = pd.DataFrame({'Pos':[pt],Field_Dir:[output],'File':item[0]})
                ptOutput = pd.concat([outdf,ptOutput])
                
        return(ptOutput.reset_index(drop=True))
    
# =============================================================================
#         
# =============================================================================   
    def analyzeData(self,importedParams,ptOutput):
        # Make this interesting. Compute the mass for each permutation

        massArray = []
        density_steel = 7.8 /1000 #g/mm**3
        for item in importedParams.iterrows():
             
            mass_cube = density_steel*item[1]['Concen_X_[gmsh]']*item[1]['Concen_Y_[gmsh]']*item[1]['Concen_Z_[gmsh]'] 
            mass_cylinder = float(item[1]['Conce2_diam_[gmsh]'])**2*np.pi/4
            mass = mass_cube - mass_cylinder
            massArray.append(mass)       

         # Assemble matrix of [magnetic field, width, diameter, mass]
        npArray = np.array((ptOutput['Field Z'],importedParams['Concen_Z_[gmsh]'],importedParams['Conce2_diam_[gmsh]'],massArray)).transpose()    
  
        
        # Use a fit function of theta0 + theta1* width + theta2*radius + theta3*radius**2
        # Solve using least squares
        if npArray.shape[0] < npArray.shape[1]:
            print('Not enough parameters for 4th order analysis')
            
         #   for item in lineOutput.groupby(by='File'):
         #       print('\nData collected in File {} = \n'.format(item[0]),item[1][['Width','Radius']].mean())
            return(0,0)
        
        theta,pcovA = curve_fit(self.sur_function,(npArray[:,1],npArray[:,2]),npArray[:,0])
        
        # Configure a grid over the range of values we solved for
        widthArray = np.arange(min(npArray[:,1]),max(npArray[:,1]),1)
        radiusArray = np.linspace(min(npArray[:,2]),max(npArray[:,2]),len(widthArray))
        
        xx,yy = np.meshgrid(widthArray,radiusArray,sparse=True)
        
        # Compute the mass for each iterated solution
        mm = 7.8/1000*item[1]['Concen_X_[gmsh]']*item[1]['Concen_Y_[gmsh]']*xx - yy**2*np.pi/4
        
        # Compute our fit function at each point
        z = self.sur_function((xx,yy),*theta)
        
        contourData = np.array((xx,yy,z,mm),dtype=object)
        return(npArray,contourData)
        
     
# =============================================================================
#         
# =============================================================================
    def createSamplePlots(self,lineOutput,importedParams,contourData):

    
        ####-------------------------------------------------------------------
        # Create first plot
        ####-------------------------------------------------------------------
        for item in lineOutput.groupby(by='File'):
            plt.plot(item[1]['Pt X'],item[1]['Field Z'])     
        plt.legend(importedParams['Concen_Z_[gmsh]'])

        if len(importedParams)<5:
            print('Not enough data to compute remaining figures')
        else:
            ####-------------------------------------------------------------------
            # Create second plot
            ####-------------------------------------------------------------------
            plt.figure(2)
            plt.subplot(1,2,1)
            plt.contourf(contourData[0][0],contourData[1].T[0],contourData[2],levels=50,cmap=cm.Greys)
            plt.colorbar()
            plt.xlabel('Width [mm]')
            plt.ylabel('Radius [mm]')
            
            plt.title('Magnetic field versus \nwidth and radius')
            
            plt.subplot(1,2,2)
            plt.contourf(contourData[0][0],contourData[1].T[0],contourData[2]/contourData[3],levels=50,cmap=cm.Blues)
            plt.title('Magnetic field per unit mass \nversus width and radius')
            plt.colorbar()
     
            ####-------------------------------------------------------------------
            # Create third plot
            ####-------------------------------------------------------------------
            plt.figure(3)
            plt.subplot(1,2,1)
            plt.plot(contourData[0][0].flatten(),contourData[2][:,1].flatten())
            plt.plot(contourData[1].T[0].flatten(),contourData[2][:,1].flatten())
            plt.xlabel('Parameter value [mm]')
            plt.ylabel('Output Value')
            plt.legend(['Parameter A','Parameter B'])
            
            plt.subplot(1,2,2)
            plt.contourf(contourData[0][0],contourData[1].T[0],contourData[2]/contourData[3],levels=50,cmap=cm.Blues)
            plt.title('Output per unit mass')
            plt.xlabel('Width [mm]')
            plt.ylabel('Radius [mm]')
            plt.colorbar()
    

# =============================================================================
#         
# =============================================================================
    def sur_function(self,VAR,a,b,c,d):
          """
          Parameters
          ----------
          VAR : TYPE
              DESCRIPTION.
          a : float
              represents theta0.
          b : float
              represents theta1.
          c : float
              represents theta2.
          d : float
              represents theta3.

          Returns
          -------
          result of equation a+b*Width+c*Radius+d*Radius**2

          """
          Width,Radius = VAR
          z = a+b*Width+c*Radius+d*Radius**2
          return(z)
        
# =============================================================================
#     
# =============================================================================
if __name__ == "__main__":
    
    program_path = os.path.dirname(__file__)
    print(program_path)
    if program_path not in sys.path:
        sys.path.insert(0,program_path)
    
    
    Analysis = ClassFEAAnalysis()
    
    parameters_subdir = 'parameters'
    parameters_filename = 'Simulation_A.xlsx'      
    
    #Analysis.process_vtu_data(parameters_dict)
    # Update to automatically change to desired experimental directory
    if os.path.realpath(program_path) == os.path.realpath(os.getcwd()):
            os.chdir("./Building Block Study 1")
            print('Changing working directory')
    
    
    parameters_dict = {'filename':parameters_filename,\
               'filepath':os.path.join(os.getcwd(),parameters_subdir),\
               'path':os.path.join(os.path.join(os.getcwd(),parameters_subdir),parameters_filename)}       
    print(os.getcwd())    
    print(parameters_dict)
    importedParams = pd.read_excel(parameters_dict['path'])  
    
    meshDict = Analysis.import_vtu_data(parameters_dict,importedParams)
    
    # Set endpoints to sample data over a line
    a = [-.050, .02, 0]
    b = [ .050, .02, 0]
    lineOutput = Analysis.extractDatafromLine(meshDict,a,b)
    
    ptOutput =  Analysis.extractSpecificPts(lineOutput, [0],'Field Z')
    
    npArray,contourData = Analysis.analyzeData(importedParams,ptOutput)
    
    Analysis.createSamplePlots(lineOutput,importedParams,contourData)