#-*- coding: utf-8 -*-
#=============================================================================#
#   DESCRIPTION:  Extracte needed data from .scf files of all completed structures. 
#
#       OPTIONS:  Python libraries : xlrd, xlwt, xlutils, pymatgen
#
#  REQUIREMENTS:  ---
#
#         NOTES:  ---
#        AUTHOR:  Ma Huan
#         EMAIL:  578113120@qq.com
#       LICENCE:  GPL version 2 or upper
#       CREATED:  2019-10-31
#       UPDATED:  
#=============================================================================#

import os
import math
import subprocess

############# as a parser lib, no need to import these libs. 2020.5.9 liuxiaotong

# import xlrd,xlwt,xlutils
# from xlutils.copy import copy
# from pymatgen.core.structure import Structure
# from pymatgen.core.periodic_table import Element, Specie

def load_structure(struct_filename):
    """
    Load structure from a structure file.
     
    Args:
        struct_filename(str)
    """
    struct = Structure.from_file(struct_filename)
    return struct

def get_dirlist(path):
    """
      Return the list of all folders.
      
    """ 
    alllist=os.listdir(path)
    dirlist = []
    for i in alllist:
        tmp_path = os.path.join(path, i)
        if os.path.isdir(tmp_path):
            dirlist.append(i)
    return dirlist

def get_ciflist(path):
    """
      Return the list of all .cif files.
      
    """ 
    alllist=os.listdir(path)   
    ciflist = [i for i in alllist if '.cif' == i[-4:]] 
    return ciflist

def get_namelist(ciflist):    
    """
      Return the list of names from all .cif files.
      
    """ 
    namelist = [i[:-4] for i in ciflist]
    return namelist

def get_wien2kcaldir_path(phase, wien2kcaldir_name):
    """
      Return the path of the folder that performs wien2k calculations.
      
    """ 
    wien2kcaldir_path=os.path.join(os.getcwd(), phase, "struc", wien2kcaldir_name)
    return wien2kcaldir_path

def get_ciffile_path(phase, wien2kcaldir_name):
    ciffile_name = wien2kcaldir_name + ".cif"
    ciffile_path = os.path.join(os.getcwd(), phase, "struc", ciffile_name)   
    return ciffile_path

def get_structfile_path(phase, wien2kcaldir_name):
    structfile_name = wien2kcaldir_name + ".struct"
    structfile_path = os.path.join(os.getcwd(), phase, "struc", wien2kcaldir_name, "calculated_results", structfile_name)   
    return structfile_path
    
def get_scffile_path(phase, wien2kcaldir_name):
    scffile_name = wien2kcaldir_name + ".scf"
    scffile_path = os.path.join(os.getcwd(), phase, "struc", wien2kcaldir_name, "calculated_results", scffile_name)   
    return scffile_path

def get_all_structure_and_struct_dir():
    phaselist = get_dirlist(os.getcwd())
    all_structure = {}
    all_struct_dir = {}
    for phase in phaselist:
        struc_path = os.path.join(os.getcwd(), phase, "struc") 
        ciflist = get_ciflist(struc_path)
        namelist = get_namelist(ciflist)
        all_structure[phase] = namelist
        struct_dirlist = get_dirlist(struc_path)
        all_struct_dir[phase] = struct_dirlist
    return all_structure, all_struct_dir

def get_completed_and_unfinished_structure():
    completed_structure = {}
    unfinished_structure = {}
    all_structure, all_struct_dir = get_all_structure_and_struct_dir()
    for phase in all_struct_dir.keys():
        completed_structure[phase] = []
        unfinished_structure[phase] = []
        for struct_dir in all_struct_dir[phase]:
            wien2kcaldir_path = get_wien2kcaldir_path(phase, struct_dir)
            if "wien2k.out" in os.listdir(wien2kcaldir_path):
                wien2kout_path = os.path.join(wien2kcaldir_path,"wien2k.out")  
                check_cvg_cmd = "grep 'stop'" + " " + wien2kout_path
                check_cvg_output = subprocess.getoutput(check_cvg_cmd)
                if (check_cvg_output != '') and ("error" not in check_cvg_output) and ("No" not in check_cvg_output):
                    completed_structure[phase].append(struct_dir)
                    save_needed_files(phase, struct_dir)
                if (check_cvg_output != '') and (("error" in check_cvg_output) or ("No" in check_cvg_output)):
                    unfinished_structure[phase].append(struct_dir)
                check_cvg_cmd = "grep 'CONVERGED'" + " " + wien2kout_path
                check_cvg_output = subprocess.getoutput(check_cvg_cmd)
                if (check_cvg_output != '') and ("NOT CONVERGED" in check_cvg_output):
                    unfinished_structure[phase].append(struct_dir)                
            if "wien2k.log" in os.listdir(wien2kcaldir_path):
                wien2klog_path = os.path.join(wien2kcaldir_path,"wien2k.log")  
                check_cvg_cmd = "grep 'stop'" + " " + wien2klog_path
                check_cvg_output = subprocess.getoutput(check_cvg_cmd)
                if (check_cvg_output != '') and ("error" not in check_cvg_output) and ("No" not in check_cvg_output):
                    completed_structure[phase].append(struct_dir)
                    save_needed_files(phase, struct_dir)
                if (check_cvg_output != '') and (("error" in check_cvg_output) or ("No" in check_cvg_output)):
                    unfinished_structure[phase].append(struct_dir)
                check_cvg_cmd = "grep 'CONVERGED'" + " " + wien2klog_path
                check_cvg_output = subprocess.getoutput(check_cvg_cmd)
                if (check_cvg_output != '') and ("NOT CONVERGED" in check_cvg_output):
                    unfinished_structure[phase].append(struct_dir)
            if "calculated_results" in os.listdir(wien2kcaldir_path):
                completed_structure[phase].append(struct_dir)
    return completed_structure, unfinished_structure 

def get_Fe_atoms(structfile_path):
    with open(structfile_path,'r') as reader:
        alllines = reader.readlines() 
    Fe_atoms = []   
    for n,line in enumerate(alllines):
        line = [i for i in line.split(' ') if i != '']
        if line[0] == "ATOM":
            serial_number = ""
            for i in line[1]:
                if i in "0123456789":
                    serial_number = serial_number + i
            serial_number = int(serial_number)
        if "Fe" in line[0]:
            Fe_atoms.append(serial_number) 
    return Fe_atoms

def get_MM(scffile_path, Fe_atoms):
    MM = []
    for i in Fe_atoms:
        serial_number = list(str(i))
        while len(serial_number) != 3:
            serial_number.insert(0,'0')
        serial_number = "".join(serial_number)
        search_term = ":MMI" + serial_number
        grep_cmd = "grep '%s' %s | tail -n 1 | awk \'{print $8}\'" %(search_term, scffile_path)
        out = subprocess.getoutput(grep_cmd)
        MM.append(out)
    return MM
        
def get_HFF(scffile_path, Fe_atoms):
    HFF = []
    for i in Fe_atoms:
        serial_number = list(str(i))
        while len(serial_number) != 3:
            serial_number.insert(0,'0')
        serial_number = "".join(serial_number)
        search_term = ":HFF" + serial_number
        grep_cmd = "grep '%s' %s | tail -n 1 | awk \'{print $5}\'" %(search_term, scffile_path)
        out = subprocess.getoutput(grep_cmd)
        HFF.append(out)
    return HFF

def get_ETA(scffile_path, Fe_atoms):
    ETA = []
    for i in Fe_atoms:
        serial_number = list(str(i))
        while len(serial_number) != 3:
            serial_number.insert(0,'0')
        serial_number = "".join(serial_number)
        search_term = ":ETA" + serial_number
        grep_cmd = "grep '%s' %s | tail -n 1 | awk \'{print $5}\'" %(search_term, scffile_path)
        out = subprocess.getoutput(grep_cmd)
        ETA.append(out)
    return ETA

def get_EFG(scffile_path, Fe_atoms):
    EFG = []
    for i in Fe_atoms:
        serial_number = list(str(i))
        while len(serial_number) != 3:
            serial_number.insert(0,'0')
        serial_number = "".join(serial_number)
        search_term = ":EFG" + serial_number
        grep_cmd = "grep '%s' %s | tail -n 1 | awk \'{print $4}\'" %(search_term, scffile_path)
        out = subprocess.getoutput(grep_cmd)
        #print(out)
        EFG.append(out)
    return EFG

def get_RTO(scffile_path, Fe_atoms):
    RTO = []
    for i in Fe_atoms:
        serial_number = list(str(i))
        while len(serial_number) != 3:
            serial_number.insert(0,'0')
        serial_number = "".join(serial_number)
        search_term = ":RTO" + serial_number
        grep_cmd = "grep '%s' %s | tail -n 1 | awk \'{print $6}\'" %(search_term, scffile_path)
        out = subprocess.getoutput(grep_cmd)
        #print(out)
        RTO.append(out)
    return RTO

def open_excel(file_name):
    """
      Open a Excel file, and return readworkbook and writeworkbook. 
    
      arguments:
        file_name(str)
    
      return:
        readworkbook,writeworkbook
    """
    # Open Excel file with read and write permission.
    readworkbook = xlrd.open_workbook(file_name)
    writeworkbook = copy(readworkbook)
    # Print all sheet names.
    #print(readworkbook.sheet_names())
    return readworkbook, writeworkbook

def extract_data(completed_structure):
    all_formula = []
    all_struct = []
    all_Fe = []
    all_S = []
    all_serial_number = []
    all_MM = []
    all_HFF = []
    all_ETA = []
    all_EFG = []
    all_RTO = []
    for phase in completed_structure.keys():
        print("\n\n-------------------------%s-------------------------\n\n" %phase)
        for struct_dir in completed_structure[phase]:
            ciffile_path = get_ciffile_path(phase, struct_dir)
            structfile_path = get_structfile_path(phase, struct_dir)
            scffile_path = get_scffile_path(phase, struct_dir)
            structure = load_structure(ciffile_path)
            Fe_atoms = get_Fe_atoms(structfile_path)
            serial_number = ["Fe%s" %value for value in Fe_atoms]             
            MM = get_MM(scffile_path, Fe_atoms)
            HFF = get_HFF(scffile_path, Fe_atoms)
            ETA = get_ETA(scffile_path, Fe_atoms)
            EFG = get_EFG(scffile_path, Fe_atoms)
            RTO = get_RTO(scffile_path, Fe_atoms)
            
            for i in range(0,len(Fe_atoms)):
                all_formula.append(phase)
                all_struct.append(struct_dir)
                all_Fe.append(structure.composition["Fe"])
                all_S.append(structure.composition["S"])  
                all_serial_number.append(serial_number[i])          
                all_MM.append(MM[i])           
                all_HFF.append(HFF[i]) 
                all_ETA.append(ETA[i])            
                all_EFG.append(EFG[i])     
                all_RTO.append(RTO[i])    
                
        all_formula.append("")
        all_struct.append("")        
        all_Fe.append("") 
        all_S.append("")
        all_serial_number.append("")                     
        all_MM.append("")
        all_HFF.append("")
        all_ETA.append("")
        all_EFG.append("")
        all_RTO.append("")         
            
    openexcel = open_excel("extracted_data.xls")
    readsheet = openexcel[0].sheet_by_name("MES")
    writesheet = openexcel[1].get_sheet("MES")
    writesheet.write(0, 0, "phase") 
    writesheet.write(0, 1, "structure")           
    writesheet.write(0, 2, "Fe")
    writesheet.write(0, 3, "S")
    writesheet.write(0, 4, "serial number")
    writesheet.write(0, 5, "MM")
    writesheet.write(0, 6, "HFF") 
    writesheet.write(0, 7, "ETA") 
    writesheet.write(0, 8, "EFG")
    writesheet.write(0, 9, "RTO")     
    for n,value in enumerate(all_formula):
        writesheet.write(n+1, 0, value)   
        writesheet.write(n+1, 1, all_struct[n])             
        writesheet.write(n+1, 2, all_Fe[n])
        writesheet.write(n+1, 3, all_S[n])
        writesheet.write(n+1, 4, all_serial_number[n])
        writesheet.write(n+1, 5, all_MM[n])
        writesheet.write(n+1, 6, all_HFF[n]) 
        writesheet.write(n+1, 7, all_ETA[n]) 
        writesheet.write(n+1, 8, all_EFG[n])
        writesheet.write(n+1, 9, all_RTO[n])     
    openexcel[1].save("extracted_data.xls")
    
def calculate_ISandQS():
    openexcel = open_excel("extracted_data.xls")
    readsheet = openexcel[0].sheet_by_name("MES")
    writesheet = openexcel[1].get_sheet("MES")
    writesheet.write(0, 10, "IS")
    writesheet.write(0, 11, "QS")     
    MM = readsheet.col_values(5)[1:]
    HFF = readsheet.col_values(6)[1:]
    ETA = readsheet.col_values(7)[1:]
    EFG = readsheet.col_values(8)[1:]
    RTO = readsheet.col_values(9)[1:]
    for i in range(0,len(MM)):
        if RTO[i] == '' or EFG[i] == '' or ETA[i] == '':
            pass
        else:
            IS = -0.291 * ( float(RTO[i]) - 15309.82 )
            QS = ( 8 * float(EFG[i]) * pow(1 + ( pow(float(ETA[i]), 2) / 3 ), 0.5 ) ) / 48.075
            writesheet.write(i+1, 10, IS)
            writesheet.write(i+1, 11, QS)
    openexcel[1].save("extracted_data.xls")       

if __name__ == '__main__':
    completed_structure, unfinished_structure = get_completed_and_unfinished_structure()               
    extract_data(completed_structure)
    calculate_ISandQS()
    print("Done!")                    
