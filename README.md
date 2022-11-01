# windows-server
This repository encompasses a publisher/subscriber model that is deployable on a Windows 10 operating system. The system follows the technical structure of the Robot Operating System found [here](http://wiki.ros.org/ROS/Technical%20Overview). The main (master) server is built on C++ and uses sockets to buffer data to different processes. Each process or node has a associated library written in python to interface with other nodes. 

## Setup 
1. Install pip for python libraries and packages
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

