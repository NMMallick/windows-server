import atexit
from time import sleep
from train_controller import train_controller
from  winserver import winserver
import random




class TrainControllerNode:
    def __init__(self):
        atexit.register(self.shutdown)

        self.node = winserver("tc_pub")
        self.pub_msg = train_controller()

        self.pub = self.node.advertise('train_controller', train_controller, 1)
        self.done = False

        self.stations = ['downtown', 'herring', 'east liberty', 'shadyside', 'wilkinburg']

    def spin(self, rate):
        while not self.done:
            ## Ints
            self.pub_msg.commandedSpeed = random.randint(0, 50)
            self.pub_msg.suggestedSpeed = random.randint(0,50)
            self.pub_msg.speedLimit = random.randint(0,50)
            self.pub_msg.temperature = random.randint(0,50)

            ## Bools
            self.pub_msg.announcement = random.choice([True, False])
            self.pub_msg.serviceBrake = random.choice([True, False])
            self.pub_msg.eBrake = random.choice([True, False])
            self.pub_msg.leftDoor = random.choice([True, False])
            self.pub_msg.rightDoor = random.choice([True, False])
            self.pub_msg.internalLights = random.choice([True, False])
            self.pub_msg.externalLights = random.choice([True, False])
            self.pub_msg.announcement = random.choice([True, False])

            ## Bool Array
            temp_auth = []
            for i in range(150):
                temp_auth.append(random.choice([True, False]))
            self.pub_msg.authority = temp_auth

            ## String
            self.pub_msg.nextStation = random.choice(self.stations)

            ## publish
            self.pub.publish(self.pub_msg)
            sleep(rate)

    def shutdown(self):
        self.done = True

if __name__ == '__main__':
    tc = TrainControllerNode()
    tc.spin(2.0)