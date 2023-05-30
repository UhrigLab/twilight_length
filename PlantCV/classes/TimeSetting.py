import pprint
from datetime import datetime


class TimeSetting(dict):
    """
    Represents a setting that changes over time, such as plant, white spot, and size marker rois 
    if the camera or plants are moved at some point in the experiment.
    """
    def __init__(self, range_setting_dict: dict = {}) -> None:
        """
        Format of range_setting_dict:
        note that each key is a tuple of datetime.datetime objects
        {
            (experiment_start, some_time): setting,
            (some_time, some_other_time): new_setting,
            (some_other_time, experiment_end): different_setting,
        }
        'setting' is valid from 'experiment_start' to 'some_time'
        'new_setting' is valid from 'some_time' to 'some_other_time'
        'different_setting' is valid from 'some_other_time' to 'experiment_end'
        """
        super().__init__(range_setting_dict)

    def __str__(self) -> str:
        return pprint.pformat(self)

    def get_setting(self, timestamp: datetime):
        for key in self:
            if timestamp >= key[0] and timestamp < key[1]:
                return self[key]

    def check_coverage(self) -> bool:
        if self == {}:
            return True
        current = list(self.keys())[0][0]
        while current != list(self.keys())[-1][1]:
            found = False
            for tup in self:
                if tup[0] == current:
                    current = tup[1]
                    found = True
                    break
            if not found:
                return False
        return True

    def add_setting(self, setting_start: datetime, setting_end: datetime, setting):
        self[(setting_start, setting_end)] = setting

    def remove_setting(self, setting_start: datetime, setting_end: datetime):
        self.pop((setting_start, setting_end))


if __name__ == '__main__':
    empty = TimeSetting()
    print(empty == {})