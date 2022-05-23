# -*- coding: utf-8 -*-
"""
Created on Wed May 18 09:33:03 2022

File: Class_curve_Estimation.py
@author: Ryan Kari <ryan.j.kari@gmail.com>
Last Modified Date: May 23, 2022
Last Modified by: Ryan Kari

"""




class curveEstimation():
    
    def func1(self,x,a,b):
        return a + b*x 
    
    def func2(self,x,a,b,c):
        return a + b*x + c*x**2    
    
    def func3(self,x, a, b, c, d):
        return a + b*x + c*x**2 + d*x**3
    
    def func4(self,x, a, b, c, d, e):
        return a + b*x + c*x**2 + d*x**3 + e*x**4
    



    def returnPts(self,df,pts,fit = '1st order',inputRange = [-0.01,0.01],channelNames = ['Pos','FieldZ']):
        """
        
        Parameters
        ----------
        df : data frame
            General data frame. The 'X' and 'Y' are specified in channelNames.
        pts : float or np.array 
            Points over which fitted points will be returned at based on fitting data
        fit : string
            Choice of fit order. The default is '1st order'.
        inputRange : list of floats or np array
            DESCRIPTION. The default is [-0.01,0.01]. This is the range of X 
            values over which poly will be fit
        channelNames : list of strings
            The default is ['Pos','FieldZ']. This is used to extract X and Y from df

        Returns
        -------
        Output values at specific points.

        """
        from scipy.optimize import curve_fit
    

        selectedData = df[df[channelNames[0]].between(inputRange[0], inputRange[1], inclusive=False)]
        xdata = selectedData[channelNames[0]].values
        ydata = selectedData[channelNames[1]].values
        
        if fit == '1st order':
            popt, pcov = curve_fit(self.func1, xdata, ydata)
            outputValue = self.func1(pts, *popt)
        if fit == '2nd order':
            popt, pcov = curve_fit(self.func2, xdata, ydata)
            outputValue = self.func2(pts, *popt)
        if fit == '3rd order':
            popt, pcov = curve_fit(self.func3, xdata, ydata)
            outputValue = self.func3(pts, *popt)
        if fit == '4th order':
            popt, pcov = curve_fit(self.func4, xdata, ydata)
            outputValue = self.func4(pts, *popt)
        
        print(outputValue)
        return(outputValue)
    
    

    