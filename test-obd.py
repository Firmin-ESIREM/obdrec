from obd import OBD, commands
from time import sleep

connection = OBD()  # connect to OBD adapter

while True:
    cmd = commands.SPEED  # define command as SPEED
    response = connection.query(cmd)  # send the command
    print(response.value)  # print result
    sleep(1)
