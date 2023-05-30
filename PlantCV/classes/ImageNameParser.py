import re
from datetime import datetime


class ImageNameParser:
    """
    Parses filenames with the format: z11c2--2022-12-25--09-30-01.png
    """
    def __init__(self, filename: str) -> None:
        regex = "z(\d+)c(\d)--(\d{4})-(\d{2})-(\d{2})--(\d{2})-(\d{2})-(\d{2}).png"
        self.match = re.search(regex, filename)
        if self.match is None:
            raise Exception("Couldn't parse image name")
        self.zone_number = int(self.match.group(1))
        self.camera_number = int(self.match.group(2))
        self.year = int(self.match.group(3))
        self.month = int(self.match.group(4))
        self.day = int(self.match.group(5))
        self.hour = int(self.match.group(6))
        self.minute = int(self.match.group(7))
        self.second = int(self.match.group(8))

    def get_timestamp(self) -> datetime:
        return datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
