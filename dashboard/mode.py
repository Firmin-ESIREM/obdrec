class DashboardMode:
    def __init__(self, mode):
        self.mode = mode


LIVE = DashboardMode("live")
REPLAY = DashboardMode("replay")
FORZA = DashboardMode("forza")
