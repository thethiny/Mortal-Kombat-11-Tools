from enum import Enum
import builtins
import json
from datetime import datetime
from os import makedirs
from os.path import isdir, join
from uuid import uuid4
import yaml
import functools


def fix_path_slash(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).replace("/", "\\")

    return wrapper


class GenericLogger:
    def __init__(self, name=None, version=None):
        self.name = name or "Logger"
        self.version = version or "0.0.0"
        self.launch_time = self.get_timestamp()
        self.log_dir = "logs"
        self.init()

    def get_timestamp(self):
        return int(datetime.now().timestamp())

    @fix_path_slash
    def get_log_dir(self):
        return join(self.log_dir, f"{self.name}_{self.version}/{self.launch_time}")

    @fix_path_slash
    def get_log_file_name(self):
        return f"{self.name}_{self.version}_{self.launch_time}.log"

    @fix_path_slash
    def get_json_file_name(self, json_name: str = ""):
        file_id = uuid4().hex[:10]
        names = (
            [str(self.get_timestamp())] + ([json_name] if json_name else []) + [file_id]
        )
        file_out = "_".join(names) + ".json"
        return join(self.get_log_dir(), file_out)

    def init(self):
        file_name = self.get_log_dir()
        if not isdir(file_name):
            makedirs(file_name)
        self.file_handle = None

    def write(self, string: str):
        if not self.file_handle:  # Create file only on write
            self.file_handle = open(
                join(self.get_log_dir(), self.get_log_file_name()),
                "w+",
                encoding="utf-8",
            )
        self.file_handle.write(f"{string}\n")
        self.file_handle.flush()

    def print(self, *args, **kwargs):
        display_args = []
        parsed_args = []
        json_name = kwargs.pop("json_name", "")
        for arg in args:
            jsonify = (
                isinstance(arg, dict)
                or (isinstance(arg, list) and arg and isinstance(arg[0], dict))
                or (isinstance(arg, list) and len(arg) > 10)
            )
            if kwargs.get("pretty", False) and jsonify:
                display_args.append(yaml.dump(arg, default_flow_style=False))
            else:
                string_arg = str(arg)
                if len(string_arg) > 256:  # Too Big to display
                    display_args.append(f"{string_arg[:64]} ... {string_arg[-64:]}")
                else:
                    display_args.append(string_arg)
            if jsonify:
                new_arg = self.get_json_file_name(json_name)
                json_h = open(new_arg, "w+", encoding="utf-8")
                json.dump(arg, json_h, indent=4, ensure_ascii=False, cls=ExtendedEncoder)
                parsed_args.append(new_arg)
            else:
                parsed_args.append(arg)

        self.write(" ".join([str(arg) for arg in parsed_args]))

        builtins.print(*display_args, **kwargs)

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return repr(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
