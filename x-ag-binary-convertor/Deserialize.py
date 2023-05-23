import struct
from base64 import b64encode
from enum import IntEnum


class AGBool(IntEnum):
    # 0x00
    ZERO = 0
    NONE = 1
    TRUE = 2
    FALSE = 3


class AGInt(IntEnum):
    # 0x10
    INT8 = 0
    UINT8 = 1
    INT16 = 2
    UINT16 = 3
    INT32 = 4
    UINT32 = 5
    INT64 = 6
    UINT64 = 7


class AGFloat(IntEnum):
    # 0x20
    _FLT = 0
    FLOAT = 1


class AGChar(IntEnum):
    # 0x30
    CHAR8 = 0
    CHAR16 = 1
    CHAR32 = 2
    BYTES8 = 3
    BYTES16 = 4
    BYTES32 = 5


class AGTime(IntEnum):
    # 0x40
    EPOCH = 0


class AGArray(IntEnum):
    # 0x50
    ARRAY8 = 0
    ARRAY16 = 1
    ARRAY32 = 2
    ARRAY64 = 3


class AGMap(IntEnum):
    # 0x60
    MAP8 = 0
    MAP16 = 1
    MAP32 = 2
    MAP64 = 3


class AGClassEnum(IntEnum):
    BOOLS = 0x0
    INTS = 0x1
    FLOATS = 0x2
    STRINGS = 0x3
    TIME = 0x4
    ARRAYS = 0x5
    MAPS = 0x6


AGMapEnum = {
    AGClassEnum.BOOLS: AGBool,
    AGClassEnum.INTS: AGInt,
    AGClassEnum.FLOATS: AGFloat,
    AGClassEnum.STRINGS: AGChar,
    AGClassEnum.TIME: AGTime,
    AGClassEnum.ARRAYS: AGArray,
    AGClassEnum.MAPS: AGMap,
}

def bytes_to_int(data: bytes, signed:bool) -> int:
    length = len(data)
    if length == 1:
        format = 'B'
    elif length == 2:
        format = 'H'
    elif length == 4:
        format = 'I'
    elif length == 8:
        format = 'Q'
    else:
        raise ValueError(f"Wrong Size of data: {length}")
    if signed:
        format = format.lower()
    return struct.unpack(f">{format}", data)[0]

def bytes_to_float(data: bytes) -> float:
    length = len(data)
    if length == 4:
        format = 'f'
    elif length == 8:
        format = 'd'
    else:
        raise ValueError(f"Wrong Size of data: {length}")
    return struct.unpack(f">{format}", data)[0]

def parse_bools(value_type: IntEnum):
    if value_type == AGBool.ZERO:
        return "0"
    if value_type == AGBool.NONE:
        return "None"
    if value_type == AGBool.TRUE:
        return "True"
    if value_type == AGBool.FALSE:
        return "False"
    # Not Possible
    raise ValueError("Unknown Type")


def data_to_int(data: bytes, cursor: int, length: int, signed = False):
    data = data[cursor : cursor + length]
    return bytes_to_int(data, signed)


def parse_ints(data: bytes, cursor: int, data_sub_type):
    data_length = 2 ** (data_sub_type // 2)
    is_signed = not bool(data_sub_type % 2)
    value = data_to_int(data, cursor, data_length, is_signed)
    cursor += data_length
    return str(value), cursor


def parse_strings(data: bytes, cursor: int, data_sub_type):
    is_binary = data_sub_type > 2
    if is_binary:
        data_sub_type -= 3
    data_length = 2 ** data_sub_type
    string_length = data_to_int(data, cursor, data_length)
    cursor += data_length
    string_data = data[cursor : cursor + string_length]
    if is_binary:
        string_data = b64encode(string_data).decode('utf-8')
    else:
        string_data = string_data.decode("utf-8").replace('\"', '\\\"')
    cursor += string_length
    return '"' + string_data + '"', cursor


def parse_arrays(data, cursor, data_sub_type):
    data_length = 2 ** data_sub_type
    elements_count = data_to_int(data, cursor, data_length)
    cursor += data_length
    elements = []
    for _ in range(elements_count):
        element, cursor = parse_general(data, cursor)
        elements.append(element)
    return "[" + ",".join(elements) + "]", cursor


def parse_maps(data, cursor, data_sub_type):
    data_length = 2 ** data_sub_type
    elements_count = data_to_int(data, cursor, data_length)
    cursor += data_length
    elements = []
    for _ in range(elements_count):
        key, cursor = parse_general(data, cursor)
        val, cursor = parse_general(data, cursor)
        string = f"{key}:{val}"
        elements.append(string)
    return "{" + ",".join(elements) + "}", cursor


def parse_time(data, cursor, data_sub_type):
    if data_sub_type != AGTime.EPOCH:
        raise NotImplementedError(f"Only {str(AGTime.EPOCH)} time is supported!")
    data_length = 4
    time_ = data_to_int(data, cursor, data_length)
    cursor += data_length
    return str(time_), cursor

def parse_floats(data, cursor, data_sub_type):
    data_length = 2 ** (data_sub_type + 2)
    float_value = data[cursor:cursor+data_length]
    cursor += data_length
    if data_sub_type not in [0, 1]:
        raise NotImplementedError(f"Sub Type {str(get_subtype(data_sub_type))} is not supported!")
    parsed_float = bytes_to_float(float_value)
    return str(parsed_float), cursor

def parse_general(data, cursor):
    var = data[cursor]
    data_type = var // 0x10
    data_sub_type = var % 0x10
    value_type = get_subtype(var)
    # print(data_type, data_sub_type, AGClassEnum(data_type), value_type)
    cursor += 1
    if data_type == AGClassEnum.BOOLS:
        return parse_bools(value_type), cursor
    elif data_type == AGClassEnum.INTS:
        return parse_ints(data, cursor, data_sub_type)
    elif data_type == AGClassEnum.FLOATS:
        return parse_floats(data, cursor, data_sub_type)
    elif data_type == AGClassEnum.STRINGS:
        return parse_strings(data, cursor, data_sub_type)
    elif data_type == AGClassEnum.TIME:
        return parse_time(data, cursor, data_sub_type)
    elif data_type == AGClassEnum.ARRAYS:
        return parse_arrays(data, cursor, data_sub_type)
    elif data_type == AGClassEnum.MAPS:
        return parse_maps(data, cursor, data_sub_type)
    raise NotImplementedError(f"{str(AGClassEnum(data_type))} is not yet implemented.")

def deserialize(data: bytes):
    if not data:
        raise ValueError("Missing Data!")
    cursor: int = 0
    parsed_string = ""
    # while cursor < len(data): # Shouldn't be a while loop
    string, cursor = parse_general(data, cursor)
    parsed_string += string

    return eval(parsed_string)


def get_subtype(value) -> IntEnum:
    type, subtype = value // 0x10, value % 0x10
    return AGMapEnum[AGClassEnum(type)](subtype)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 deserialize.py <file>")
        exit(1)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
        # Compare first 4 bytes with magic number
        MAGIC = bytes.fromhex("E3 61 45 90")
        if data[:4] == MAGIC:
            print("Found a Save File!")
            data = data[6:]
        
        deserialized_data = deserialize(data)

    if len(sys.argv) > 2:
        save_to = sys.argv[2]
        print(f"Saving to {save_to}")
        with open(sys.argv[2], "w") as f:
            f.write(str(deserialized_data))
    else:
        print(deserialized_data)
