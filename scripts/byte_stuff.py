import struct


data = 1000
my_str = 'my_string'
p_str = struct.pack(f'{len(my_str)}s', my_str.encode('utf-8'))
arr = bytearray()

arr.extend(data.to_bytes(4, 'big'))
arr.extend(p_str)

print(arr[2])