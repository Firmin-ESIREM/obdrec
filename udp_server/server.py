from socket import socket, SOCK_DGRAM, AF_INET


def retrieve_udp() -> str:
    retrieve_server = socket(AF_INET, SOCK_DGRAM)
    retrieve_server.bind(("127.0.0.1", 5678))
    message, address = retrieve_server.recvfrom(1500)
    return message.decode("utf-8")


def send_udp(data: str):
    data_encoded = data.encode("utf-8")
    send_server = socket(AF_INET, SOCK_DGRAM)
    send_server.bind(("127.0.0.1", 1234))
    address = ("127.0.0.1", 5678)
    send_server.sendto(data, address)


def receive_forza_data(port: int, ip: str = "0.0.0.0") -> bytes:
    forza_server = socket(AF_INET, SOCK_DGRAM)
    forza_server.bind((ip, port))
    message, address = forza_server.recvfrom(1500)
    return message
