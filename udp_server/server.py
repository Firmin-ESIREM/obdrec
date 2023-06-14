from socket import socket, SOCK_DGRAM, AF_INET


def retrieve_udp():
    retrieve_server = socket(AF_INET, SOCK_DGRAM)
    retrieve_server.bind(("127.0.0.1", 1234))
    message, address = retrieve_server.rcvfrom(1500)
    return message


def send_udp(data):
    send_server = socket(AF_INET, SOCK_DGRAM)
    send_server.bind(("127.0.0.1", 1234))
    address = ("127.0.0.1", 1234)
    send_server.sendto(data, address)


def receive_forza_data(port: int, ip: str = "0.0.0.0"):
    forza_server = socket(AF_INET, SOCK_DGRAM)
    forza_server.bind((ip, port))
    message, address = forza_server.recvfrom(1500)
    return message
