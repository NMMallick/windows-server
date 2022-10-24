from copy import deepcopy
import struct


# data = 1000
# my_str = 'my_string'
# p_str = struct.pack(f'{len(my_str)}s', my_str.encode('utf-8'))
# arr = bytearray()

# arr.extend(data.to_bytes(4, 'big'))
# arr.extend(p_str)

# print(arr[2])


#########
# class test_class:
#     def __init__(self):
#         self.data = 10
#         # print(var)
#         # print(self.locals())

#     def printVars(self):
#         print(self.__dict__['data'])

#     def changeVars(self, var_name):
#         self.__dict__[var_name] = 11
    

dic = {
    "one" : 1, 
    "two" : 2, 
    "n" : None
}

if __name__ == '__main__':

    arr =[]
    
    for i in range(10):
        dic["n"] = i
        arr.append(deepcopy(dic))

    print(arr)

    for d in arr:
        arr.remove(d)

    print('---')
    print(arr)