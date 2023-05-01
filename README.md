# FEA Building Blocks
### Installation
When originally uploaded, I neglected to include a requirements.txt and information about what packages I was using. After pulling it a year later, I was surprised that there were already multiple problems caused by changes in the packages. For anyone rather new to Python, I'd first recommend using a virtual environment to install Python and all the packages into. There are many ways to do this, but with Anaconda step-by-step instructions are:

#Using Conda Prompt, Create a new virtual Environment by:

conda create --name NewEnvName

#Activate the NewEnvName with

activate NewEnvName

#I used Python 3.10.10, and did notice that there were already issues with Python 3.11. Install python 3.10.10 into the virtual environment with:

conda install python==3.10.10

#Install the packages within requirements.txt using pip

conda install pip

pip install -r "path to requirements.txt"

#If errors, the environment can be removed with:

conda remove -n ENV_NAME --all


In regards to IDEs, I typically work with Spyder but there are many options, including the command window or Anaconda Prompt. Spyder can be installed into the virtual environment as described by:

https://docs.spyder-ide.org/current/installation.html

To install in short

conda create -c conda-forge -n spyder-env spyder

To run the code as a demo, simply execute ExecuteFEA.py

### Summary
This serves as an example of a full FEA package that I've hatched together for personal projects, in which I have developed and use the methods presented frequently as part of my day job. This is built using: ELMER FEM to act as the solver, GMSH and the API specifically to act as the geometry editor and mesh generation tool, and then PYVista to extract data from the VTU file (standard file type used to store the FEA solution). For my uses which I suspect may be common, an FEA analysis is more than just a single solution. It is often used to provide insight into how changes in geometry impact a very finite vector magnitude measured within a result. For example, I want to know the magnetic field in a particular location for a given input an local geometry. Digging deeper as to why I want to know that, perhaps I want the biggest magnetic field possible while using the lightest shape (or most inexpensive to manufacture, or least sensitive to tolerances). 

It's for this reason parametric modeling makes commercial packages so powerful. These packages provide a means of defining variables to control geometries and then run a parametric sweep of tests to understand how the output varies with the input. However, I’ve still found that I often export the results of these tests for further analysis within Python, such as to carry out an optimization using a cost function that considers external data. 

This project puts together this full suite with Open Source tools. This presents currents and fields, but can be modified for stress and strain, heat transfer, fluid flow etc. I often automate the full creation of the full *.sif file (rather than just appending the output file name and body information), however always begin by ‘hacking’ it as a text file as I work through the details of the FEA solution. This sif file can easily be changed to whatever physics need to be solved. To help with this debugging stage, a file (direct_cmd.txt) is created showing the command line that can be executed directly within the command prompt. 
In regards to requirements, I have Elmer 9.0 installed and use MPI. I have not tested other releases lately. 

![image](https://user-images.githubusercontent.com/73919562/169894493-d8f4c04e-4328-447f-92d2-e75fbe337ba1.png)

The figure below is from the simple example of current conducted within a wire shown in Building Block Study 2.
![image](https://user-images.githubusercontent.com/73919562/170806725-7c2d7cc3-cfb2-404b-ad76-78aefabfaa84.png)

It can be seen the current from the calculation is in reasonable agreement with the measured value in A/m.

Inspect = 0.003

Uo = 4 * np.pi * 1e-07

B =  Uo * Current/(2 * np.pi * Inspect)

print('Field in Tesla = {} Oe = {} A/m = {}'.format(B,B*10000,B*10000*80))

![image](https://user-images.githubusercontent.com/73919562/170807035-1596630d-1dd1-4c9d-b9dd-21359e1127a5.png)

