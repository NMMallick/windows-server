import math
from posixpath import abspath
import struct
import os
import struct
import math
import argparse


def generateImports(file):
    file.write(f'from msg import msg\n\n')

def generateClassHeader(file, name):
    file.write(f'class {name}(msg):\n')
    file.write(f'\tdef __init__(self):\n')
    file.write(f'\t\tsuper().__init__()\n')
    file.write(f'\t\tself.__vars__ = []\n')

def generateClassVariables(file, vars):
    for var in vars:
        if '[]' not in var[0]:
            file.write(f"\t\tself.{var[1]} = None\n")
        else:
            file.write(f"\t\tself.{var[1]} = []\n")
        file.write(f'\t\tself.__vars__.append(self.{var[1]})\n')

    for var in vars:
        file.write(f'\t\tself.__data_types__.append("{var[0]}")\n')
    file.write('\n\n')

def generateSerializeFunc(file, vars):
    file.write('\tdef serialize(self):\n')
    for i, var in enumerate(vars):
        file.write(f'\t\tself.__vars__[{i}] = self.{var[1]}\n')
    file.write('\t\treturn self.__serialize__(self.__vars__)\n\n')

def generateDeserializeFunc(file, vars):
    file.write('\tdef deserialize(self, buffer):\n')
    file.write('\t\tself.__deserialize__(buffer, self.__vars__)\n')

    for i, var in enumerate(vars):
        file.write(f'\t\tself.{var[1]} = self.__vars__[{i}]\n')


def getVars(msgName, input, output):

    # contents = os.listdir('.')
    # msg_dir = 'msgs'
    # msg_files = os.listdir(f'./{msg_dir}/') if msg_dir in contents else None
    msg_dir = os.path.abspath(input)
    msg_files = os.listdir(msg_dir)

    out_dir = os.path.abspath(output)

    # msg_files = os.listdir(out_dir)
    if msg_files != None:
        for msg_file in msg_files:

            if '.msg' not in msg_file:
                continue

            ## Open a .msg file located in the given dir
            f = open(f'{msg_dir}/{msg_file}')
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
                file = open(f"{out_dir}/{msgName}.py", 'w')
                generateImports(file)
                generateClassHeader(file, msg_file.split('.msg')[0])
                generateClassVariables(file, vars)
                generateSerializeFunc(file, vars)
                generateDeserializeFunc(file, vars)
                file.close()

if __name__ == '__main__':

    ## Parse Inputs
    parser = argparse.ArgumentParser(description="Message generating script for use in the github.com/NMMallick/windows-server repository")
    parser.add_argument('input_path', type=str,
                        help="input path to *.msg file(s)")
    parser.add_argument('output_path', type=str,
                        help="Output path where the generated message is written to, typically an include location")
    parser.add_argument('msg_name', type=str,
                        help="Library or module name to be generated")
    args = parser.parse_args()

    ## Generate class
    getVars(args.msg_name, args.input_path, args.output_path)


