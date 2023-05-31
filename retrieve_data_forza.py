import struct
from socket import socket, SOCK_DGRAM, AF_INET
from threading import Thread
from flask import request, Response
import flask_app
from json import dumps, loads
from werkzeug.exceptions import NotFound

# creat UDP server
SERVER_SOCKET = None


def forza_server_init(ip: str, port: int) -> None:
    global SERVER_SOCKET
    SERVER_SOCKET = socket(AF_INET, SOCK_DGRAM)
    SERVER_SOCKET.bind((ip, port))  # IP and Port of the receiver


# reading data and assigning names to data types in data_types dict
data_types = {}
with open('data_format.txt', 'r') as f:
    lines = f.read().split('\n')
    for line in lines:
        data_types[line.split()[1]] = line.split()[0]

# assigning sizes in bytes to each variable type
jumps = {
    's32': 4,  # Signed 32bit int, 4 bytes of size
    'u32': 4,  # Unsigned 32bit int
    'f32': 4,  # Floating point 32bit
    'u16': 2,  # Unsigned 16bit int
    'u8': 1,  # Unsigned 8bit int
    's8': 1,  # Signed 8bit int
    'hzn': 12  # Unknown, 12 bytes of.. something
}

DATA = {
    "IsRaceOn": 0,
    "EngineMaxRpm": 0,
    "CurrentEngineRpm": 0,
    "Speed": 0,
    "Fuel": 0,
    "DistanceTraveled": 0,
    "BestLap": 0,
    "CurrentLap": 0,
    "LapNumber": 0,
    "RacePosition": 0,
    "Accel": 0,
    "Brake": 0,
    "Gear": 0
}


def decoded_data(data: str) -> dict[str, int]:  #inspired by https://github.com/nikidziuba/Forza_horizon_data_out_python/tree/main
    data_decoded = {}
    # additional var
    passed_data = data

    for i in data_types:
        d_type = data_types[i]  # checks data type (s32, u32 etc.)
        jump = jumps[d_type]  # gets size of data
        current = passed_data[:jump]  # gets data

        decoded = 0
        # complicated decoding for each type of data
        if d_type == 's32':
            decoded = int.from_bytes(current, byteorder='little', signed=True)
        elif d_type == 'u32':
            decoded = int.from_bytes(current, byteorder='little', signed=False)
        elif d_type == 'f32':
            decoded = struct.unpack('f', current)[0]
        elif d_type == 'u16':
            decoded = struct.unpack('H', current)[0]
        elif d_type == 'u8':
            decoded = struct.unpack('B', current)[0]
        elif d_type == 's8':
            decoded = struct.unpack('b', current)[0]

        # adds decoded data to the dict
        data_decoded[i] = decoded

        # removes already read bytes from the variable
        passed_data = passed_data[jump:]

    # returns the decoded data
    return data_decoded


def retrieve_data() -> None:
    ip = input("Enter the IP address you specify on Forza Horizon EX : 0.0.0.0: ")
    port = int(input("Enter the port number you specify on Forza Horizon: "))
    forza_server_init(ip, port)
    while True:
        data, addr = SERVER_SOCKET.recvfrom(1500)  # received data string
        data_decoded = decoded_data(data)  # decoded data
        DATA["IsRaceOn"] = data_decoded["IsRaceOn"]
        DATA["EngineMaxRpm"] = data_decoded["EngineMaxRpm"]
        DATA["CurrentEngineRpm"] = data_decoded["CurrentEngineRpm"]
        DATA["Speed"] = data_decoded["Speed"]
        DATA["Fuel"] = data_decoded["Fuel"]
        DATA["DistanceTraveled"] = data_decoded["DistanceTraveled"]
        DATA["BestLap"] = data_decoded["BestLap"]
        DATA["CurrentLap"] = data_decoded["CurrentLap"]
        DATA["LapNumber"] = data_decoded["LapNumber"]
        DATA["RacePosition"] = data_decoded["RacePosition"]
        DATA["Accel"] = data_decoded["Accel"]
        DATA["Brake"] = data_decoded["Brake"]
        DATA["Gear"] = data_decoded["Gear"]


@flask_app.app.route('/get_data_forza/', methods=["POST"])
def get_data() -> Response:
    data_type = request.form.get('data_type_forza')
    data_request = loads(data_type)
    data_filtered = {}
    for element in data_request:
        if element not in DATA.keys():
            raise NotFound
        data_filtered[element] = DATA[element]
    data_json = dumps(data_filtered)
    return data_json


Thread(target=retrieve_data()).start()