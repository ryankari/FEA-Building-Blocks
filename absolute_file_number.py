# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 12:21:50 2021

@author: RKari
"""
#XXX-YYYYYYYY-ZZZZ
#XXX refers to project_type
#YYYYYYYY refer to date file recorded
#ZZZZ refers to increment on the particular day

from datetime import date
import re
import json
import os
    
# =============================================================================
#     
# =============================================================================
def file_handling(filename):
    
    from pathlib import Path
    today = date.today()
    print(filename)
    my_file = Path(filename)
    
    if ( my_file.is_file() ):
        if (os.path.getsize(filename) != 0):
            #File exists and is not empty
            print('{} exists'.format(my_file.name))
            
            file_numbers = json.load(open(filename))
        else:
            #File exists and is empty
            print('{} empty'.format(my_file.name))
            default = {'new':'new-' + today.strftime("%m%d%Y") + '-0000'}
            json.dump(default,open(filename,'w'))
            file_numbers = json.load(open(filename))
            print('Setting default')
            
    else:
        #File does not exist. Check if folder exists
        
        if my_file.is_dir():
            print('Directory does not exist - Need to create directory')
            return(0)
        
        #File does not exist but folder does. Create a new file with default entry
        print('{} does not exist - creating'.format(my_file.name))
        default = {'new':'new-' + today.strftime("%m%d%Y") + '-0000'}
        json.dump(default,open(filename,'w'))
        file_numbers = json.load(open(filename))
        
    return(file_numbers)

# =============================================================================
# 
# =============================================================================
def update_file_designator(project_type='R&D',read_or_increment = 'read',
    filename = r'C:\Test\absolute_file_number.txt'):
    """
    Allows inputs of read, increment, and real all
    
    Parameters
    ----------
    project_type : string, optional
        DESCRIPTION. The default is 'R&D'. Any string can be provided.
    read_or_increment : TYPE, optional
        DESCRIPTION. The default is 'read'. 'increment', and 'read all' options

    Returns
    -------
    absolute_file_number string

    """


    file_numbers = file_handling(filename)
    today = date.today()
      
       
    if project_type in file_numbers:
        var =  re.split('-+|\n',file_numbers[project_type])
        
        # If the date matches then increment the post-fix
        if (var[1] == today.strftime("%m%d%Y")):
            var[2] = int(var[2])+1
            var[2] = "{:04d}".format(var[2])
            new_item = '-'.join(var)  
            output_item = (re.sub("-$","\n",new_item))
            file_numbers[project_type] = output_item
        else: #If the date does not match
            var[1] = today.strftime("%m%d%Y")
            var[2] = str('0000')
            new_item = '-'.join(var)  
            output_item = (re.sub("-$","\n",new_item))
            file_numbers[project_type] = output_item
    else:
        output_item = project_type + '-' + today.strftime("%m%d%Y") + '-0000'
        file_numbers[project_type] = output_item
            
    if read_or_increment == 'increment':    
        json.dump(file_numbers,open(filename,'w'))
        
    if read_or_increment == 'read all':
        for item in file_numbers:
            print(item,' -  ',file_numbers[item])
    
    return(output_item)



if __name__ == "__main__":
    output = update_file_designator('test2','read',r'C:\Test\absfile.txt')
    print(output)