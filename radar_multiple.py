import socket
import sys
import matplotlib.pyplot as plt
import math
import numpy as np
import time
import csv

from datetime import datetime


def recv_msg(sockTCP, msg_len, max_msg_size):
    resp_frame = bytearray(msg_len)
    pos = 0
    while pos < msg_len:
        resp_frame[pos:pos + max_msg_size] = sockTCP.recv(max_msg_size)
        pos += max_msg_size
    return resp_frame


# Define variables
msg_len = 9
max_msg_size = 8
packageLength = 1500
x = list(range(128))
TCP_IP_1 = '192.168.100.201'
TCP_IP_2 = '192.168.100.203'

TCP_PORT = 6172


def collect_data(TCP_IP, i):
    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockTCP.connect((TCP_IP, TCP_PORT))
    except:
        print('Error while connecting with TCP/IP socket')
        sys.exit(1)

    # Create UDP object with corresponding IP and port
    UDP_IP = "192.168.100.1"
    UDP_PORT = 4567
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    try:
        sockUDP.bind((UDP_IP, UDP_PORT))
    except:
        print('Error while connecting with UDP socket')
        sys.exit(1)

    # Connect with sensor
    header = bytes("INIT", 'utf-8')
    payloadlength = (0).to_bytes(4, byteorder='little')
    cmd_frame = header + payloadlength
    sockTCP.send(cmd_frame)
    resp_frame = recv_msg(sockTCP, msg_len, max_msg_size)
    if resp_frame[8] != 0:
        print('Error: Command not acknowledged')
        sys.exit(1)

    # Set max range to 10m
    header = bytes("RSET", 'utf-8')
    payloadlength = (4).to_bytes(4, byteorder='little')
    max_range = (1).to_bytes(4, byteorder='little')
    cmd_frame = header + payloadlength + max_range
    sockTCP.send(cmd_frame)
    resp_frame = recv_msg(sockTCP, msg_len, max_msg_size)
    if resp_frame[8] != 0:
        print('Error: Command not acknowledged')
        sys.exit(1)

    # Create figure

    # Enable PDAT and TDAT data
    header = bytes("RDOT", 'utf-8')
    datarequest = (24).to_bytes(4, byteorder='little')
    cmd_frame = header + payloadlength + datarequest
    sockTCP.send(cmd_frame)
    resp_frame = recv_msg(sockTCP, msg_len, max_msg_size)
    array_dat = []
    # readout and plot time and frequency adc_data continuously

    # GET PDAT DATA ---------------------------------
    pdat_data = []
    packageData, adr = sockUDP.recvfrom(packageLength)
    while packageData[0:4] != b'PDAT':  # do while header isn't expected header
        packageData, adr = sockUDP.recvfrom(packageLength)
    respLength = int.from_bytes(packageData[4:8], byteorder='little')  # get response length
    numberoftargets = round(respLength / 10)  # calculate number of detected targets
    packageData = packageData[8:len(packageData)]  # exclude header from data
    pdat_data = packageData  # store data
    packageData, adr = sockUDP.recvfrom(packageLength)  # get data
    while packageData.find(b'TDAT') == -1:
        pdat_data += packageData  # store data
        packageData, adr = sockUDP.recvfrom(packageLength)  # get data

    # GET TDAT DATA -------------------------------
    respLength = int.from_bytes(packageData[4:8], byteorder='little')  # get response length
    numberoftrackedtargets = round(respLength / 10)  # calculate number of tracked targets
    packageData = packageData[8:len(packageData)]  # exclude header from data
    tdat_data = packageData  # store data
    packageData, adr = sockUDP.recvfrom(packageLength)  # get data
    while packageData.find(b'PDAT') == -1:
        tdat_data += packageData  # store data
        packageData, adr = sockUDP.recvfrom(packageLength)  # get data

    # init arrays
    distance_pdat = []
    speed_pdat = []
    azimuth_pdat = []
    elevation_pdat = []
    magnitude_pdat = []
    distance_tdat = []
    speed_tdat = []
    azimuth_tdat = []
    elevation_tdat = []
    magnitude_tdat = []

    array_dat_1 = []

    # get distance [cm], speed [km/h*100] and azimuth angle [degree*100] of the detected raw targets by converting pdat into uint16/int16
    for target in range(0, numberoftargets):
        distance_pdat.append(int.from_bytes(pdat_data[10 * target:10 * target + 2], byteorder='little', signed=False))
        speed_pdat.append(
            int.from_bytes(pdat_data[10 * target + 2:10 * target + 4], byteorder='little', signed=True) / 100)
        azimuth_pdat.append(
            math.radians(
                int.from_bytes(pdat_data[10 * target + 4:10 * target + 6], byteorder='little', signed=True) / 100))
        elevation_pdat.append(
            math.radians(
                int.from_bytes(pdat_data[10 * target + 6:10 * target + 8], byteorder='little', signed=True) / 100))
        magnitude_pdat.append(
            int.from_bytes(pdat_data[10 * target + 8:10 * target + 10], byteorder='little', signed=False))

    # get distance [cm], speed [km/h*100] and azimuth angle [degree*100] of the tracked targets by convert tdat data into uint16/int16
    for target in range(0, numberoftrackedtargets):
        distance_tdat.append(int.from_bytes(tdat_data[10 * target:10 * target + 2], byteorder='little', signed=False))
        speed_tdat.append(
            int.from_bytes(tdat_data[10 * target + 2:10 * target + 4], byteorder='little', signed=True) / 100)
        azimuth_tdat.append(
            math.radians(
                int.from_bytes(tdat_data[10 * target + 4:10 * target + 6], byteorder='little', signed=True) / 100))
        elevation_tdat.append(
            math.radians(
                int.from_bytes(tdat_data[10 * target + 6:10 * target + 8], byteorder='little', signed=True) / 100))
        magnitude_tdat.append(
            int.from_bytes(tdat_data[10 * target + 8:10 * target + 10], byteorder='little', signed=False))

        from datetime import datetime
        t1 = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

        array_dat.append(
            [t1, target, distance_pdat[target], speed_pdat[target], azimuth_pdat[target], elevation_pdat[target],
             magnitude_pdat[target]]

        # saving to directory

        # disconnect from sensor
    payloadlength = (0).to_bytes(4, byteorder='little')
    header = bytes("GBYE", 'utf-8')
    cmd_frame = header + payloadlength
    sockTCP.send(cmd_frame)

    # get response
    response_gbye = recv_msg(sockTCP, msg_len, max_msg_size)
    if response_gbye[8] != 0:
        print('Error during disconnecting with V-MD3')
    sys.exit(1)

    # close connection to TCP/IP
    sockTCP.close()

    # close connection to UDP
    sockUDP.close()
    return array_dat


def main():
    array_dat = []
    array_dat1 = []
    for ctr in range(10):
        array_dat.append(collect_data(TCP_IP_1, 2))

        time.delay(0.1)
        array_dat1.append(collect_data(TCP_IP_2,1))
        #b.append(array_dat1)
    header = ['time_stamp(sec)', 'target_ID', 'distance_tdat(cm)', 'speed_tdat[km/h × 100]',
              'azimuth_tdat[degree × 100]', 'elevation_tdat[degree× 100]', 'magnititude_tdat']
    with open('output1.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(a)
    with open('output2.csv', 'w', encoding='UTF8', newline='') as f1:
        writer1 = csv.writer(f1)

        # write the header
        writer1.writerow(header)

        # write multiple rows
        writer1.writerows(b)
#just checking how this works
#ii dont know what iam doing
#check three if it works
if __name__ == '__main__':
    main()






