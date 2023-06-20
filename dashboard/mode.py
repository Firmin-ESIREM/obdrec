class DashboardMode:
    def __init__(self, mode):
        """
        Initialize the dashboard mode class.
        :param mode:
        """
        self.mode = mode


LIVE = DashboardMode("live")
REPLAY = DashboardMode("replay")
