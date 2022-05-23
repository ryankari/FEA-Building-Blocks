# -*- coding: utf-8 -*-
"""
Created on Fri May 13 06:07:16 2022

@author: RKari
"""

import numpy as np
import pandas as pd
import pyvista as pv


ColumnNames=['Pos X','Pos Y','Pos Z','Field X','Field Y','Field Z']


class classVTUImport:
    
    
    def ReadVTUArray(self,Filename):

            if type(Filename) is not list:
                Filename = [Filename]
            
            meshArray = []
            for index,File in enumerate(Filename):
                meshArray.append(pv.read(File))
            
            return(meshArray)
    
    
    # =============================================================================
    #     # Read data from VTU file returning position and field data in pandas data frame
    # =============================================================================
    def ReadVTUtoPandas(self,Filename):
    
            print('In ReadVTUFile \n{}\n'.format(Filename))
            self.PDData =  pd.DataFrame({})
    
            #FEADataOut = pd.DataFrame(columns = self.ColumnNames)
            if type(Filename) is not list:
                Filename = [Filename]
    
            for index,File in enumerate(Filename):
                mesh = pv.read(File)
                #Read in coordinates
                PointData = mesh.points
                #Read in field data
                FieldData = mesh.point_arrays['magnetic field strength']
    
                df1 = pd.DataFrame(data=np.append(PointData,FieldData,axis=1), columns=ColumnNames)
                for item in df1.items():
                    df1[item[0]] =  df1[item[0]].fillna(value = df1[item[0]].iloc[0])
    
                df1['FileOrder'] = index
                ArrayNames = mesh.array_names
    
                if 'GeometryIds' in ArrayNames:
                    GeometryIdsData = pd.DataFrame({'GeometryIds':mesh.cell_arrays['GeometryIds']})
                else:
                    GeometryIdsData = []
    
                print('Shape of read data = ',df1.shape)
                print('Columns of read data = ',df1.columns.values)
    
                #Check if exists
                if 'FileOrder' in self.PDData:
                    print('Variable exists')
                    PDDataTemp = self.PDData
                    self.PDData = pd.concat([PDDataTemp,df1],ignore_index=True)
                    #PDData = PDData.set_index(['FileOrder'],drop=False)
                    print(self.PDData.shape)
                else:
                    print('Variable not yet populated')
                    self.PDData = df1
                    self.PDData['FileOrder'] = index
    
            return(self.PDData,GeometryIdsData)
    
