from obd import OBD, commands
from time import time
from datetime import datetime
from flask import request, Response
from threading import Thread
from json import dumps, loads
from werkzeug.exceptions import NotFound
import flask_app

connection = OBD()  # connect to OBD adapter
travel_name = "travel_" + datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv"
with open(travel_name, 'a') as f:  # create csv file to log data from the travel
    f.write('time' + ';' + 'speed_kph' + ';' + 'rpm' + ';' + 'intake_temperature_degC' + '\n')

DATA = {
    "speed": 0,
    "rpm": 0,
    "intake_temp": 0
}


@flask_app.app.route('/get_data/', methods=["POST"])  # post retrieve data for the dashboard
def get_data() -> Response:
    data_type = request.form.get('data_type')
    data_request = loads(data_type)
    data_filtered = {}
    for element in data_request:
        if element not in DATA.keys():
            raise NotFound
        data_filtered[element] = DATA[element]
    data_json = dumps(data_filtered)
    return data_json


def pull_data() -> None:
    while True:
        cmd = commands.SPEED  # define command as SPEED
        speed = connection.query(cmd)  # send the command
        DATA["speed"] = speed.value.m
        cmd = commands.RPM
        rpm = connection.query(cmd)
        DATA["rpm"] = rpm.value.m
        cmd = commands.INTAKE_TEMP
        intake_temperature = connection.query(cmd)
        DATA["intake_temp"] = intake_temperature.value.m
        with open(travel_name, 'a') as ft:
            ft.write(str(time()) + ';' + str(speed.value.m) + ';' + str(rpm.value.m) + ';'
                     + str(intake_temperature.value.m) + '\n')
        print(str(time()) + " : new record")


Thread(target=pull_data).start()
