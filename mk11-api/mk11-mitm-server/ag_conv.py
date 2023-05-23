from random_data import get_random_collection
import base64
import datetime
import json
from math import ceil, log


def get_size(x: object):
    if hasattr(x, "__len__"):
        if isinstance(x, str):
            data = len(x.encode())
        else:
            data = len(x)  # type: ignore
    else:
        data: int = x  # type: ignore

    if not data:
        return 1

    data = ceil(log(data, 255))

    if not data:
        return 1

    size = 2 ** ceil(log(data, 2))
    if size > 8:
        raise ValueError(f"Value is bigger than 8 bytes: {size}")
    return size


def value_to_bytes(data: int, size):
    return data.to_bytes(size, "big")


def adjust_type(type_, size, step_size = 1):
    if size:
        increment = ceil(log(size, 2))
        type_ += increment * step_size
    return type_


def obj_to_type_bytes(obj: object):
    type_: int
    size = 0
    has_extra = False
    if isinstance(obj, dict):
        type_ = 0x60
        serial_type = "map"
        has_extra = True
    elif isinstance(obj, (list, set)):
        type_ = 0x50
        serial_type = "container"
        has_extra = True
    elif isinstance(obj, str):
        type_ = 0x30
        serial_type = "value"
        has_extra = True
    elif isinstance(obj, bytes):
        type_ = 0x33
        serial_type = "value"
        has_extra = True
    elif isinstance(obj, datetime.datetime):
        type_ = 0x40
        size = 8
        serial_type = "value"
    elif obj is None:
        type_ = 1
        serial_type = "value"
    elif obj is True:
        type_ = 2
        serial_type = "value"
    elif obj is False:
        type_ = 3
        serial_type = "value"
    elif obj == 0:
        type_ = 0x11
        size = 1
        serial_type = "value"
    elif isinstance(obj, int):
        serial_type = "value"
        if obj > 0:
            type_ = 0x11
            size = get_size(obj)
            type_ = adjust_type(type_, size, 2)
        elif obj == 0:  # Impossible
            type_ = 0x0
        else:
            type_ = 0x10
            size = get_size(abs(obj))
            type_ = adjust_type(type_, size, 2)
            
    else:
        raise ValueError(f"Unsupported Object: {type(obj)}")

    if has_extra:
        size = get_size(obj)
        type_ = adjust_type(type_, size)

    type_data = value_to_bytes(type_, 1)

    if has_extra:
        data = len(obj)  # type: ignore
        extra_data = value_to_bytes(data, size)
    else:
        extra_data = b""

    return type_data + extra_data, serial_type, size

def int_to_signed_bytes(data: int, size: int):
    data = data + 2 ** (size*8)
    return data.to_bytes(size, "big")

def json_to_ag(data):
    resp, type_, size = obj_to_type_bytes(data)
    if type_ == "value":
        if size:
            if isinstance(data, str):
                add_data = data.encode()
            elif isinstance(data, int):
                if data > 0:
                    add_data = value_to_bytes(data, size)
                elif data == 0: # Impossible
                    add_data = b""
                else:
                    add_data = int_to_signed_bytes(data, size)                    
            elif isinstance(data, bytes):
                add_data = resp
            elif isinstance(data, datetime.datetime):
                add_data = value_to_bytes(int(data.timestamp() / 1000), 8)
            else:
                raise ValueError(f"Unsupported Value Type: {type(data)}")
            resp += add_data
    elif type_ == "container":
        for item in data:
            resp += json_to_ag(item)
    elif type_ == "map":
        for key, value in data.items():
            resp += json_to_ag(key)
            resp += json_to_ag(value)

    return resp


mode = "random"
# mode = "json"

if __name__ == "__main__":
    if mode == "random":
        data = get_random_collection()
        print(data)
        data = json_to_ag(data)
        print(data)
    elif mode == "json":
        with open("premium_shop.json") as file:
            data = json_to_ag(json.load(file))
            print(data)
            b64 = base64.encodebytes(data).decode().strip()
            print(b64)
    else:
        raise ValueError(f"Unsupported Mode: {mode}")