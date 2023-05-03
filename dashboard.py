from sys import argv, stderr, exit as sys_exit
import dashboard
from os import path

mode = dashboard.LIVE

print(argv)

if len(argv) == 2:
    mode = dashboard.REPLAY
    if not(path.isfile(argv[1])):
        print("The file you specified does not exist.", file=stderr)
        sys_exit(1)
