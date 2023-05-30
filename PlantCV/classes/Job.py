import json
from pathlib import Path
from datetime import datetime, time

try:
    from TimeSetting import TimeSetting
    from ImageNameParser import ImageNameParser
except ImportError:
    from .TimeSetting import TimeSetting
    from .ImageNameParser import ImageNameParser


class Job:
    def __init__(self) -> None:
        self.zonecamera : str = None
        self.description : str = None

        self.start_timestamp : datetime = None # YYYY-MM-DD--HH-MM
        self.end_timestamp : datetime = None   # YYYY-MM-DD--HH-MM
        self.light_on_time : time = None   # HH-MM
        self.light_off_time : time = None  # HH-MM

        self.input_image_dir : Path = None
        self.output_image_dir : Path = None
        self.output_csv_file : Path = None

        self.camera_angle_paths : list = []

        self.genotype_map : TimeSetting = TimeSetting()
        self.white_spot_roi : TimeSetting = TimeSetting()
        self.plant_rois : TimeSetting = TimeSetting()
        self.size_marker_rois : TimeSetting = TimeSetting()

        self.np_average_min : int = None
        self.np_average_max : int = None

        self.upper_hsv : list = []
        self.lower_hsv : list = []
        self.mask_fill_threshold : int = None

        self.size_marker_upper_hsv : list = []
        self.size_marker_lower_hsv : list = []
        self.size_marker_fill_threshold : int = None

        self.undistort : bool = None
        self.fx : float = None
        self.cx : float = None
        self.fy : float = None
        self.cy : float = None
        self.k1 : float = None
        self.k2 : float = None
        self.k3 : float = None
        self.k4 : float = None


    def __str__(self) -> str:
        if self.zonecamera is None:
            return "z?c?"
        return self.zonecamera

    def date_in_experiment(self, timestamp: datetime) -> bool:
        if timestamp >= self.start_timestamp and timestamp <= self.end_timestamp:
            return True
        return False

    def is_light_on(self, t : time) -> bool:
        if t >= self.light_on_time and t < self.light_off_time:
            return True
        return False

    def get_zone(self) -> int:
        c_index = self.zonecamera.find("c")
        return int(self.zonecamera[1:c_index])

    def get_camera(self) -> int:
        c_index = self.zonecamera.find("c")
        return int(self.zonecamera[c_index+1:])

    def get_genotype(self, timestamp: datetime, plant_id: str) -> str:
        return self.genotype_map.get_setting(timestamp)[plant_id]

    def get_job_images(self, verbose=False, testing_mode: bool = False) -> list:
        # if testing mode, get one image from each day, otherwise get all images
        l = []
        days = []
        image_paths = self.input_image_dir.iterdir()
        for image_path in image_paths:
            image_path : Path
            image_name = image_path.name
            try:
                inp = ImageNameParser(image_name)
                timestamp = inp.get_timestamp()
                if not self.date_in_experiment(timestamp):
                    raise Exception("Timestamp not in experiment")
                if not self.is_light_on(timestamp.time()):
                    raise Exception("Time not during light on period")
                if inp.zone_number != self.get_zone():
                    raise Exception("Zone number mismatch")
                if inp.camera_number != self.get_camera():
                    raise Exception("Camera number mismatch")
            except Exception as e:
                if verbose:
                    print(f"Skipping image: {image_name}\nReason: {e}")
            else:
                if testing_mode:
                    if inp.day not in days:
                        days.append(inp.day)
                        l.append(image_path)
                else:
                    l.append(image_path)
        print(f"Found {len(l)} images in job")
        l.sort()
        return l  

    def to_json(self) -> dict:
        d = {}
        for key in self.__dict__:
            if key in ["start_timestamp", "end_timestamp"]: # datetime is not serializable
                if self.__dict__[key] != None:
                    d[key] = self.__dict__[key].strftime('%Y-%m-%d--%H-%M')
                else:
                    d[key] = None

            elif key in ["light_on_time", "light_off_time"]: # time is not serializable
                if self.__dict__[key] != None:
                    d[key] = self.__dict__[key].strftime('%H-%M')
                else:
                    d[key] = None

            elif key in ["input_image_dir", "output_image_dir", "output_csv_file"]: # Path is not serializable
                if self.__dict__[key] != None:
                    d[key] = str(self.__dict__[key])
                else:
                    d[key] = None

            elif key in ["camera_angle_paths"]: # list of Path is not serializable
                if self.__dict__[key] != []:
                    d[key] = [str(p) for p in self.__dict__[key]]
                else:
                    d[key] = []

            elif key in ["genotype_map", "white_spot_roi", "plant_rois", "size_marker_rois"]: # TimeSetting is not serializable
                if self.__dict__[key] != None:
                    d[key] = {}
                    for timesettingkey in self.__dict__[key]:
                        # each key is a tuple of datetime.datetime objects
                        start = timesettingkey[0].strftime('%Y-%m-%d--%H-%M')
                        end = timesettingkey[1].strftime('%Y-%m-%d--%H-%M')
                        d[key][start+"->"+end] = self.__dict__[key][timesettingkey]
                else:
                    d[key] = None

            else:
                d[key] = getattr(self, key)
        return d


    def from_json(self, json_dict: dict) -> None:
        for key in json_dict:
            if key in ["start_timestamp", "end_timestamp"]: # datetime is not serializable
                if json_dict[key] != None:
                    setattr(self, key, datetime.strptime(json_dict[key], '%Y-%m-%d--%H-%M'))

            elif key in ["light_on_time", "light_off_time"]: # time is not serializable
                if json_dict[key] != None:
                    setattr(self, key, datetime.strptime(json_dict[key], '%H-%M').time())

            elif key in ["input_image_dir", "output_image_dir", "output_csv_file"]: # Path is not serializable
                if json_dict[key] != None:
                    setattr(self, key, Path(json_dict[key]))

            elif key in ["camera_angle_paths"]: # list of Path is not serializable
                for str_path in json_dict[key]:
                    self.__dict__[key].append(Path(str_path))

            elif key in ["genotype_map", "white_spot_roi", "plant_rois", "size_marker_rois"]: # TimeSetting is not serializable
                for timesettingkey in json_dict[key]:
                    # each key is a tuple of datetime.datetime objects
                    start = datetime.strptime(timesettingkey.split("->")[0], '%Y-%m-%d--%H-%M')
                    end = datetime.strptime(timesettingkey.split("->")[1], '%Y-%m-%d--%H-%M')
                    self.__dict__[key][(start, end)] = json_dict[key][timesettingkey]
            else:
                setattr(self, key, json_dict[key])

    def print_undefined_job_attributes(self) -> None:
        """
        Print all attributes of a job that are not defined
        """
        # check for missing values
        print(self)
        for k,v in self.__dict__.items():
            if v in [None, "", [], {}]:
                print("missing", k)


def job_to_file(job: Job, file: Path) -> None:
    """
    Write a job object to a file

    Future: add warning if file already exists
    """
    with open(file, 'w') as f:
        json.dump(job.to_json(), f, indent=4)

def file_to_job(file: Path) -> Job:
    """
    Read a job object from a file
    """
    with open(file, 'r') as f:
        d = json.load(f)
        j = Job()
        j.from_json(d)
    return j


if __name__ == '__main__':
    pass
