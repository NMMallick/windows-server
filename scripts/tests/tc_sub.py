from train_controller import train_controller
from winserver import winserver


class TrainControllerSub:
    def __init__(self):
        self.node = winserver("tc_sub")
        self.sub = self.node.subscribe('train_controller', train_controller, self.callback, 1)

    def callback(self, msg):
        print('Ints')
        print('----\n')
        print('Commanded speed: ', msg.commandedSpeed)
        print('Suggested speed: ', msg.suggestedSpeed)
        print('Speed limit: ', msg.speedLimit)
        print('Temperature: ', msg.temperature)
        print('\n')

        print('Booleans')
        print('--------\n')
        print('Service Brake: ', msg.serviceBrake)
        print('Emergency Brake: ', msg.eBrake)
        print('Left Door: ', msg.leftDoor)
        print('Right Door: ', msg.rightDoor)
        print('Internal Lights: ', msg.internalLights)
        print('External Lights: ', msg.externalLights)
        print('Announcement: ', msg.announcement)
        print('Authority: ', msg.authority)

        print('String')
        print('------\n')
        print('Next Station: ', msg.nextStation)

    def spin(self):
        self.node.spin()

if __name__ == '__main__':
    tc = TrainControllerSub()
    tc.spin()