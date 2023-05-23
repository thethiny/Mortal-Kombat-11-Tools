import re
from enum import Enum, EnumMeta
from locale import getdefaultlocale
from typing import Any, Dict, List, Literal, Tuple, TypedDict, TypeVar, Union

from src.utils.logger import GenericLogger
from src.utils.singleton import Singleton


class UnlockerCommon(metaclass=Singleton):
    def __init__(self):
        self.UnlockerVersionType = "R"
        self.UnlockerCurrentVersion = "3.2.0.0"  # Release.Month.Update.Fix
        self.UnlockerVersion = (
            f"{self.UnlockerVersionType}{self.UnlockerCurrentVersion}"
        )
        self.logger = GenericLogger("MKULogger", self.UnlockerVersion)


# Functions


def print(*args, **kwargs):
    UnlockerCommon().logger.print(*args, **kwargs)


# Exceptions


class AuthorizationException(Exception):
    class UserBanned(Exception):
        ...

    class Forbidden(Exception):
        ...

    class MissingInfo(Exception):
        ...


class HashException(Exception):
    class InvalidHash(Exception):
        ...

    class MissingHash(Exception):
        ...

    class InvalidTimeString(Exception):
        ...

    class MissingTS(Exception):
        ...


class IPCException(Exception):
    class BaseException(Exception):
        __name__ = f"IPCException.{BaseException.__name__}"

    class NotConnected(BaseException):
        ...

    class ValueError(BaseException):
        ...


# Enums


class IPCStates(Enum):
    NONE = 0
    INITIALIZED = 1
    CONNECTED = 2
    DISCONNECTED = 3


class NoErrorEnumMeta(EnumMeta):
    def __call__(self, value=None):
        if value is None and hasattr(self, "NONE"):
            return getattr(self, "NONE")
        try:
            return super().__call__(value)
        except ValueError:
            return value

class MK11EnumMeta(EnumMeta):
    def __call__(self, value=None):  # Override Value to "" to auto refer to NONE
        if value is None and hasattr(self, "NONE"):
            return getattr(self, "NONE")
        return super().__call__(value)


class MK11Enum(Enum, metaclass=MK11EnumMeta):
    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return super().__eq__(o)
        return self.value == o

    def __hash__(self) -> Any:
        return hash(self.value)

class ItemUnlockEnum(MK11Enum):
    NONE = None # Invalid
    UNLOCKABLE = "Unlockable" # Unlock by Unlock Endpoint
    INCREMENTABLE = "Incrementable" # Unlock by increment Endpoint
    EXPERIENCE = "Experience" # Unlock by XP Endpoint
    KOLLECTIBLE = "Kollectible" # Unlock by bit Endpoint

class ItemTypeEnum(MK11Enum):
    NONE = None
    ABILITY = "Abilities"
    FINISHER = "Finishers"
    BRUTALITY = "Brutalities"
    GEAR = "Gear"
    SKIN = "Skins"
    TAUNT = "Taunts"
    INTRO = "Intros"
    VICTORY_POSE = "Victory Poses"
    ICON = "Icons"
    AIBUFF = "AI Fighter Buffs"
    AUGMENT = "Augments"
    UNKNOWN = "Other"


class StackableTypeEnum(MK11Enum):
    KURRENCY = "Currency"
    STACKABLE = "Consumeable"
    AUGMENT = ItemTypeEnum.AUGMENT.value
    AIBUFF = ItemTypeEnum.AIBUFF.value
    EXPERIENCE = "Experience"


class UnlockableTypeEnum(MK11Enum):
    NONE = "Ignore"
    CHAR = "Characters"
    BGND = "Backgrounds"
    STAGE = "Stages"
    ANNO = "Announcers"
    SKIN = "Skins"
    ICON = "Icons"
    ENDING = "Endings"
    FATHEAD = "FatalityHeads"
    EMOJI = "Emoticons"
    OTHER = "Other"


class KollectionTypeEnum(MK11Enum):
    NONE = "Ignore"
    MUSIC = "Music"
    ENDING = "Endings"
    RECIPE = "Recipes"
    ARTE = "Environments Art"
    ARTC = "Characters Art"
    ARTS = "Story Art"
    FATALITY = "Fatalities Art"
    OTHER = "Other"


class MK11Endpoints(MK11Enum):
    MK11 = "https://mk11-api.wbagora.com"
    AUTH = "auth"
    ACCESS = "access"
    MY_ACCOUNT = "accounts/me"
    MY_PROFILE = "profiles/me"
    MY_INVENTORY = "profiles/me/inventory"
    UNLOCK = "ssc/invoke/inventory_update"
    MATCH_REWARDS = "ssc/invoke/match_completed"
    PROFILES = "profiles"
    ACCOUNTS = "accounts"


class MK11IPCRequest(MK11Enum):
    AUTH = "AUTH"
    ACCESS = "ACCESS"
    STEAM_KEY = "KEY"
    XBOX_KEY = "XBX"
    STEAM_ID = "ID"
    USER = "USER"
    HASH = "HASH"

class LanguagesShortEnum(Enum, metaclass=NoErrorEnumMeta):
    ARB = "ar"
    BEN = "bn"
    CHS = "zh"
    CHT = "zh"
    ELL = "el"
    ENG = "en"
    ESP = "eo"
    FAS = "fa"
    FRA = "fr"
    GER = "de"
    GRE = "el"
    HIN = "hi"
    HUN = "hu"
    JPN = "ja"
    KOR = "ko"
    NLD = "nl"
    DUT = "nl"
    ITA = "it"
    PER = "fa"
    POL = "pl"
    POR = "pt"
    RUS = "ru"
    SPA = "es"
    SWE = "sv"
    TUR = "tr"
    URD = "ur"

class LanguagesEnum(Enum, metaclass=NoErrorEnumMeta):
    ARB = "العربية"
    BEN = "বাঙালি"
    CHS = "简体中文"
    CHT = "繁體中文"
    ELL = "Ελληνικά"
    ENG = "English"
    ESP = "Esperanto"
    FAS = "فارسی"
    FRA = "Français"
    GER = "Deutsch"
    GRE = "Ελληνικά"
    HUN = "Magyar"
    HIN = "हिन्दी"
    JPN = "日本語"
    KOR = "한국어"
    NLD = "Nederlands"
    DUT = "Nederlands"
    ITA = "Italiano"
    PER = "فارسى"
    POL = "Polski"
    POR = "Português"
    RUS = "Русский"
    SPA = "Español"
    SWE = "Svenska"
    TUR = "Türkçe"
    URD = "اردو"
    NONE = ""

class EnvironmentsEnum(Enum, metaclass=NoErrorEnumMeta):
    XBOX = "xb1"
    STEAM = "steam"
    PS4 = "ps4"

AllUnlockEnums = Union[str, ItemTypeEnum, StackableTypeEnum, ItemUnlockEnum]

# Types

# TDClassType = Union[MutableMapping, TypedDict, ABCMeta, Type]
_TD = TypeVar("_TD", bound=object)


class RecentsKeysType(TypedDict):
    SteamKey: List[Tuple[str, str]]
    AccessToken: List[Tuple[str, str]]


class RecentsFilesType(TypedDict):
    Coalesced: List[str]
    Equipment: List[str]
    Unlockables: List[str]
    Kollections: List[str]
    Game: List[str]


class RecentsType(TypedDict):
    Keys: RecentsKeysType
    Files: RecentsFilesType


class SortingMethodsEnum(MK11Enum):
    ASCENDING = "Ascending"
    DESCENDING = "Descending"
    GAME = "Game Sort"
    NONE = GAME  # Enable in type hinting

# SortingMethodsEnum.NONE = SortingMethodsEnum.NONE.value # type: ignore  # Fix value

class ThemeColorsType(TypedDict):
    primary: str
    secondary: str
    success: str
    info: str
    warning: str
    danger: str
    bg: str
    fg: str
    selectbg: str
    selectfg: str
    border: str
    inputfg: str
    inputbg: str

class TTKThemesType(TypedDict):
    name: str
    display: str
    font: str
    type: str
    colors: ThemeColorsType

class ThemesType(TypedDict):
    unlocker: Dict[str, str]
    custom: Dict[str, str]

class SettingsType(TypedDict):
    ChunkSize: Literal[0, 1, 5, 10, 100, 150, 250]
    ShowOwnedItems: bool
    RequestsSleep: float  # How long to wait between requests
    IPCPort: int
    DefaultLanguage: LanguagesEnum
    Sorting: SortingMethodsEnum
    Theme: Literal["PLACEHOLDER"]
    DisplayLanguage: Literal["PLACEHOLDER"]


class AboutType(TypedDict):
    GameVersion: str
    PublicVersion: str
    VersionType: Literal["Alpha", "Beta", "Gamma", "Public Beta", "Release"]


def lang_enum_to_disp(lang: Union[str, LanguagesEnum]):
    if isinstance(lang, LanguagesEnum):
        ret: str = lang.value
        return ret
    try:
        ret: str = eval(f"LanguagesEnum.{lang}").value
        return ret
    except AttributeError:
        return lang

def get_locale_language():
    system_locale = getdefaultlocale()[0]

    if system_locale:
        system_locale = system_locale.split('_')[0].lower()
        system_locale = LanguagesShortEnum(system_locale)
        if isinstance(system_locale, str): # Failed
            system_locale = LanguagesShortEnum("en")
    else:
        system_locale = LanguagesShortEnum("en")

    return lang_enum_to_disp(system_locale.name)

XBL3_string = "XBL3.0 x={x}"
XBL3_string_user = XBL3_string.format(x="{user_hash};{xbl_token}")


XBL3_re = re.compile(r"^(?:XBL3\.0 )?x\=(?:[0-9]+|\*|\-);")
steam_re = re.compile(r"^08011[0-9A-F]+$")
auth_re = re.compile(r"^[A-Za-z0-9\+/=]+$")
