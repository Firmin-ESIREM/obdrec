from obd import OBD, commands
from time import sleep, time

connection = OBD()  # connect to OBD adapter

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
    with open("output.csv", 'a') as f:
        f.write(str(time()) + ';' + str(speed) + ';' + str(rpm) + ';' + str(intake_temperature) + '\n')
    sleep(1)
