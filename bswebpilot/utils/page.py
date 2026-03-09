from bswebpilot.base import BSWebPilotSync, BSWebPilotAsync


class BSLogger:
    pass


class BSWebPilotPage:
    def __init__(self, pilot:BSWebPilotSync | BSWebPilotAsync, logger: BSLogger):
        """
        Clase base para todas las páginas (síncrono o asíncrono).
        """
        pilot: BSWebPilotSync | BSWebPilotAsync
        logger: BSLogger



