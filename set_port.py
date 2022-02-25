import socket
import sys

def recv_msg(sockTCP, msg_len, max_msg_size):
    resp_frame = bytearray(msg_len)
    pos = 0
    while pos < msg_len:
        resp_frame[pos:pos + max_msg_size] = sockTCP.recv(max_msg_size)
        pos += max_msg_size
    return resp_frame
msg_len = 9
max_msg_size = 8
packageLength = 1500
TCP_IP = '192.168.100.203'
TCP_PORT = 6172
UDP_IP = "192.168.100.1"


class set_udp_port:

    def __init__(self,UDP_PORT = 4567):
        self.UDP_PORT = UDP_PORT
        self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sockTCP.connect((TCP_IP, TCP_PORT))
        except:
            print('Error while connecting with TCP/IP socket')
            sys.exit(1)

    def start_connection(self):
        header = bytes("INIT", 'utf-8')
        payloadlength = (0).to_bytes(4, byteorder='little')
        cmd_frame = header + payloadlength
        self.sockTCP.send(cmd_frame)
        resp_frame = recv_msg(self.sockTCP, msg_len, max_msg_size)
        if resp_frame[8] != 0:
            print('start Error: Command not acknowledged')
            sys.exit(1)

    def change_port(self):
        header = bytes("UDPP", 'utf-8')
        payloadlength = (4).to_bytes(4, byteorder='little')
        command = (self.UDP_PORT).to_bytes(4, byteorder='little')
        cmd_frame = header + payloadlength + command
        self.sockTCP.send(cmd_frame)
        resp_frame = recv_msg(self.sockTCP, msg_len, max_msg_size)
        if resp_frame[8] != 0:
            print('change port Error: Command not acknowledged')
            sys.exit(1)

    def stop(self):
        payloadlength = (0).to_bytes(4, byteorder='little')
        header = bytes("GBYE", 'utf-8')
        cmd_frame = header + payloadlength
        self.sockTCP.send(cmd_frame)

        # get response
        response_gbye = recv_msg(self.sockTCP, msg_len, max_msg_size)
        if response_gbye[8] != 0:
            print('Error during disconnecting with V-MD3')
        self.sockTCP.close()


def main():
    try:
        s = set_udp_port(4660)
        s.start_connection()
        s.change_port()
        s.stop()
        print("Done")
    except:
        print("Error")


if __name__ == '__main__':
    main()