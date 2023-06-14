from obd import OBD, commands
from time import time
from datetime import datetime
from threading import Thread
from json import dumps
from udp_server import send_udp

connection = OBD()  # connect to OBD adapter


def car_on(rpm: int) -> bool:
    return rpm != 0 and rpm is not None


DATA = {
    "speed": 0,
    "rpm": 0,
    "intake_temp": 0
}


def pull_data() -> None:
    while True:
        cmd = commands.RPM
        rpm = connection.query(cmd)
        if car_on(rpm):
            travel_name = "travel_" + datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv"
            with open(travel_name, 'a') as f:  # create csv file to log data from the travel
                f.write('time' + ';' + 'speed_kph' + ';' + 'rpm' + ';' + 'intake_temperature_degC' + '\n')
            while car_on(rpm):
                cmd = commands.RPM
                rpm = connection.query(cmd)
                DATA["rpm"] = rpm.value.m
                cmd = commands.SPEED  # define command as SPEED
                speed = connection.query(cmd)  # send the command
                DATA["speed"] = speed.value.m
                cmd = commands.INTAKE_TEMP
                intake_temperature = connection.query(cmd)
                DATA["intake_temp"] = intake_temperature.value.m
                with open(travel_name, 'a') as ft:
                    ft.write(str(time()) + ';' + str(speed.value.m) + ';' + str(rpm.value.m) + ';'
                             + str(intake_temperature.value.m) + '\n')
                print(str(time()) + " : new record")
                data_json = dumps(DATA)
                send_udp(data_json)


Thread(target=pull_data).start()
