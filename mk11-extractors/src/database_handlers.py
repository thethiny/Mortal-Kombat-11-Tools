import os
import re
import shutil
from ast import Bytes
from os.path import join
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from src.common import ItemTypeEnum, KollectionTypeEnum, print
from src.items import (CHARACTERS, create_item_name, parse_buttons,
                       parse_item_type, parse_kollection_name,
                       parse_kollection_type, parse_unlockable_name,
                       parse_unlockable_type)
from src.utils.utils import (copy_file, create_folders, execute_exe,
                             get_typeddict_items, get_typeddict_items_file,
                             hashdata, hashfile, little_endian_to_int,
                             separate_digits, set_typeddict_items_file)
from src.validators.MK11Items import (MK11CharacterDataType,
                                      MK11EquipmentItemNameType,
                                      MK11EquipmentItemType,
                                      MK11EquipmentNameType, MK11EquipmentType,
                                      MK11KollectionDetailsType,
                                      MK11KollectionGalleryType,
                                      MK11KollectionItemType,
                                      MK11KollectionMItemType,
                                      MK11KollectionSaveItemType,
                                      MK11KollectionsDataType,
                                      MK11KollectionsSaveDataType,
                                      MK11KollectionsType,
                                      MK11NamedItemsDataType,
                                      MK11NamedItemsType, MK11NamedItemType,
                                      MK11UnlockablesDataType,
                                      MK11UnlockablesType)


class Database:

    # Overloads
    def __init__(self, cur_dir="", version="1.0"):
        self.init_config(version)
        self.init_paths(cur_dir)
        self.init_values()

    def init_paths(self, cur_dir):
        self.WORKDIR = cur_dir or os.getcwd()

        self.data_folder = join(self.WORKDIR, "extracted_data")
        self.items_folder = join(self.data_folder, self.TYPE)
        self.temporary_folder = join(self.data_folder, f"{self.__class__.__name__}.temp")

        self.tools_folder = join(self.WORKDIR, "tools")
        self.decompressor = join(self.tools_folder, "mk11_decompressor")
        self.dfp_slayer = join(self.tools_folder, "dfpslayer")
        self.equipment_extractor = join(self.tools_folder, "extractMK11")
        self.json_convertor = join(self.tools_folder, "DatabaseExtractor")

        self.items_file = f"{self.TYPE}.json"

    def init_config(self, version):
        self.TYPE = self.__class__.__name__
        self.VERSION = version
        self.DataType: Type = Any

    def init_values(self):
        self.dfp_string = b"mcnxyxcmvmcxyxcmskdldkjshagsdhfj"

    def handle(self, path):
        path = self.validate_path(path)
        self.validate_file(path)

    # Overrides

    def decompress(self, *args, **kwargs) -> Any:
        raise AssertionError(
            f"Function {self.decompress.__name__} should be overrided!"
        )

    def extract(self, *args, **kwargs) -> Any:
        raise AssertionError(f"Function {self.extract.__name__} should be overrided!")

    def parse(self, *args, **kwargs) -> Any:
        raise AssertionError(f"Function {self.parse.__name__} should be overrided!")

    def read(self, *args, **kwargs) -> Any:
        raise AssertionError(f"Function {self.read.__name__} should be overrided!")

    def create_data(self, *args, **kwargs) -> Any:
        raise AssertionError(
            f"Function {self.create_data.__name__} should be overrided!"
        )

    # Common

    def save_data(self, data_type, save_path, data):
        set_typeddict_items_file(data_type, save_path, data)

    def get_save_location(self, hash):
        create_folders(self.items_folder)
        hashed_file = self.get_hashed_file_name(hash)
        location = join(self.items_folder, hashed_file)
        return location

    def get_hashed_file_name(self, file_hash):
        return f"{file_hash}_{self.items_file}"

    def is_dfp(self, file_path):
        file = open(file_path, "rb")
        file.seek(-0x20, 2)
        is_dfp = file.read(0x20) == self.dfp_string
        file.close()
        return is_dfp

    def decrypt_dfp(self, path):
        self.validate_file(path)
        copied_file = copy_file(path, self.temporary_folder)
        os.chdir(self.temporary_folder)

        _, file = self.get_file_structure(path)

        if self.is_dfp(file):
            execute_exe(self.dfp_slayer, file, silent=True)
        else:
            shutil.copy2(file, file + ".decrypted")

        self.chdir_homedir()

        return copied_file + ".decrypted"

    def decompress_file(self, file_name, silence=True):
        print(f"Decompressing...")
        os.chdir(self.temporary_folder)
        self.validate_file(file_name)

        _, file_name = self.get_file_structure(file_name)

        execute_exe(self.decompressor, file_name, silent=silence)

        self.chdir_homedir()

        return file_name.rsplit(".", 1)[0] + ".unp"  # Replace extension with unp

    def database_to_json(self, file_name, silence=True):
        print(f"Converting {file_name} to json")
        os.chdir(self.temporary_folder)
        self.validate_file(file_name)

        _, file_name = self.get_file_structure(file_name)

        execute_exe(self.json_convertor, file_name, silent=silence)

        self.chdir_homedir()

        return join(self.temporary_folder, "out.json")

    def chdir_homedir(self):
        os.chdir(self.WORKDIR)

    def hash_me(self, path, *hashobjects):
        hashes = ""
        if path:
            hashes += self.hashfile(path)
        if hashobjects:
            hashes += self.hashdata(hashobjects)
        return hashes

    def is_prepared(self, save_path):
        try:
            data = get_typeddict_items_file(self.DataType, save_path)
            if data.get("version", "") == self.VERSION:
                return data
            return None
        except FileNotFoundError:
            return None
        except OSError as e:
            print(f"Failed to load {save_path}!")
            raise

    def process(self, file_location, *hashobjects):
        self.chdir_homedir()
        create_folders(self.temporary_folder)
        if file_location:
            print(f"Processing {self.TYPE} File:", file_location)
        else:
            print(f"Combining {self.TYPE} Data")
        file_location = self.validate_path(file_location)
        try:
            file_hash = self.hash_me(file_location, *hashobjects)
            save_path = self.get_save_location(file_hash)
            data: self.DataType = self.is_prepared(save_path)  # type: ignore
            if data:
                print(
                    f"File {self.get_file_structure(file_location)[-1] if file_location else self.TYPE} is already prepared at {save_path}"
                )
            else:
                items = self.handle(file_location, *hashobjects)
                data = self.create_data(items)
                self.save_data(self.DataType, save_path, data)
        except Exception:
            self.cleanup()
            raise
        self.cleanup()
        return data

    def cleanup(self):
        self.chdir_homedir()
        try:
            shutil.rmtree(self.temporary_folder)
        except FileNotFoundError:
            pass

    @classmethod
    def get_file_structure(cls, path):
        path = cls.validate_path(path)
        data = path.rsplit("/", 1)
        if len(data) == 1:
            return "", data[0]
        return path.rsplit("/", 1)

    @classmethod
    def validate_file(cls, path):
        if not os.path.isfile(path) and not os.path.isdir(path):
            raise FileNotFoundError

    @classmethod
    def validate_path(cls, path):
        if not path:
            return path
        return path.replace("\\", "/")

    @classmethod
    def toSigned32(cls, n):
        n = n & 0xFFFFFFFF
        return n | (-(n & 0x80000000))

    @classmethod
    def hashfile(cls, location):
        return hashfile(location)[:10]

    @classmethod
    def hashdata(cls, data: Union[Bytes, int, Any]):
        MAX_HASH = 10
        if not data:
            return hashdata(bytes([0]))
        if isinstance(data, list):
            data_ = data[0]
            if isinstance(data_, int):
                data = bytes(data)
            elif isinstance(data_, Bytes):
                data_ = bytes()
                for b in data:
                    data_ += b
                data = data_
            else:
                data = "".join([str(b) for b in data])

        if isinstance(data, bytes):
            pass
        elif isinstance(data, int):
            data = bytes([data])
        else:
            data = bytes([ord(l) % 256 for l in str(data)])

        return hashdata(data)[:MAX_HASH]


class Coalesced(Database):
    def __init__(self, cur_dir=""):
        self.__init_aes()
        super().__init__(cur_dir, "2.0.2")

    def init_config(self, version):
        super().init_config(version)
        self.DataType = MK11EquipmentNameType

    def decompress(self, path):
        dedfp_path = self.decrypt_dfp(path)
        return self.aes_decrypt(dedfp_path)

    def create_data(self, data):
        return get_typeddict_items(
            MK11EquipmentNameType,
            characters=data[0],
            kollections=data[1],
            version=self.VERSION,
        )

    def parse_unlockables(self, unlockables_data: List[str]):
        unlockable_items = {}
        kollection_type = None
        for line in unlockables_data:
            line = line.strip()
            if not line:
                continue
            if line.startswith(";"):
                continue
            if line.startswith("["):
                if line.startswith("[Kollection."):
                    kollection_type = line.split(".", 1)[-1].split("]", 1)[0]
                    unlockable_items.setdefault(kollection_type, {})
                    continue
                else:
                    kollection_type = None
                    continue
            if kollection_type:
                if "=" not in line:
                    continue
                subtype, subtype_name = line.split("=")
                if "." in subtype:
                    subtype, subtype_value = subtype.split(".", 1)
                    if subtype in unlockable_items[kollection_type] and not isinstance(
                        unlockable_items[kollection_type][subtype], dict
                    ):
                        unlockable_items[kollection_type][subtype] = {}
                    else:
                        unlockable_items[kollection_type].setdefault(subtype, {})
                    unlockable_items[kollection_type][subtype][
                        subtype_value
                    ] = subtype_name
                else:
                    unlockable_items[kollection_type].setdefault(
                        subtype, subtype_name
                    )  # Only if doesn't exist
                continue
        return unlockable_items

    def parse_equipment(self, equipment_data: List[str]):
        char_items: MK11CharacterDataType = {}
        character: Optional[str] = None
        is_attr: bool = False
        for line in equipment_data:
            line = line.strip()
            if not line:
                continue
            if line.startswith(";"):
                continue
            if line.startswith("[Inventory."):
                char = line.split(".", 1)[-1].split("]", 1)[0]
                is_attr = False

                if len(char) == 3:
                    character = char
                elif char == "Attributes":
                    is_attr = True
                elif char == "None":
                    character = "ALL"
                else:
                    continue

                if character:  # Always true
                    char_items.setdefault(character, {})
                continue
            if not character:
                continue
            if "=" not in line:
                continue
            item_id, item_name = line.split("=", 1)
            item_id = item_id.strip()
            item_name = item_name.strip()

            if "_" in item_id:
                assumed_item_id, assumed_item_type = item_id.rsplit("_", 1)
            else:
                assumed_item_id = item_id
                assumed_item_type = ""
            found_attributes = re.findall(
                r"Description|Flavor[0-9]+|MoveInfo", assumed_item_type
            )
            for item_type in found_attributes:
                if item_type == "Description":
                    char_items[character][assumed_item_id]["item_misc"][
                        "Description"
                    ] = item_name
                elif item_type == "MoveInfo":
                    char_items[character][assumed_item_id]["item_misc"][
                        "MoveInfo"
                    ] = item_name
                elif item_type.startswith("Flavor"):
                    flavor_id = re.split(r"([0-9]+)", item_type)[1]
                    char_items[character][assumed_item_id]["item_misc"]["Flavor"][
                        flavor_id
                    ] = item_name
                else:
                    # Never
                    pass
            else:
                item: MK11EquipmentItemNameType = get_typeddict_items(
                    MK11EquipmentItemNameType, item_name=item_name
                )

                if is_attr:
                    try:
                        char_items[character][item_id]["attributes"] = item_name
                    except KeyError:
                        i = 1
                        while f"{item_id}_{i}" in char_items[character]:
                            char_items[character][f"{item_id}_{i}"][
                                "attributes"
                            ] = item_name
                            i += 1
                else:
                    char_items[character][item_id] = item

        return char_items

    def handle(self, path):
        super().handle(path)  # For Validation
        decompressed_data = self.decompress(path)
        data = self.extract(decompressed_data)
        parsed_data = self.parse(*data)
        return parsed_data

    def read(self):
        pass

    def parse(self, equipment_data: List[str], kollections_data: List[str]):
        equipment = self.parse_equipment(equipment_data)
        kollections = self.parse_unlockables(kollections_data)
        return equipment, kollections

    def extract(self, data):
        equipment_names = []
        equipment_counter = 0
        kollections_names = []
        kollections_counter = 0
        files = int.from_bytes(data[:4], byteorder="little") // 2
        for _ in range(files):
            name_len = self.toSigned32(int.from_bytes(data[4:8], byteorder="little"))
            name_len = abs(name_len) * 2
            name = data[8 : 8 + name_len].decode("utf-16").replace("\0", "")
            equipment_file = re.search("mk11itemdefinitions[.].*$", name.lower())
            kollections_file = re.search("mk11game[.].*$", name.lower())
            data_len = self.toSigned32(
                int.from_bytes(
                    data[8 + name_len : 8 + name_len + 4], byteorder="little"
                )
            )
            data_len = abs(data_len) * 2
            if equipment_file:
                equipment_counter += 1
                text_data = data[8 + name_len + 4 : 8 + name_len + 4 + data_len].decode(
                    "utf-16"
                )
                text_data = text_data.replace("\0", "").strip()
                if text_data:
                    equipment_names += [
                        t.strip() for t in text_data.split("\n") if t.strip()
                    ]
            elif kollections_file:
                kollections_counter += 1
                text_data = data[8 + name_len + 4 : 8 + name_len + 4 + data_len].decode(
                    "utf-16"
                )
                text_data = text_data.replace("\0", "").strip()
                if text_data:
                    kollections_names += [
                        t.strip() for t in text_data.split("\n") if t.strip()
                    ]

            data = data[8 + name_len + 4 + data_len - 4 :]

        print(
            f"Extracted {equipment_counter} Equipment | {kollections_counter} Kollection files."
        )
        return equipment_names, kollections_names

    def __init_aes(self):
        self.AES_KEY = b"\x93\xBB\x69\xDF\x37\xD5\x38\x57\xB8\x6B\x20\xE1\x45\xCB\xA0\x61\xDD\x7D\xCF\xED\x3A\xAC\xF2\xDB\x29\x35\x91\x6C\x27\x66\x0B\xAF"
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.AES_KEY), modes.ECB(), backend=backend)
        self.decryptor = cipher.decryptor()

    def aes_decrypt(
        self,
        data: Union[bytes, str],
    ):
        if isinstance(data, (str)):
            with open(data, "rb") as file:
                decrypt_data = file.read()
        else:
            decrypt_data = data
        # the buffer needs to be at least len(data) + n - 1 where n is cipher/mode block size in bytes
        buffer = bytearray(len(decrypt_data) + len(self.AES_KEY) - 1)
        len_decrypted = self.decryptor.update_into(decrypt_data, buffer)
        decrypted_data = bytes(buffer[:len_decrypted]) + self.decryptor.finalize()
        return decrypted_data


class ItemsDatabase(Database):
    def __init__(self, cur_dir=""):
        super().__init__(cur_dir, "1.1")

    def init_paths(self, cur_dir):
        super().init_paths(cur_dir)
        self.database_reader = join(self.tools_folder, "read_database_lazy")

    def init_config(self, version):
        super().init_config(version)
        self.DataType = MK11EquipmentType

    def read(self, equipment_subfile):
        print("Reading...")
        os.chdir(self.temporary_folder)
        self.validate_file(equipment_subfile)

        execute_exe(
            self.database_reader, equipment_subfile, redirect_out=self.items_file
        )

        if not os.path.getsize(self.items_file):
            raise ValueError("Error while attempting to extract items from database!")

        out_file_path = join(self.temporary_folder, self.items_file)

        self.chdir_homedir()

        return out_file_path

    def handle(self, path):
        super().handle(path)  # For Validation
        decompressed_file = self.decompress(path)
        extracted_path = self.extract(decompressed_file)
        data_path = self.read(extracted_path)
        data = self.parse(data_path)
        return data

    def decompress(self, path):
        dedfp_path = self.decrypt_dfp(path)
        decompressed_file = self.decompress_file(dedfp_path)
        return decompressed_file

    def parse(self, path) -> Dict[str, MK11EquipmentItemType]:
        try:
            file = open(path, encoding="utf-8")
        except Exception:
            try:
                file = open(path, encoding="utf-16-le")
            except Exception:
                raise Exception("Couldn't read Items Databse.")
        GUIDs: List[str] = []
        items = {}
        print("Parsing Database")
        l_type: str
        l_data: str
        for line in file:
            l_type, l_data = line.split(": ", 1)
            l_type = l_type.strip()
            l_data = l_data.strip()
            if l_type.lower() == "guid":
                GUIDs.append(l_data.upper())
            elif l_type.lower() == "name":
                item_slug = GUIDs[0]
                if item_slug not in items:
                    equipItem: MK11EquipmentItemType = get_typeddict_items(
                        MK11EquipmentItemType, item_id=l_data, item_definition=GUIDs[-1]
                    )
                    items[item_slug] = equipItem
                GUIDs = []
            else:
                continue  # Unknown
        return items

    def create_data(self, data) -> MK11EquipmentType:
        return get_typeddict_items(
            MK11EquipmentType, item_slugs=data, version=self.VERSION
        )

    def extract(self, file_path):
        print(f"Extracting...")
        os.chdir(self.temporary_folder)
        self.validate_file(file_path)
        create_folders("database")

        path_to_file, file = self.get_file_structure(file_path)

        execute_exe(self.equipment_extractor, file, silent=True)

        self.chdir_homedir()

        return join(path_to_file, "database", "output_3.seg")


class NamedItems(Database):
    def __init__(self, cur_dir=""):
        super().__init__(cur_dir=cur_dir, version="1.1.3")

    def init_config(self, version):
        super().init_config(version)
        self.DataType = MK11NamedItemsType

    def find_item_in_chars(
        self, item_id: str, chars: MK11CharacterDataType
    ) -> Tuple[Optional[MK11EquipmentItemNameType], Optional[str]]:
        # Attempt to save time
        guess_name = item_id.split("_", 1)[0]
        item = chars.get(guess_name, {})
        if item and item_id in item:
            return item[item_id], guess_name

        for char_name, item_ids in chars.items():
            for char_item_id, item_data in item_ids.items():
                if char_item_id == item_id:
                    return item_data, char_name

        return None, None

    def parse(
        self, equipment_data: MK11EquipmentType, names_data: MK11EquipmentNameType
    ):
        combined_items: MK11NamedItemsDataType = {}
        for item_slug, item_data in equipment_data["item_slugs"].items():
            item_id = item_data["item_id"]
            item_type = parse_item_type(item_id)
            item_name_data, char = self.find_item_in_chars(
                item_id, names_data["characters"]
            )
            if not item_name_data:
                # Item without name like icons or such
                item_name_data = get_typeddict_items(
                    MK11EquipmentItemNameType,
                    item_name=create_item_name(item_id, item_type),
                )
            if item_type == ItemTypeEnum.AUGMENT.value:
                re_find = re.split(r"([0-9]+)", item_id)
                if len(re_find) == 3:
                    item_name_data["item_name"] += f" Level {re_find[1]}"
            if not char:
                guess_char = item_id.split("_", 1)[0].upper()
                char = guess_char if guess_char in CHARACTERS else "UNKNOWN"
            item_name_data["item_type"] = item_type
            combined_items.setdefault(char, {})
            combined_items[char][item_slug] = get_typeddict_items(
                MK11NamedItemType, **item_data, **item_name_data
            )
        return combined_items

    def handle(self, _, *hashobjects):
        return self.parse(*hashobjects)

    def process(self, file_location, equipment_data, names_data):
        return super().process(file_location, equipment_data, names_data)

    def create_data(self, data):
        return get_typeddict_items(MK11NamedItemsType, data=data, version=self.VERSION)


class Serializable(Database):
    def init_config(self, version):
        return super().init_config(version)

    def create_data(self, data):
        return get_typeddict_items(self.DataType, data=data, version=self.VERSION)

    def decompress(self, path):
        copied_file = copy_file(path, self.temporary_folder)
        decompressed_location = self.decompress_file(copied_file)
        return join(self.temporary_folder, decompressed_location)

    def handle(self, path: str):
        super().handle(path)
        path = self.decompress(path)
        path = self.extract(path)
        for i in range(3):
            try:
                path = self.database_to_json(path)
                data = self.read(path)
            except SyntaxError:
                continue
            return data
        raise SyntaxError(f"Failed to convert the database for whatever reason. Try again or use a pre-made one.")

    def read(self, path):
        with open(path) as file:
            data = file.read()
            return eval(data.replace("true", "True").replace("false", "False"))

    def extract(self, path):
        os.chdir(self.temporary_folder)
        with open(path, "rb") as file:
            file_data = file.read()
            data_offset = file_data[8:12]
            data_offset = little_endian_to_int(data_offset) + 16
            database_data = file_data[data_offset:]

            with open(self.__class__.__name__, "wb+") as outfile:
                outfile.write(database_data)
                outfile.flush()

            name_table_offset = file_data[0x2C : 0x2C + 4]
            name_table_count = file_data[0x28 : 0x28 + 4]
            name_table_offset = little_endian_to_int(name_table_offset)
            name_table_count = little_endian_to_int(name_table_count)

            with open(self.__class__.__name__ + ".txt", "w+") as outfile:
                cur_pointer = name_table_offset
                for i in range(name_table_count):
                    name_length = file_data[cur_pointer : cur_pointer + 4]
                    name_length = little_endian_to_int(name_length)
                    name = "".join(
                        [
                            chr(file_data[cur_pointer + 4 + i])
                            for i in range(name_length)
                        ]
                    )[:-1]
                    hex_val = hex(i)[2:].upper()
                    if i:
                        outfile.write("\n")
                    outfile.write(f"{hex_val}: {name}")
                    cur_pointer += 4 + name_length
                outfile.flush()

        self.chdir_homedir()
        return join(self.temporary_folder, self.__class__.__name__)


class Kollections(Serializable):
    def __init__(self, cur_dir=""):
        super().__init__(cur_dir=cur_dir, version="3.3")
        self.DataType = MK11KollectionsType

    def handle(self, path: str, names_data):
        for i in range(3):
            try:
                data: MK11KollectionItemType = super().handle(path)
                # Get Names
                named_data = self.parse(data, names_data)
            except KeyError:
                continue
            return named_data
        raise KeyError(f"Failed to convert the database for whatever reason. Try again or use a pre-made one.")

    def parse(
        self, data: MK11KollectionItemType, names: MK11EquipmentNameType
    ) -> MK11KollectionsSaveDataType:
        # item_names: Dict[str, MK11KollectionSaveItemType] = {}
        item_types: MK11KollectionsSaveDataType = get_typeddict_items(MK11KollectionsSaveDataType)
        for item in data["mItems"]:
            # item_names: Dict[str, MK11KollectionSaveItemType] = {}
            mID = item.get("mID", "")
            if not mID:
                continue
            item_type = parse_kollection_type(mID)
            item_name = self.find_item_name(
                item, names["kollections"]
            ) or parse_kollection_name(mID, item_type)
            if item_type == KollectionTypeEnum.FATALITY.value:
                char_abbr, fat_type, level = mID.split('_')
                fat_type = separate_digits(fat_type)
                char = CHARACTERS.get(char_abbr.upper())
                item_name = parse_buttons(item_name.strip('"')).strip()
                item_name = f"{char} {fat_type}: {item_name}"
            mDetails = get_typeddict_items(
                MK11KollectionDetailsType, Name=item_name, Type=item_type
            )
            # item_names[item["mID"]] = get_typeddict_items(
            #     MK11KollectionSaveItemType, mItem=item, mDetails=mDetails
            # )
            item_object = get_typeddict_items(
                MK11KollectionSaveItemType, mItem=item, mDetails=mDetails
            )
            item_key = item_type.replace(' ', '')
            item_types[item_key][mID] = item_object
        return item_types

    def find_item_name(
        self, item: MK11KollectionMItemType, names: MK11KollectionsDataType
    ):
        search_id = item.get("mImage", None)
        if search_id:
            if search_id in names["GalleryImageTitles"]:
                return names["GalleryImageTitles"][search_id]
            for category_obj in names["Galleries"].values():  # type: ignore
                category_obj: MK11KollectionGalleryType
                if search_id in category_obj:
                    return category_obj[search_id]
        return None


class Unlockables(Serializable):
    def __init__(self, cur_dir=""):
        super().__init__(cur_dir=cur_dir, version="1.3.1")
        self.DataType = MK11UnlockablesType

    def handle(self, path):
        data = super().handle(path)
        data = self.parse(data)
        return data

    def parse(self, data):
        parsed_data: MK11UnlockablesDataType = get_typeddict_items(
            MK11UnlockablesDataType
        )

        for item in data["mUnlocks"]:
            to_parse = item.get("mID", None)
            if not to_parse:
                continue
            type_ = parse_unlockable_type(to_parse)
            if type_ == "Ignore":
                continue
            parsed_data[type_][to_parse] = parse_unlockable_name(to_parse, type_)

        return parsed_data
