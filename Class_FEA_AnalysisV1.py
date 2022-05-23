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
        
from Class_VTU_Functions import classVTUImport
VTU = classVTUImport()

from Class_curve_Estimation import curveEstimation
CE = curveEstimation()

class ClassFEAAnalysis:
    

# =============================================================================
#         
# =============================================================================
      def process_vtu_data(self,cwd,parameters_dict):
        """
          
          Parameters
          ----------
          parameter_file_name : string, optional
              DESCRIPTION. The name of the spreadsheet containing the parameter values
          filepath : string, optional
              DESCRIPTION. The string of the filepath containing the VTU files

          Returns
          -------
          None.

          """  
        
        df_all = pd.read_excel(parameters_dict['path'])  
        
        
        vtufullfiles = []
        vtufiles = []
        var1 = []
        var2 = []
        

        vtuPath = os.path.join(cwd,'output')
        for item in df_all.iterrows():
            # Extract each pvtu file associated with the test in the spreadsheet
            # Alternatively, can extract from SQL
            vtufiles.append(item[1]['Filename'] + '_t0001.pvtu')
            vtufullfiles.append(os.path.join(vtuPath,item[1]['Filename'] + '_t0001.pvtu'))
            
            # Extract values associated with each file for analysis
            var1.append(float(item[1]['Concen_Z_[gmsh]']))
            var2.append(float(item[1]['Conce2_diam_[gmsh]']))
        
        var1 = np.array(var1)
        var2 = np.array(var2)
        # Store each mesh into a dictionary
        meshDict = VTU.ReadVTUArray(vtufullfiles)
        
        # Set endpoints to sample data over a line
        a = [-.050, .02, 0]
        b = [ .050, .02, 0]
        
        if len(meshDict) != len(vtufiles):
            print('Warning - same file name likely present in multiple rows')
            
        cE = curveEstimation()
        outputValues = []
        dfArray = pd.DataFrame()
        # Sample over the line and store results in data frame
        
        for index,mesh in enumerate(meshDict):
            output = mesh.sample_over_line(a,b,resolution=100)
            df = pd.DataFrame({'Pos':output.points[:,0],'FieldZ':output.point_arrays['magnetic field strength'][:,2],\
                               'Width':float(var1[index]),'Radius':float(var2[index]),'FileOrder':index  })
            dfArray = pd.concat((dfArray,df))
            #Extract narrow range of results and fit a curve to extract point at specific location
            
            inspection_pt = 0
            
            output = cE.returnPts(df, inspection_pt,fit ='2nd order',inputRange=[-0.005,0.005]) 
            outputValues.append(output)
        outputValues = np.array(outputValues)    
        
        
        ####-------------------------------------------------------------------
        # Create first plot
        ####-------------------------------------------------------------------
        for item in dfArray.groupby(by='FileOrder'):
            plt.plot(item[1]['Pos'],item[1]['FieldZ'])     
            
        plt.legend(var1)
        
    
        
        # Make this interesting. Compute the mass for each permutation
        npArray = np.array((outputValues,var1,var2)).transpose()
        massArray = []
        density_steel = 7.8 /1000 #g/mm**3
        for item in df_all.iterrows():
            
            mass_cube = density_steel*item[1]['Concen_X_[gmsh]']*item[1]['Concen_Y_[gmsh]']*item[1]['Concen_Z_[gmsh]'] 
            mass_cylinder = float(item[1]['Conce2_diam_[gmsh]'])**2*np.pi/4
            mass = mass_cube - mass_cylinder
            massArray.append(mass)
        massArray = np.array(massArray)
        
        # Assemble matrix of [magnetic field, width, diameter, mass]
        npArray = np.array((outputValues,var1,var2,massArray)).transpose()    
        
        # Use a fit function of theta0 + theta1* width + theta2*radius + theta3*radius**2
        # Solve using least squares
        theta,pcovA = curve_fit(self.sur_function,(npArray[:,1],npArray[:,2]),npArray[:,0])
        
        # Configure a grid over the range of values we solved for
        widthArray = np.arange(min(npArray[:,1]),max(npArray[:,1]),1)
        radiusArray = np.linspace(min(npArray[:,2]),max(npArray[:,2]),len(widthArray))
        
        xx,yy = np.meshgrid(widthArray,radiusArray,sparse=True)
        
        # Compute the mass for each iterated solution
        mm = 7.8/1000*item[1]['Concen_X_[gmsh]']*item[1]['Concen_Y_[gmsh]']*xx - yy**2*np.pi/4
        
        # Compute our fit function at each point
        z = self.sur_function((xx,yy),*theta)
        
        
        ####-------------------------------------------------------------------
        # Create second plot
        ####-------------------------------------------------------------------
        plt.figure(2)
        plt.subplot(1,2,1)
        plt.contourf(widthArray,radiusArray,z,levels=50,cmap=cm.Greys)
        plt.colorbar()
        plt.xlabel('Width [mm]')
        plt.ylabel('Radius [mm]')
        plt.title('Magnetic field versus \nwidth and radius')
        
        plt.subplot(1,2,2)
        plt.contourf(widthArray,radiusArray,z/mm,levels=50,cmap=cm.Blues)
        plt.title('Magnetic field per unit mass \nversus width and radius')
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
    Analysis = ClassFEAAnalysis()
    
    parameters_subdir = 'parameters'
    parameters_filename = 'Simulation_A.xlsx'
    cwd = os.getcwd()
    parameters_dict = {'filename':parameters_filename,\
               'filepath':os.path.join(cwd,parameters_subdir),\
               'path':os.path.join(os.path.join(cwd,parameters_subdir),parameters_filename)}
        
    Analysis.process_vtu_data(os.getcwd(),parameters_dict)
    
