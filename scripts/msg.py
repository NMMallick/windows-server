datatypes = {
    ## Character ##
    "character" :{
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
    "integer" : {
        "bytes" : 4,
        "format" : 'i'
    }
}

class msg:
    def __init__(self):
        self.__data_types__ = []

    def __serialize__(self, topic_name, data):

        if len(data) != len(self.__data_types__):
            print("Err! Invalid number of message variables")
            exit(-1)

        for i, dtype in enumerate(self.__data_types__):
            isArray = True if '[]' in dtype else False
            if isArray:
                dtype = dtype.replace('[]', '')

            data_byte_length = datatypes[dtype]['byte']

            field_length = len(len(data[i]))*data_byte_length if isArray else data_byte_length

        ## Add header topic/time

        ## Add data
        pass

    def __deserialize__(self, topic_name,data):

        ## Remove header

        ## unpack data
        pass

    def __get_format__(self, datatype):

        pass