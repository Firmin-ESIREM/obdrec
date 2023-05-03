from obd import OBD, commands
from time import sleep, time
from datetime import datetime

connection = OBD()  # connect to OBD adapter
travel_name = "travel_" + datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv"
with open(travel_name, 'a') as f:   # create csv file to log data from the travel
    f.write('time' + ';' + 'speed_kph' + ';' + 'rpm' + ';' + 'intake_temperature' + '\n')
while True:
    cmd = commands.SPEED	  # define command as SPEED
    speed = connection.query(cmd)  # send the command
    print(speed)
    cmd = commands.RPM
    rpm = connection.query(cmd)
    print(rpm)
    cmd = commands.INTAKE_TEMP
    intake_temperature = connection.query(cmd)
    print(intake_temperature)
    with open(travel_name, 'a') as f:
        f.write(str(time()) + ';' + str(speed.value.value) + ';' + str(rpm.value.value) + ';'
                + str(intake_temperature.value.value) + '\n')
    sleep(1)
