""" #VMD_3 radar # two sensors # Multithreading
    Data Collection method from multiple sensor
    before running this program please set port number 
    ~developed by Sohan P Varghese- Cranfield University"""


from threading import Thread
import socket
import sys
import math
import csv
from datetime import datetime

def recv_msg(sock_tcp, msg_length, maximum_msg_size):
    resp_frame = bytearray(msg_length)
    pos = 0
    while pos < msg_length:
        resp_frame[pos:pos + maximum_msg_size] = sock_tcp.recv(maximum_msg_size)
        pos += maximum_msg_size
    return resp_frame


msg_len = 9
max_msg_size = 8
packageLength = 1500


TCP_IP_1 = '192.168.100.201'
TCP_IP_2 = '192.168.100.203'
TCP_PORT = 6172


def threaded(func):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread
    return wrapper


class radar_interface:

    def __init__(self, tcp_ip, UDP_PORT = 4567):
        self.TCP_IP = tcp_ip
        self.array_pdat = []
        self.array_tdat = []
        UDP_IP = '192.168.100.1'
        self.UDP_PORT = UDP_PORT
        self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sockTCP.connect((self.TCP_IP, TCP_PORT))
        except:
            print('Error while connecting with TCP/IP socket')
            sys.exit(1)

        # Create UDP object with corresponding IP and port

        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        try:
            self.sockUDP.bind((UDP_IP, self.UDP_PORT))
        except:
            print('Error while connecting with UDP socket')
            sys.exit(1)

    def reset(self):
        self.array_pdat = []
        self.array_tdat = []

    def connect(self):
        header = bytes("INIT", 'utf-8')
        payload_length = (0).to_bytes(4, byteorder='little')
        cmd_frame = header + payload_length
        self.sockTCP.send(cmd_frame)
        resp_frame = recv_msg(self.sockTCP, msg_len, max_msg_size)
        if resp_frame[8] != 0:
            print('Error: Command not acknowledged')
            sys.exit(1)

    def configure(self):
        print("inside configure")
        header = bytes("RSET", 'utf-8')
        payload_length = (4).to_bytes(4, byteorder='little')
        max_range = (1).to_bytes(4, byteorder='little')
        cmd_frame = header + payload_length + max_range
        self.sockTCP.send(cmd_frame)
        resp_frame = recv_msg(self.sockTCP, msg_len, max_msg_size)
        if resp_frame[8] != 0:
            print('Error: Command not acknowledged')
            sys.exit(1)

    def start(self):
        # Enable PDAT and TDAT data
        payload_length = (4).to_bytes(4, byteorder='little')
        header = bytes("RDOT", 'utf-8')
        data_request = (24).to_bytes(4, byteorder='little')
        cmd_frame = header + payload_length + data_request
        self.sockTCP.send(cmd_frame)
        resp_frame = recv_msg(self.sockTCP, msg_len, max_msg_size)

    def receive_data(self):
        # GET PDAT DATA ---------------------------------
        pdat_data = []
        packageData, adr = self.sockUDP.recvfrom(packageLength)
        #print(adr)
        while packageData[0:4] != b'PDAT':  # do while header isn't expected header
            packageData, adr = self.sockUDP.recvfrom(packageLength)
        respLength = int.from_bytes(packageData[4:8], byteorder='little')  # get response length
        numberoftargets = round(respLength / 10)  # calculate number of detected targets
        packageData = packageData[8:len(packageData)]  # exclude header from data
        pdat_data = packageData  # store data
        packageData, adr = self.sockUDP.recvfrom(packageLength)  # get data
        while packageData.find(b'TDAT') == -1:
            pdat_data += packageData  # store data
            packageData, adr = self.sockUDP.recvfrom(packageLength)  # get data

        # GET TDAT DATA -------------------------------
        respLength = int.from_bytes(packageData[4:8], byteorder='little')  # get response length
        numberoftrackedtargets = round(respLength / 10)  # calculate number of tracked targets
        packageData = packageData[8:len(packageData)]  # exclude header from data
        tdat_data = packageData  # store data
        packageData, adr = self.sockUDP.recvfrom(packageLength)  # get data
        while packageData.find(b'PDAT') == -1:
            tdat_data += packageData  # store data
            packageData, adr = self.sockUDP.recvfrom(packageLength)  # get data

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



        # get distance [cm], speed [km/h*100] and azimuth angle [degree*100] of the detected raw targets by converting pdat into uint16/int16
        for target in range(0, numberoftargets):
            distance_pdat.append(
                int.from_bytes(pdat_data[10 * target:10 * target + 2], byteorder='little', signed=False))
            speed_pdat.append(
                int.from_bytes(pdat_data[10 * target + 2:10 * target + 4], byteorder='little', signed=True) / 100)
            azimuth_pdat.append(
                math.radians(
                    int.from_bytes(pdat_data[10 * target + 4:10 * target + 6], byteorder='little',
                                   signed=True) / 100))
            elevation_pdat.append(
                math.radians(
                    int.from_bytes(pdat_data[10 * target + 6:10 * target + 8], byteorder='little',
                                   signed=True) / 100))
            magnitude_pdat.append(
                int.from_bytes(pdat_data[10 * target + 8:10 * target + 10], byteorder='little', signed=False))
            t1 = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.array_pdat.append(
                [t1, target, distance_pdat[target], speed_pdat[target], azimuth_pdat[target],
                 elevation_pdat[target],
                 magnitude_pdat[target]])
            #print(array_pdat)

        # get distance [cm], speed [km/h*100] and azimuth angle [degree*100] of the tracked targets by convert tdat data into uint16/int16
        for target in range(0, numberoftrackedtargets):
            distance_tdat.append(
                int.from_bytes(tdat_data[10 * target:10 * target + 2], byteorder='little', signed=False))
            speed_tdat.append(
                int.from_bytes(tdat_data[10 * target + 2:10 * target + 4], byteorder='little', signed=True) / 100)
            azimuth_tdat.append(
                math.radians(
                    int.from_bytes(tdat_data[10 * target + 4:10 * target + 6], byteorder='little',
                                   signed=True) / 100))
            elevation_tdat.append(
                math.radians(
                    int.from_bytes(tdat_data[10 * target + 6:10 * target + 8], byteorder='little',
                                   signed=True) / 100))
            magnitude_tdat.append(
                int.from_bytes(tdat_data[10 * target + 8:10 * target + 10], byteorder='little', signed=False))
            t1 = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')



            self.array_tdat.append(
               [t1, target, distance_pdat[target], speed_pdat[target], azimuth_pdat[target],
                elevation_pdat[target],
                magnitude_pdat[target]])
            #print(array_tdat)

    def stop(self):
        payloadlength = (0).to_bytes(4, byteorder='little')
        header = bytes("GBYE", 'utf-8')
        cmd_frame = header + payloadlength
        self.sockTCP.send(cmd_frame)

        # get response
        response_gbye = recv_msg(self.sockTCP, msg_len, max_msg_size)
        if response_gbye[8] != 0:
            print('Error during disconnecting with V-MD3')

    def disconnect(self):
        # close connection to TCP/IP
        self.sockTCP.close()

        # close connection to UDP
        self.sockUDP.close()

    @threaded
    def loop(self):
        for ctr in range(10):
            self.start()
            self.array_dat.append(self.receive_data())
            self.stop()


def main():
    #radar1 = radar_interface(TCP_IP_1, 4567)
    radar2 = radar_interface(TCP_IP_2, 4660)
    #radar1.connect()
    #radar1.configure()
    # radar1.start()
    #print("connected 1")

    radar2.connect()
    radar2.configure()
    radar2.start()
    print("connected 2")

    # threads = []
    # #threads.append(radar1.loop())
    # threads.append(radar2.loop())
    for ctr in range(10):

        #radar1.receive_data()
        print(ctr)
        radar2.receive_data()
        
        
    # for thread in threads:
    #     thread.join()

    # try:
    #     radar1.stop()
    #     radar1.disconnect()
    #     print("Disconnected 1")
    # except:
    #     print("Couldn't Stop radar 1")
    #
    try:
        radar2.stop()
        radar2.disconnect()
        print("Disconnected 2")
    except:
        print("Couldn't Stop radar 2")

    # print("showing final 1")
    #array_dat_1 = radar1.array_pdat
    print("showing final 2")
    array_dat_2 = radar2.array_tdat
    print(array_dat_2)
    header = ['time_stamp(sec)', 'target_ID', 'distance_tdat(cm)', 'speed_tdat[km/h × 100]',
              'azimuth_tdat[degree × 100]', 'elevation_tdat[degree× 100]', 'magnititude_tdat']
    #with open('output1.csv', 'w', encoding='UTF8', newline='') as f:
    #    writer = csv.writer(f)

        # write the header
    #    writer.writerow(header)

        # write multiple rows
    #    writer.writerows(array_dat)
    #    print("write complete1")
    with open('output2.csv', 'w', encoding='UTF8', newline='') as f1:
        writer1 = csv.writer(f1)

        # write the header
        writer1.writerow(header)

        # write multiple rows
        writer1.writerows(array_dat_2)
        print("write complete2")


if __name__ == '__main__':
    main()

