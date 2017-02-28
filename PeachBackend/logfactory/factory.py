import logging

class LoggerFactory:
    def __init__(self, level, logfile):
        self.level = level
        self.logfile = logfile

    def get_logger(self):
        log = logging.getLogger()
        log.setLevel(self.level)
        logfile = logging.FileHandler(self.logfile)
        log.addHandler(logfile)
        return log


