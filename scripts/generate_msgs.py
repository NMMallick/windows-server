import math
import struct
import os
import struct
import math

def generateClassHeader(file, name):
    file.write(f'class {name}:\n')
    file.write(f'\tdef __init__(self):\n')

def generateClassVariables(file, vars):
    file.write(f"\t\tself.__serial_data__ = None\n")
    for var in vars:
        if '[]' not in var[0]:
            file.write(f"\t\tself.{var[1]} = None\n")
        else:
            file.write(f"\t\tself.{var[1]} = []\n")

def generateSerializeFunc():
    pass

def generateDeserializeFunc():
    pass

def getVars(moduleName):

    contents = os.listdir('.')
    msg_dir = 'msgs'
    msg_files = os.listdir(f'./{msg_dir}/') if msg_dir in contents else None

    if msg_files != None:
        for msg_file in msg_files:

            if '.msg' not in msg_file:
                continue

            ## Open a .msg file located in the given dir
            f = open(f'./{msg_dir}/{msg_file}')
            vars = []
            for line in f:
                ## Remove any newline characters
                line = line.replace('\n', '')

                ## Split the line in variable type | variable name
                type_var = line.split(' ')
                vars.append((type_var[0], type_var[1]))

                ## Verify that the .msg file is well formated s
                if len(type_var) != 2:
                    print(f'Err: invalid message type in file {msg_file}')
                    exit(-1)

            ## Generate the file and create the class header
            if len(vars) > 0:
                file = open(f"{moduleName}.py", 'w')
                generateClassHeader(file, msg_file.split('.msg')[0])
                generateClassVariables(file, vars)
                file.close()

if __name__ == '__main__':

    getVars('wayside_controller')


