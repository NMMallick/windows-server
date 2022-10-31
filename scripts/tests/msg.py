import enum
import time
import struct
import math

datatypes = {
    ## Character ##
    "char" :{
        "bytes" : 1,
        "format" : 'c'
    },
    ## Double ##
    "double" : {
        "bytes" : 8,
        "format" : 'd'
    },
    ## Float ##
    "float" : {
        "bytes" : 4,
        "format" : 'f'
    },
    ## Boolean ##
    "bool" : {
        "bytes" : 1,
        "format" : '?'
    },
    ## Integer ##
    "int" : {
        "bytes" : 4,
        "format" : 'i'
    },
    "string" : {
        "bytes" : None,
        "format" : 's'
    }
}

class msg:
    def __init__(self):
        self.__data_types__ = []
        self.__serialized_data__ = bytearray()

        self.sender = ""
        self.time = None

    ## MESSAGE HEADER ##
    ## (fields)
    ## 4 bytes = header length
    ## 8 bytes = time stamp
    ## (header length - 8 bytes) = sender name
    def __generate_header__(self, sender):
        ## Generate 8 bytes corresponding to time
        __serialized_data__ = bytearray()

        now = time.time()
        __serial_time__ = struct.pack('>d', now)

        ## Figure out how many chars are in the sender id
        __topic_length__ = len(sender)

        ## Generate {topic_length} number of bytes
        __serial_topic__ = struct.pack(f'>{__topic_length__}s', sender.encode('utf-8'))

        __total_header_byte_length__ = __topic_length__ + 8
        __serial_header_length__ = struct.pack('>i', __total_header_byte_length__)

        __serialized_data__ += (__serial_header_length__ + __serial_time__ + __serial_topic__)

        return __serialized_data__

    ##
    def __serialize__(self, data):

        if len(data) != len(self.__data_types__):
            print("Err! Invalid number of message variables")
            exit(-1)

        ## Clear the byte array
        self.__serialized_data__.clear()
        __serialized_data__ = bytearray()

        ## Add header topic/time
        __header__ = self.__generate_header__(self.sender)

        for i, dtype in enumerate(self.__data_types__):
            ## Figure out if it's an array
            isArray = True if '[]' in dtype else False
            isString = True if 'string' in dtype else False

            if isArray:
                dtype = dtype.replace('[]', '')

            __data_byte_length__ = 0
            if isString:
                __data_byte_length__ = len(data[i])
            else:
                __data_byte_length__ = datatypes[dtype]['bytes']

            # data_byte_length = datatypes[dtype]['bytes']
            format_type = datatypes[dtype]['format']

            ## Determine the field length
            __field_length__ = 0

            if isArray:
                __field_length__ = len(data[i])*__data_byte_length__
            else:
                __field_length__ = __data_byte_length__

            __serialized_data__.extend(struct.pack('>i', __field_length__))

            ## Extend the bytearray to hold the actual data
            if isArray:
                for d in data[i]:
                    __serialized_data__.extend(struct.pack(f'>{format_type}', d))
            elif isString:
                __serialized_data__.extend(struct.pack(f'>{__field_length__}{format_type}', data[i].encode('utf-8')))
            else:
                __serialized_data__.extend(struct.pack(f'>{format_type}', data[i]))

        __message__length__ = len(__serialized_data__) + len(__header__)
        self.__serialized_data__ += (struct.pack('>i', __message__length__) + __header__ + __serialized_data__)
        return self.__serialized_data__

    def __deserialize__(self, data, vars):

        if len(data) == 0:
            return

        __message_length__ = struct.unpack('>i', data[0:4])[0]
        __stamped_message__ = data[4:]

        if len(data) != __message_length__ + 4:
            print("Err: message unable to be deserialized (size conflict)")
            return

        ## Unpack header
        __header_length__ = struct.unpack('>i', __stamped_message__[0:4])[0]
        __header__ = __stamped_message__[4:__header_length__+4]
        self.time = struct.unpack('>d', __header__[0:8])[0]
        self.sender = struct.unpack(f'>{__header_length__-8}s', __header__[8:__header_length__])[0]

        ## Unpack data
        __data__ = __stamped_message__[__header_length__+4:]

        for i, d in enumerate(self.__data_types__):
            ## Get integer from first 4 bytes
            #   indicating size of variable
            __field_size__ = struct.unpack('>i', __data__[0:4])[0]
            __data__ = __data__[4:]

            ## Figure out whether or not the data
            #   is a primitive data type or an array
            #   of primitive data types
            isArray = False
            if '[]' in d:
                d = d.replace('[]', '')
                isArray = True

            isString = False
            if d == 'string':
                isString = True

            __prim_type__ = datatypes[d]

            if isArray:
                var = []
                for i in range(int(__field_size__/__prim_type__['bytes'])):
                    var.append(struct.unpack('>' + __prim_type__['format'], __data__[0:__prim_type__['bytes']])[0])
                    __data__ = __data__[__prim_type__['bytes']:]

                vars[i] = var
            else:
                if isString:
                    var = struct.unpack(f'>{__field_size__}'+__prim_type__['format'], __data__[0:__field_size__])[0]
                    vars[i] = var.decode('utf-8')
                    __data__ = __data__[__field_size__:]
                else:
                    var = struct.unpack('>'+__prim_type__['format'], __data__[0:__field_size__])[0]
                    vars[i] = var
                    __data__ = __data__[__field_size__:]

if __name__ == '__main__':
    m = msg()

    m.__data_types__ = ['double[]', 'string', 'int', 'bool[]']
    my_double = [math.pi, math.pi, math.pi]
    my_string = "my_string"
    my_int = 10
    my_bools = [True, False]

    m.__serialize__([my_double, my_string, my_int, my_bools])

    m.__deserialize__(m.__serialized_data__, [my_double, my_string, my_int, my_bools])

