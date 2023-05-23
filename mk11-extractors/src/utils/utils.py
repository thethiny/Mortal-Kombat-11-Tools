import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import unicodedata
from enum import Enum
from os.path import isfile
from pydoc import locate
from typing import (Any, Dict, List, Literal, Mapping, MutableMapping, Set,
                    Tuple, Type, TypedDict, Union)

from src.common import _TD
from src.validators.MK11Api import KEY_MAPS


def dummy_pylance() -> Any:
    return


def hashfile(path):
    with open(path, "rb") as file:
        file_hash = hashlib.sha1(file.read()).hexdigest()
        return file_hash


def hashdata(data):
    return hashlib.sha1(data).hexdigest()


def is_full_match(pattern: re.Pattern, string):
    match = pattern.match(string)
    return match and len(string) == match.span()[1]


def io_pattern(pattern, action, *args):
    for f in glob.glob(pattern):
        action(f, *args)


def delete_pattern(pattern):
    io_pattern(pattern, os.remove)


def move_pattern(pattern, *args):
    io_pattern(pattern, shutil.move, *args)


def create_folders(folder, file=False):
    if file:
        folder = folder.replace("\\", "/").rsplit("/", 1)[0]
    if not os.path.isdir(folder):
        os.makedirs(folder)


def copy_file(location, destination):
    create_folders(destination)

    file_name = location.replace("\\", "/").rsplit("/")[-1]

    copy_destination = os.path.join(destination, file_name)
    if isfile(os.path.join(location, copy_destination)):
        os.remove(os.path.join(location, copy_destination))
    shutil.copy2(location, copy_destination)
    return copy_destination


def windows_escape(path):
    if isinstance(path, str) and " " in path:
        return f'"{path}"'
    return path


def execute_exe(exe, *args, redirect_out="", redirect_err="", silent=False):
    string_args = " ".join([windows_escape(arg) for arg in args])
    string = windows_escape(exe) + " " + string_args
    if silent:
        string += " > NUL 2>&1"
    else:
        if redirect_out:
            string += f" > {windows_escape(redirect_out)}"
        if redirect_err:
            string += f" 2> {windows_escape(redirect_err)}"
    os.system(string)


def create_socket_endpoint(protocol, address, port):
    return f"{protocol}://{address}:{port}"


def is_typeddict_instance(cls):
    return isinstance(cls, (TypedDict.__class__))  # type: ignore


def separate_cases(string):
    return " ".join(
        [l.strip() for l in re.findall("[A-Z]*[^A-Z]*", string) if l.strip()]
    ).strip()


def separate_digits(string):
    return " ".join(
        [l.strip() for l in re.findall("[0-9]*[^0-9]*", string) if l.strip()]
    ).strip()


def iter_typeddict(cls: Type[_TD]):
    for key, type_ in cls.__annotations__.items():
        yield key, type_


def get_dir(path):
    path = path.replace("\\", "/")
    return path.rsplit("/", 1)[0]


def get_literal_values(cls: Type[_TD], key: str) -> List:
    return eval(str(cls.__annotations__[key]).split("Literal")[-1])


def get_typeddict_items(
    cls, data_dict=None, remap=True, recurse=True, fill_missing=True, **kwargs
):
    # Parse KWArgs and Dict
    data_dict = data_dict or {}
    for k, v in kwargs.items():
        if remap:
            k = KEY_MAPS.get(k, k)  # Map if exists
        data_dict[k] = v

    insert_dict: cls = {}
    for key, type_ in iter_typeddict(cls):
        if remap:
            key = KEY_MAPS.get(key, key)  # Map if exists

        if key in kwargs:  # Override
            insert_dict[key] = kwargs[key]
            continue

        og_type = type_
        values = []
        if str(og_type).startswith("typing.Union["):
            type_ = str(type_)[13:-1]
            # Need to handle Type[] such as Next Elif
            types = [t.strip() for t in type_.split(",")]
            if "NoneType" in types:
                type_ = None
            else:
                type_ = random.choice(types)
                type_ = locate(type_)
        elif str(og_type).startswith("typing.Literal["):
            type_ = str(type_)[15:-1]
            values = [val.strip()[1:-1] for val in type_.split(",", 1)]
            type_ = Literal
        elif str(og_type)[-1] == "]":
            type_ = str(type_).split("[", 1)[0]
            type_ = locate(type_)
        if 0:
            if og_type != type_:
                print(f"{key} -> {og_type} -> {type_}")
            else:
                print(f"{key} -> {type_}")

        is_single_val = True
        if type_ == List:
            val = []
        elif type_ == Tuple:
            val = ()
        elif type_ in (Dict, dict, MutableMapping, Mapping, Set):
            val = {}
        elif type_ == Literal:
            val = values[0]
        elif type_ == str:
            val = ""
        elif type_ in (int, float):
            val = 0
        elif type_ == bool:
            val = False
        elif type_ in [Any, None, type(None)]:
            val = None
        elif isinstance(type_, (TypedDict.__class__)):  # type: ignore
            if recurse:
                val = get_typeddict_items(
                    type_, data_dict.get(key, {}), remap, recurse, fill_missing
                )
                is_single_val = False
            else:
                val = data_dict.get(key, {})
        elif key in data_dict:
            val = data_dict[key]  # Unknown type
        # elif issubclass(type_, Enum):
        #     val = type_("")
        else:
            # raise NotImplementedError(f"Unsupported Type: {type_}")
            val = type_()  # type: ignore
        if is_single_val and key in data_dict:
            insert_dict[key] = data_dict[key]
        else:
            if fill_missing or not is_single_val:
                insert_dict[key] = val
            else:
                ...

    return insert_dict


def get_typeddict_items_file(Type: Type[_TD], file_name, data_dict=None, **kwargs):
    if isfile(file_name):
        with open(file_name, encoding="utf-8") as file:
            try:
                file_j: dict = json.load(file, object_hook=ExtendedEncoder.as_enum)
            except json.JSONDecodeError:
                file_j = {}
    else:
        file_j = {}

    return get_typeddict_items(Type, data_dict, **file_j, **kwargs)


def set_typeddict_items_file(Type, file_name, data_dict=None, **kwargs):
    data_dict = data_dict or {}
    data = get_typeddict_items(Type, data_dict, **kwargs)
    with open(file_name, "w+", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4, cls=ExtendedEncoder)


def is_enum(obj, enums: Union[Tuple[Enum], Enum]):
    if not isinstance(enums, (tuple, list)):
        enums = (enums,)
    for enum in enums:
        if obj in [enum, enum.value]:
            return True
    return False


def little_endian_to_int(data: bytes):
    return int("".join([f"{hex(i)[2:]:0>2}" for i in data[::-1]]), 16)


def big_endian_to_int(data: bytes):
    return int("".join([f"{hex(i)[2:]:0>2}" for i in data[:]]), 16)


def check_process(process):
    call_string = "TASKLIST", "/FI", f"imagename eq {process}"
    output = subprocess.check_output(call_string)
    output = decode_unknown(output).strip()
    output = output.split("\n")[-1]
    output = output.split()[0]
    return output.lower() == process.lower()


supported_encodings = ["utf-8", "cp1252", "cp1256", "utf-16-le", "cp850"] # Standard, Windows, WindowsArabic, Wide, Spanish


def decode_unknown(string: bytes) -> str:
    if isinstance(string, str):
        return string
    for encoding in supported_encodings:
        try:
            return string.decode(encoding)
        except UnicodeDecodeError:
            pass
        except AttributeError:
            raise AttributeError(
                f"Please specify a string or bytes! {type(string)} is not allowed!"
            )
    raise ValueError("Failed to determine encoding. Please notify thethiny to add support for this encoding.")


class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
            # return {"__enum__": {"class": obj.__class__.__name__, "name": obj.name, "value": obj.value}}
        return json.JSONEncoder.default(self, obj)

    @classmethod
    def as_enum(cls, d):  # Improper
        enum_ = d.get("__enum__", None)
        if enum_:
            # return eval(f"{enum_['class']}.{enum_['name']}")
            return enum_["value"]
        return d


def istypeddict(__obj: Mapping, __class_or_tuple: Union[Type[TypedDict], Tuple[Type[TypedDict]]]) -> bool:
    if not isinstance(__class_or_tuple, Tuple):
        __class_or_tuple = (__class_or_tuple,)
    for comp in __class_or_tuple:
        equal: bool = True
        for key, type_ in iter_typeddict(comp): # type: ignore
            if key not in __obj:
                equal = False
                break
        if equal:
            return True
    return False

def sanitize_path(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'(?i)[^\w\s\-\.]', '', value)
    return re.sub(r'(?i)[-\s]+', '-', value).strip()
