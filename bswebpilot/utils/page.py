from bsutils.logger.bslogger import BSLogger

from bswebpilot.base import BSWebPilotSync, BSWebPilotAsync


class BSWebPilotPage:
    pilot: BSWebPilotSync | BSWebPilotAsync
    logger: BSLogger

    def __init__(self, pilot:BSWebPilotSync | BSWebPilotAsync, logger: BSLogger):
        """
        Clase base para todas las páginas (síncrono o asíncrono).
        """
        self.pilot = pilot
        self.logger = logger



