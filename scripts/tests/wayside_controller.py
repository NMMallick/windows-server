from msg import msg

class wayside(msg):
	def __init__(self):
		super().__init__()
		self.__vars__ = []
		self.my_str = None
		self.__vars__.append(self.my_str)
		self.my_int = None
		self.__vars__.append(self.my_int)
		self.my_bools = []
		self.__vars__.append(self.my_bools)
		self.__data_types__.append("string")
		self.__data_types__.append("int")
		self.__data_types__.append("bool[]")


	def serialize(self):
		self.__vars__[0] = self.my_str
		self.__vars__[1] = self.my_int
		self.__vars__[2] = self.my_bools
		return self.__serialize__(self.__vars__)

	def deserialize(self, buffer):
		self.__deserialize__(buffer, self.__vars__)
		self.my_str = self.__vars[0]
		self.my_int = self.__vars[1]
		self.my_bools = self.__vars[2]
