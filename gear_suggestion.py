from typing import Union


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
    :return: 'up', 'down' or None, depending on the most fuel-economic option
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
