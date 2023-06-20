from socket import socket, SOCK_DGRAM, AF_INET


def retrieve_udp() -> str:
    """
    Init a UDP socket to receive data and return it.
    :return: the message that was received
    """
    retrieve_server = socket(AF_INET, SOCK_DGRAM)
    retrieve_server.bind(("127.0.0.1", 5678))
    message, address = retrieve_server.recvfrom(1500)
    return message.decode("utf-8")


def send_udp(data: str):
    """
    Init a UDP socket to send data.
    :param data: data you need to send
    :return:
    """
    data_encoded = data.encode("utf-8")
    send_server = socket(AF_INET, SOCK_DGRAM)
    send_server.bind(("127.0.0.1", 1234))
    address = ("127.0.0.1", 5678)
    send_server.sendto(data_encoded, address)


def receive_forza_data(port: int, ip: str) -> bytes:
    """
    Init a UDP socket to receive data from Forza and return them.
    :param port: port number specify on Forza
    :param ip: IP address specify on Forza
    :return: telemetry from Forza
    """
    forza_server = socket(AF_INET, SOCK_DGRAM)
    forza_server.bind((ip, port))
    message, address = forza_server.recvfrom(1500)
    return message
