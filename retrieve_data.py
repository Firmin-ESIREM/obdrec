from obd import OBD, commands
from time import sleep, time
from datetime import datetime
from flask import Flask
from threading import Thread

connection = OBD()  # connect to OBD adapter
travel_name = "travel_" + datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv"
with open(travel_name, 'a') as f:  # create csv file to log data from the travel
    f.write('time' + ';' + 'speed_kph' + ';' + 'rpm' + ';' + 'intake_temperature_degC' + '\n')

app = Flask(__name__)

DATA = {
    "speed": 0,
    "rpm": 0,
    "intake_temp": 0
}


@app.route('/get_data/', methods=["POST"])
def get_data():
    return str(DATA)


def pull_data():
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
