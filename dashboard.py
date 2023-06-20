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
ui.attributes("-fullscreen", True)
ui.configure(bg="black", cursor="none")
speed = tk.StringVar(ui, '0')
temperature = tk.StringVar(ui, '0°C')
date_time = tk.StringVar(ui, datetime.now().strftime("%d/%m/%Y\n%H:%M"))
gear = tk.StringVar(ui, "")
position = tk.StringVar(ui, "")
lap_time = tk.StringVar(ui, "")
RPM_INDICATOR = [None, None]
GEAR_IMG = None
ACCELERATION_GAUGE = None
BRAKING_GAUGE = None

mode = dashboard.LIVE

if len(argv) not in [2, 3] \
        or (argv[1] == "replay" and len(argv) != 3) \
        or (argv[1] == "live" and len(argv) != 2) \
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

csv_header = "time;speed_kph;rpm;intake_temperature_degC\n"


def gear_change(old_speed: int, new_speed: int, time_diff: float, rpm: int, combustion: str,
                current_gear: str = None) -> Union[str, None]:
    """
    Suggest shifting to the driver according to the situation.
    :param old_speed: speed five measures ago
    :param new_speed: current speed
    :param time_diff: time between new speed and old speed
    :param rpm: current number of rpm
    :param combustion: engine combustion type. Can be 'E' or 'D'
    :param current_gear: current gear
    :return: 'up' or 'down' or nothing
    """
    acceleration = (new_speed / 3.6 - old_speed / 3.6) / time_diff
    rpm_limit = [0, 0, 0, 0]
    if combustion == "E":  # rpm limit for petrol motorisation
        rpm_limit = [1300, 2000, 2700, 3500]
    elif combustion == "D":  # rpm limit for diesel motorisation
        rpm_limit = [1300, 2000, 2700, 3500]
    if 15 < new_speed < 90:
        if acceleration < -2 and rpm < rpm_limit[1] and current_gear != 1:
            return "down"
        if -2 < acceleration < 2:
            if rpm < rpm_limit[0] and current_gear != 1:
                return "down"
            elif rpm > rpm_limit[2]:
                return "up"
        if acceleration > 2 and rpm > rpm_limit[3]:
            return "up"
    return None


def live_trip() -> None:
    """
    Control the dashboard for live trip or for Forza.
    :return:
    """
    sp1, sp2, sp3, sp4 = None, None, None, None
    Thread(target=set_date_time).start()
    while True:
        data = loads(retrieve_udp())
        elements = data.keys()
        sp4 = sp3
        sp3 = sp2
        sp2 = sp1
        sp1 = [data["speed"], time()]
        speed.set(str(round(data["speed"])))
        if "intake_temp" in elements:
            temperature.set(str(data["intake_temp"]) + "°C")
        else:
            canvas.delete(temperature_icon)
            canvas.delete(temperature_txt)
        if "EngineMaxRpm" in elements:
            Thread(target=redo_rpm_arc, args=(data["rpm"], int(data["EngineMaxRpm"]))).start()
        else:
            Thread(target=redo_rpm_arc, args=(data["rpm"],)).start()
        if "Gear" in elements:
            if all((sp1, sp2, sp3, sp4)):
                gear_suggestion = gear_change(sp4[0], sp1[0], sp1[1] - sp4[1], data["rpm"], 'E', data["Gear"])
                Thread(target=gear_img, args=(gear_suggestion,)).start()
            gear.set(data["Gear"])
        else:
            if all((sp1, sp2, sp3, sp4)):
                gear_suggestion = gear_change(sp4[0], sp1[0], sp1[1] - sp4[1], data["rpm"], 'E')
                Thread(target=gear_img, args=(gear_suggestion,)).start()
        if "Accel" in elements:
            Thread(target=redo_acceleration_gauge, args=(data["Accel"],)).start()
        if "Brake" in elements:
            Thread(target=redo_braking_gauge, args=(data["Brake"],)).start()
        if "IsRaceOn" in elements and data["RacePosition"] != 0:
            current_lap = round(data["CurrentLap"])
            nb_seconds = current_lap % 60
            nb_minutes = (current_lap - nb_seconds) // 60
            if nb_minutes > 0:
                lap_time.set(f"Temps du tour : {nb_minutes} min {nb_seconds} s")
            else:
                lap_time.set(f"Temps du tour : {nb_seconds} s")
            position.set(f"Position : {data['RacePosition']}")
        else:
            lap_time.set("")
            position.set("")


def recorded_trip_loop() -> None:
    """
    Control the dashboard when you replay a trip.
    :return:
    """
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
                    # Thread(target=gear_img, args=(gear_suggestion,)).start()
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
gear_txt = canvas.create_text(int(w) / 2, 0.75 * int(h), font=Font(size=50, family="MADE INFINITY PERSONAL USE"),
                              fill="#DDE6ED", text=gear.get(), anchor=tk.CENTER)
position_txt = canvas.create_text(40, 40, font=Font(size=30, family="MADE INFINITY PERSONAL USE"),
                                  fill="#DDE6ED", text=position.get(), anchor=tk.NW)
lap_time_txt = canvas.create_text(40, 100, font=Font(size=30, family="MADE INFINITY PERSONAL USE"),
                                  fill="#DDE6ED", text=lap_time.get(), anchor=tk.NW)


def on_speed_change(varname, i, m) -> None:
    """
    Function needed to trace the variable speed.
    """
    canvas.itemconfigure(speed_txt, text=ui.getvar(varname))


def on_temperature_change(varname, i, m) -> None:
    """
    Function needed to trace the variable temperature.
    """
    canvas.itemconfigure(temperature_txt, text=ui.getvar(varname))


def on_date_time_change(varname, i, m) -> None:
    """
    Function needed to show the date on the dashboard.
    """
    canvas.itemconfigure(date_time_txt, text=ui.getvar(varname))


def on_gear_change(varname, i, m) -> None:
    """
    Function needed to trace the variable gear.
    """
    canvas.itemconfigure(gear_txt, text=ui.getvar(varname))


def on_lap_time_change(varname, i, m) -> None:
    """
    Function needed to trace variable lap time.
    """
    canvas.itemconfigure(lap_time_txt, text=ui.getvar(varname))


def on_position_change(varname, i, m) -> None:
    """
        Function needed to trace variable position.
    """
    canvas.itemconfigure(position_txt, text=ui.getvar(varname))


speed.trace_variable('w', on_speed_change)
temperature.trace_variable('w', on_temperature_change)
date_time.trace_variable('w', on_date_time_change)
gear.trace_variable('w', on_gear_change)
lap_time.trace_variable('w', on_lap_time_change)
position.trace_variable('w', on_position_change)
todo_text = {
    "up": "↑",
    "down": "↓"
}


def gear_img(todo: Union[str, None]) -> None:
    """
    Function needed to trace the shifting suggestion.
    """
    shift_img_on_canvas = None
    if todo is not None:
        shift_img_on_canvas = canvas.create_text(int(w) / 2 + 250, int(h) / 2 - 200,
                                                 font=Font(size=100, family="Arial", weight="bold"), fill="#DDE6ED",
                                                 text=f"{todo_text[todo]}", anchor=tk.CENTER)
    global GEAR_IMG
    if GEAR_IMG is not None:
        canvas.delete(GEAR_IMG)
    GEAR_IMG = shift_img_on_canvas


def redo_rpm_arc(rpm: int, max_rpm: int = 8000) -> None:
    """
    Function needed to trace the arc that show the rpm.
    :param rpm: Current rpm
    :param max_rpm: Maximun rpm only for Forza
    :return:
    """
    max_rpm = 1 if max_rpm == 0 else max_rpm
    rpm_to_scale = rpm * (60 / max_rpm)
    right = canvas.create_arc(int(w) / 2 - 230, int(h) / 2 - 230, int(w) / 2 + 230, int(h) / 2 + 230, style=tk.ARC,
                              extent=str(rpm_to_scale), start=str(210 - rpm_to_scale), width=20, outline="#DDE6ED")
    left = canvas.create_arc(int(w) / 2 - 230, int(h) / 2 - 230, int(w) / 2 + 230, int(h) / 2 + 230, style=tk.ARC,
                             extent=str(rpm_to_scale), start=330, width=20, outline="#DDE6ED")
    global RPM_INDICATOR
    if None not in RPM_INDICATOR:
        canvas.delete(RPM_INDICATOR[0])
        canvas.delete(RPM_INDICATOR[1])
    RPM_INDICATOR = [left, right]


def draw_gauge(value: int, pos_x: int, pos_y: int, size_x: int, size_y: int):
    """
    Function needed to trace gauges.
    """
    return canvas.create_rectangle(pos_x, pos_y + size_y * (1 - (value / 255)), pos_x + size_x, pos_y + size_y,
                                   fill="#DDE6ED", outline="")


def redo_acceleration_gauge(acceleration: int) -> None:
    """
    Function needed to trace acceleration rate. Only for Forza.
    :param acceleration: Current acceleration rate
    :return:
    """
    gauge = draw_gauge(acceleration, int(w) - 80, int(h) - 100, 15, 70)
    global ACCELERATION_GAUGE
    if ACCELERATION_GAUGE is not None:
        canvas.delete(ACCELERATION_GAUGE)
    ACCELERATION_GAUGE = gauge


def redo_braking_gauge(braking: int) -> None:
    """
    Function needed to trace braking rate. Only for Forza.
    :param braking: Current braking rate
    :return:
    """
    gauge = draw_gauge(braking, int(w) - 40, int(h) - 100, 15, 70)
    global BRAKING_GAUGE
    if BRAKING_GAUGE is not None:
        canvas.delete(BRAKING_GAUGE)
    BRAKING_GAUGE = gauge


def set_date_time() -> None:
    """
    Function needed to refresh the variable date time every 5 seconds.
    :return:
    """
    while True:
        date_time.set(datetime.now().strftime("%d/%m/%Y\n%H:%M"))
        sleep(5)


if mode == dashboard.REPLAY:
    Thread(target=recorded_trip_loop).start()
    ui.mainloop()

if mode == dashboard.LIVE:
    Thread(target=live_trip).start()
    ui.mainloop()
