# windows-server
This repository encompasses a publisher/subscriber model that is deployable on a Windows 10 operating system. The system follows the technical structure of the Robot Operating System found [here](http://wiki.ros.org/ROS/Technical%20Overview). The main (master) server is built on C++ and uses sockets to buffer data to different processes. Each process or node has a associated library written in python to interface with other nodes. 

## Setup 
1. Install pip for retrieving and installing python libraries and packages
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```
2. Install python interface modules 
```
py -m pip install -e <path/to/repository>/scripts
```

## Running the Server
For now, a pre-compiled executable for Windows 10 can be found in [this](https://github.com/NMMallick/windows-server/tree/main/server/Release) folder. This must be running before you can run and publisher or subscriber.

## Examples for creating Publishers and Subscribers
Examples on creating publisher and subscriber nodes can be found [here](https://github.com/NMMallick/windows-server/tree/main/scripts/examples). You'll find another README.md on how to generate message classes to send custom messages over the server
