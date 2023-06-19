from json import loads
from sys import argv, stderr, exit as sys_exit
import dashboard
from os import path
from datetime import datetime
from csv import reader
import tkinter as tk
from tkinter.font import Font
from threading import Thread
from time import sleep, time
from typing import Union
from udp_server import retrieve_udp


ui = tk.Tk(className="Dashboard")
#ui.attributes("-fullscreen", True)
ui.configure(bg="black", cursor="none")
speed = tk.StringVar(ui, '0')
temperature = tk.StringVar(ui, '0°C')
date_time = tk.StringVar(ui, datetime.now().strftime("%d/%m/%Y\n%H:%M"))
RPM_INDICATOR = [None, None]
GEAR_IMG = None

mode = dashboard.LIVE

if len(argv) not in [2, 3] \
        or (argv[1] == "replay" and len(argv) != 3) \
        or (argv[1] == "live" and len(argv) != 2) \
        or (argv[1] == "forza" and len(argv) != 2) \
        or argv[1] not in ["live", "replay"]:
    print(
        "The arguments you specified are invalid.\n"
        "Usage : $PYTHON_INTERPRETER dashboard.py <live|replay> [path_to_replay_file]",
        file=stderr
    )
    sys_exit(1)

if argv[1] == "replay" and len(argv) == 3:
    mode = dashboard.REPLAY
    if not (path.isfile(argv[2])):
        print("The file you specified does not exist.", file=stderr)
        sys_exit(1)
    if not (argv[2].endswith(".csv")):
        print("The file you provided does not seem to be a CSV file.", file=stderr)
        sys_exit(1)
elif argv[1] == "forza":
    mode = dashboard.FORZA


csv_header = "time;speed_kph;rpm;intake_temperature_degC\n"


def gear_change(old_speed: int, new_speed: int, time_diff: float, rpm: int, combustion: str) -> Union[str, None]:
    acceleration = (new_speed / 3.6 - old_speed / 3.6) / time_diff
    rpm_limit = [0, 0, 0, 0]
    if combustion == "E":  # rpm limit for petrol motorisation
        rpm_limit = [1000, 1700, 2700, 3500]
    elif combustion == "D":  # rpm limit for diesel motorisation
        rpm_limit = [1000, 1700, 2700, 3500]
    if 15 < new_speed < 90:
        if acceleration < -2 and rpm < rpm_limit[1]:
            return "down"
        if -2 < acceleration < 2:
            if rpm < rpm_limit[0]:
                return "down"
            elif rpm > rpm_limit[2]:
                return "up"
        if acceleration > 2 and rpm > rpm_limit[3]:
            return "up"
    return None


def live_trip() -> None:
    sp1, sp2, sp3, sp4 = None, None, None, None
    Thread(target=set_date_time).start()
    while True:
        data = loads(retrieve_udp())
        sp4 = sp3
        sp3 = sp2
        sp2 = sp1
        sp1 = [data["Speed"], time()]
        speed.set(str(round(data["Speed"])))
        #temperature.set(str(data["intake_temp"]) + "°C")
        Thread(target=redo_rpm_arc, args=(data["CurrentEngineRpm"],)).start()
        if all((sp1, sp2, sp3, sp4)):
            gear_suggestion = gear_change(sp4[0], sp1[0], sp1[1] - sp4[1], data["CurrentEngineRpm"], 'E')
            Thread(target=gear_img, args=(gear_suggestion,)).start()


def recorded_trip_loop() -> None:
    sp1, sp2, sp3, sp4, gear_suggestion_before = None, None, None, None, None
    with open(argv[2], 'r') as f:
        lines = f.readlines()

        if lines[0] != csv_header:
            print(lines[0])
            print("The file you provided does not seem to have been generated by our services.", file=stderr)
            sys_exit(1)
        start_time = datetime.now()
        trip_beginning = float(list(reader([lines[1]], delimiter=';'))[0][0])
        for line in lines[1:]:
            parsed_line = list(reader([line], delimiter=';'))[0]
            while float(parsed_line[0]) - trip_beginning > (datetime.now() - start_time).total_seconds():
                pass
            sp4 = sp3
            sp3 = sp2
            sp2 = sp1
            sp1 = [float(parsed_line[0]), round(float(parsed_line[1]))]
            speed.set(str(round(float(parsed_line[1]))))
            temperature.set(str(round(float(parsed_line[3]))) + "°C")
            Thread(target=redo_rpm_arc, args=(round(float(parsed_line[2])),)).start()
            if all((sp1, sp2, sp3, sp4)):
                gear_suggestion = gear_change(sp4[1], sp1[1], sp1[0] - sp4[0], round(float(parsed_line[2])), 'E')
                print(gear_suggestion)
                if gear_suggestion != gear_suggestion_before:
                    #Thread(target=gear_img, args=(gear_suggestion,)).start()
                    gear_img(gear_suggestion)
                    gear_suggestion_before = gear_suggestion
            date_time.set(datetime.fromtimestamp(round(float(parsed_line[0]))).strftime("%d/%m/%Y\n%H:%M"))


canvas = tk.Canvas(ui, bg="#526D82", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)
h = ui.winfo_screenheight()
w = ui.winfo_screenwidth()
canvas.create_oval(int(w) / 2 - 220, int(h) / 2 - 220, int(w) / 2 + 220, int(h) / 2 + 220, fill="#27374D", outline="")
speed_txt = canvas.create_text(int(w) / 2, int(h) / 2, font=Font(size=100, family="Ethnocentric Rg"), fill="#DDE6ED",
                               text=speed.get(), anchor=tk.CENTER)
temp_img = tk.PhotoImage(file="img/temperature.gif")
temperature_icon = canvas.create_image(3 * int(w) / 4, 50, anchor=tk.NE, image=temp_img)
temperature_txt = canvas.create_text(3 * int(w) / 4 + 130, 90, font=Font(size=50, family="MADE INFINITY PERSONAL USE"),
                                     fill="#DDE6ED", text=temperature.get(), anchor=tk.CENTER)
date_time_txt = canvas.create_text(50, int(h) - 150, font=Font(size=30, family="MADE INFINITY PERSONAL USE"),
                                   fill="#DDE6ED", text=date_time.get(), anchor=tk.NW)


def on_speed_change(varname, i, m) -> None:
    canvas.itemconfigure(speed_txt, text=ui.getvar(varname))


def on_temperature_change(varname, i, m) -> None:
    canvas.itemconfigure(temperature_txt, text=ui.getvar(varname))


def on_date_time_change(varname, i, m) -> None:
    canvas.itemconfigure(date_time_txt, text=ui.getvar(varname))


speed.trace_variable('w', on_speed_change)
temperature.trace_variable('w', on_temperature_change)
date_time.trace_variable('w', on_date_time_change)
todo_text = {
    "up": "↑",
    "down": "↓"
}


def gear_img(todo: Union[str, None]) -> None:
    shift_img_on_canvas = None
    if todo is not None:
        #shift_img = tk.PhotoImage(file=f"img/{todo}.gif")
        #shift_img_on_canvas = canvas.create_image(int(w) / 2 + 200, int(h) / 2 - 150, anchor=tk.NW, image=shift_img)
        shift_img_on_canvas = canvas.create_text(int(w) / 2 + 250, int(h) / 2 - 200,
                                                 font=Font(size=100, family="Arial", weight="bold"), fill="#DDE6ED",
                                                 text=f"{todo_text[todo]}", anchor=tk.CENTER)
    global GEAR_IMG
    if GEAR_IMG is not None:
        canvas.delete(GEAR_IMG)
    GEAR_IMG = shift_img_on_canvas


def redo_rpm_arc(rpm: int) -> None:
    rpm_to_scale = rpm * 0.0075
    right = canvas.create_arc(int(w) / 2 - 230, int(h) / 2 - 230, int(w) / 2 + 230, int(h) / 2 + 230, style=tk.ARC,
                              extent=str(rpm_to_scale), start=str(210 - rpm_to_scale), width=20, outline="#DDE6ED")
    left = canvas.create_arc(int(w) / 2 - 230, int(h) / 2 - 230, int(w) / 2 + 230, int(h) / 2 + 230, style=tk.ARC,
                             extent=str(rpm_to_scale), start=330, width=20, outline="#DDE6ED")
    global RPM_INDICATOR
    if None not in RPM_INDICATOR:
        canvas.delete(RPM_INDICATOR[0])
        canvas.delete(RPM_INDICATOR[1])
    RPM_INDICATOR = [left, right]


def set_date_time() -> None:
    while True:
        date_time.set(datetime.now().strftime("%d/%m/%Y\n%H:%M"))
        sleep(5)


if mode == dashboard.REPLAY:
    Thread(target=recorded_trip_loop).start()
    ui.mainloop()

if mode == dashboard.LIVE:
    Thread(target=live_trip).start()
    ui.mainloop()
