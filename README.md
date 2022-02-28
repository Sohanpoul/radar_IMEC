# radar_V-MD3
RFbeam microwave GmBH sensor is a digital 3D radar transceiver.
Sensor takes in command through TCP/IP protocol and radar datas are sent over UDP.
This project will help Setuptegrating mltiple radar sensors for data collection.
Setup consist of multiple radar sensors connected via a switch connected to a host machine.
Each sensors need to have seperate IP adrress.
UDP server IP is the host computer IP.
Data is sent to seperate ports in computer and all sensors can be run parallely using multithreading concept.
