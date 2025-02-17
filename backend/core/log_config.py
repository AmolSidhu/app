import os
import datetime
from logging.handlers import TimedRotatingFileHandler

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, log_dir, base_filename, when="midnight", interval=1, backupCount=7, encoding="utf-8", utc=True):
        self.log_dir = log_dir
        self.base_filename = base_filename
        self.update_filename()
        super().__init__(self.filename, when, interval, backupCount, encoding, utc)

    def update_filename(self):
        date_str = datetime.datetime.utcnow().strftime('%d-%m-%Y')
        self.filename = os.path.join(self.log_dir, f"{self.base_filename}-{date_str}.log")

    def doRollover(self):
        self.update_filename()
        super().doRollover()

    def getFilesToDelete(self):
        dir_name, base_name = os.path.split(self.filename)
        base_name_no_ext, ext = os.path.splitext(base_name)

        matching_files = [
            f for f in os.listdir(dir_name)
            if f.startswith(self.base_filename + "-") and f.endswith(".log")
        ]

        matching_files.sort()
        return matching_files[:-self.backupCount]
