from msg import msg

class train_controller(msg):
	def __init__(self):
		super().__init__()
		self.__vars__ = []
		self.commandedSpeed = None
		self.__vars__.append(self.commandedSpeed)
		self.suggestedSpeed = None
		self.__vars__.append(self.suggestedSpeed)
		self.speedLimit = None
		self.__vars__.append(self.speedLimit)
		self.temperature = None
		self.__vars__.append(self.temperature)
		self.serviceBrake = None
		self.__vars__.append(self.serviceBrake)
		self.eBrake = None
		self.__vars__.append(self.eBrake)
		self.leftDoor = None
		self.__vars__.append(self.leftDoor)
		self.rightDoor = None
		self.__vars__.append(self.rightDoor)
		self.internalLights = None
		self.__vars__.append(self.internalLights)
		self.externalLights = None
		self.__vars__.append(self.externalLights)
		self.announcement = None
		self.__vars__.append(self.announcement)
		self.authority = []
		self.__vars__.append(self.authority)
		self.nextStation = None
		self.__vars__.append(self.nextStation)
		self.__data_types__.append("int")
		self.__data_types__.append("int")
		self.__data_types__.append("int")
		self.__data_types__.append("int")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool")
		self.__data_types__.append("bool[]")
		self.__data_types__.append("string")


	def serialize(self):
		self.__vars__[0] = self.commandedSpeed
		self.__vars__[1] = self.suggestedSpeed
		self.__vars__[2] = self.speedLimit
		self.__vars__[3] = self.temperature
		self.__vars__[4] = self.serviceBrake
		self.__vars__[5] = self.eBrake
		self.__vars__[6] = self.leftDoor
		self.__vars__[7] = self.rightDoor
		self.__vars__[8] = self.internalLights
		self.__vars__[9] = self.externalLights
		self.__vars__[10] = self.announcement
		self.__vars__[11] = self.authority
		self.__vars__[12] = self.nextStation
		return self.__serialize__(self.__vars__)

	def deserialize(self, buffer):
		self.__deserialize__(buffer, self.__vars__)
		self.commandedSpeed = self.__vars__[0]
		self.suggestedSpeed = self.__vars__[1]
		self.speedLimit = self.__vars__[2]
		self.temperature = self.__vars__[3]
		self.serviceBrake = self.__vars__[4]
		self.eBrake = self.__vars__[5]
		self.leftDoor = self.__vars__[6]
		self.rightDoor = self.__vars__[7]
		self.internalLights = self.__vars__[8]
		self.externalLights = self.__vars__[9]
		self.announcement = self.__vars__[10]
		self.authority = self.__vars__[11]
		self.nextStation = self.__vars__[12]
