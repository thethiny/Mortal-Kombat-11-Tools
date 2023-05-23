import re
from enum import Enum
from typing import List, Tuple, Type, Union

from src.common import (_TD, AllUnlockEnums, ItemTypeEnum, ItemUnlockEnum,
                        KollectionTypeEnum, StackableTypeEnum,
                        UnlockableTypeEnum)
from src.utils.utils import (is_full_match,
                             separate_cases, separate_digits)


class MK11SlugItem:
    CONSUMEABLE = [ItemTypeEnum.AIBUFF, ItemTypeEnum.AUGMENT, StackableTypeEnum.KURRENCY, StackableTypeEnum.STACKABLE]
    INCREMENTABLES = [ItemUnlockEnum.INCREMENTABLE, ItemUnlockEnum.EXPERIENCE]
    MAX_AMOUNT = 0x7A000000
    def __init__(
        self,
        item_slug: str,
        item_name: str,
        item_char: str,
        item_amount: int,
        item_type: AllUnlockEnums,
        item_internal_type: Union[Enum, str],
        *args,
        **kwargs,
    ):
        self.item_slug = item_slug.strip()
        self.item_name = item_name.strip()
        item_char = item_char.strip()
        item_char = item_char if item_char else "ANY"
        self.item_char = CHARACTERS.get(item_char, item_char) # Get Character's full name if abbreviated
        self.item_amount = item_amount
        self.item_type = self.get_item_type(item_type)
        self.item_stackable: bool = self.is_stackable()
        self.item_internal_type: str = item_internal_type if isinstance(item_internal_type, str) else item_internal_type.value

    def validate_amount(self, amount: Union[str, int]):
        if isinstance(amount, str):
            amount = int(amount)
        if amount > self.MAX_AMOUNT:
            return self.MAX_AMOUNT
        return amount

    @classmethod
    def str_to_enum(cls, string: str):
        if isinstance(string, str):
            item = None
            for e in (ItemTypeEnum, StackableTypeEnum, ItemUnlockEnum):
                try:
                    item = e(string)
                except AttributeError:
                    continue
                return item

            raise ValueError(f"Item {string} is not a valid item type!")

    @classmethod
    def get_item_type(cls, item: AllUnlockEnums):
        if isinstance(item, str):
            item = cls.str_to_enum(item)
        
        if isinstance(item, ItemUnlockEnum):
            return item

        if isinstance(item, StackableTypeEnum):
            if item == StackableTypeEnum.EXPERIENCE:
                return ItemUnlockEnum.EXPERIENCE
            return ItemUnlockEnum.INCREMENTABLE

        if isinstance(item, ItemTypeEnum):
            if item in VALID_AUTO_ITEMS:
                return ItemUnlockEnum.UNLOCKABLE
            if item in cls.CONSUMEABLE:
                return ItemUnlockEnum.INCREMENTABLE
            return ItemUnlockEnum.UNLOCKABLE

        # Impossible
        raise ValueError(f"Item {item} is not a valid item type!")

    def is_stackable(self):
        return self.item_type in self.INCREMENTABLES

    @classmethod
    def fromdict(cls, dict):
        return cls(**dict)

    def to_dict(self, type_: Type[_TD]):
        raise NotImplementedError()


    def __hash__(self) -> int:
        return hash(self.item_slug)

    def __str__(self) -> str:
        string = f"{self.item_char}: {self.item_name}" if self.item_char else self.item_name
        if self.item_amount > 1:
            string += f" x{self.item_amount}"
        elif self.item_amount < 0:
            string += f" [Remove] x{abs(self.item_amount)}"
        return string

    def __repr__(self) -> str:
        return repr(str(self))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.item_slug == o.item_slug
        return self.item_slug.__eq__(o)

    def __lt__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.item_slug < o.item_slug
        elif isinstance(o, str):
            return self.item_slug.__lt__(o)
        raise TypeError

    def __gt__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.item_slug > o.item_slug
        elif isinstance(o, str):
            return self.item_slug.__gt__(o)
        raise TypeError



KURRENCY = {
    "Exp_Koins": "Koins",
    "Exp_SoulFragments": "Soul Fragments",
    "Exp_BrutalityHearts": "Brutality Hearts",
    "Exp_PremiumCurrency": "Time Krystals",
    "Exp_RerollTokens": "Reroll Tokens",
    "GearXPBoost": "Gear Tokens",
    "EasyFatality": "Easy Fatality Tokens",
    "SkipFight": "Skip Fight Tokens",
    "SkeletonKey": "Skeleton Keys",
}

EXPERIENCE = {
    "Player": "Me",
    "ItemProgression": "Gear",
    "Baraka": "Baraka",
    "JohnnyCage": "Johnny Cage",
    "CassieCage": "Cassie Cage",
    "Cetrion": "Cetrion",
    "CyberFrost": "Frost",
    "Cyrax": "Cyrax",
    "DVorah": "D'Vorah",
    "ErronBlack": "Erron Black",
    "FireGod": "Fire Liu Kang",
    "Fujin": "Fujin",
    "JacquiBriggs": "Jacqui Briggs",
    "Jade": "Jade",
    "JaxBriggs": "Jax Briggs",
    "Joker": "The Joker",
    "Kabal": "Kabal",
    "Kano": "Kano",
    "Kitana": "Kitana",
    "Kollector": "Kollector",
    "KotalKahn": "Kotal Kahn",
    "Kronika": "Kronika",
    "KungLao": "Kung Lao",
    "LiuKang": "Liu Kang",
    "Mileena": "Mileena",
    "Nightwolf": "Nightwolf",
    "NoobSaibot": "Noob Saibot",
    "Raiden": "Raiden",
    "Rain": "Rain",
    "Rambo": "Rambo",
    "Robocop": "Robocop",
    "Scorpion": "Scorpion",
    "Sektor": "Sektor",
    "ShangTsung": "Shang Tsung",
    "ShaoKahn": "Shao Kahn",
    "Sheeva": "Sheeva",
    "Sindel": "Sindel",
    "Skarlet": "Skarlet",
    "Sonya": "Sonya Blade",
    "Spawn": "Spawn",
    "SubZero": "Sub-Zero",
    "Terminas": "Geras",
    "Terminator": "The Terminator",
}

# Add Tag Assists if they're missing
# Add Player EXP and Progression EXP

CHARACTERS = {
    "ALL": "All Characters",
    "ANY": "Any Character",
    "ASH": "Ash Williams",
    "BAR": "Baraka",
    "CAS": "Cassie Cage",
    "CET": "Cetrion",
    "CYR": "Cyrax",
    "DAE": "Daegon",
    "DVO": "D'Vorah",
    "ERR": "Erron Black",
    "FIR": "Fire Liu Kang",
    "FRO": "Frost",
    "FUJ": "Fujin",
    "GEN": "General",
    "HAV": "Havik",
    "JAC": "Jacqui Briggs",
    "JAD": "Jade",
    "JAX": "Jax Briggs",
    "JOH": "Johnny Cage",
    "JOK": "The Joker",
    "KAB": "Kabal",
    "KAN": "Kano",
    "KIT": "Kitana",
    "KOL": "Kollector",
    "KOT": "Kotal Kahn",
    "KRO": "Kronika",
    "KUN": "Kung Lao",
    "LIU": "Liu Kang",
    "MIL": "Mileena",
    "NIA": "Nitara",
    "NIO": "Nightwolf Objects",
    "NIT": "Nightwolf",
    "NOO": "Noob Saibot",
    "RAI": "Raiden",
    "RAM": "Rambo",
    "RAN": "Rain",
    "REI": "Reiko",
    "ROB": "Robocop",
    "SAR": "Sareena",
    "SCO": "Scorpion",
    "SEK": "Sektor",
    "SHA": "Shao Kahn",
    "SHE": "Sheeva",
    "SHI": "Shinnok",
    "SHT": "Shang Tsung",
    "SIN": "Sindel",
    "SKA": "Skarlet",
    "SON": "Sonya Blade",
    "SPA": "Spawn",
    "SUB": "Sub-Zero",
    "TAK": "Takeda",
    "TAV": "Taven",
    "TBD": "Uncompleted",
    "RED": "Injustice2 Leftover Code",
    "TER": "Geras",
    "TRM": "The Terminator",
    "PL1": "Krypt Guy",
    "PLY": "Me", # For Compatibility with unlocker
    "NONE": None
}

BUTTON_MAPPINGS = {
    "Away": "⬅",
    "Towards": "➡",
    "Up": "⬆",
    "Jump": "⬆",
    "Down": "⬇",
    "FP": "J",
    "BP": "I",
    "FK": "K",
    "BK": "L"
}

BUTTON_MAPPINGS_PATTERN = re.compile(r"(?i)\[(?:" + '|'.join(BUTTON_MAPPINGS.keys()) + r")\]")

ITEM_PATTERNS: List[Tuple[ItemTypeEnum, re.Pattern]] = [
    (ItemTypeEnum.ABILITY, re.compile(r"(?i)[A-Z]{3}_Ability[0-9]+(_Level[0-9]+){0,1}")),
    (ItemTypeEnum.FINISHER, re.compile(r"(?i)[A-Z]{3}_Fatality[0-9]+(_Level[0-9]+){0,1}")),
    (ItemTypeEnum.FINISHER, re.compile(r"(?i)[A-Z]{3}_Friendship[0-9]+(_Level[0-9]+)")),
    (ItemTypeEnum.FINISHER, re.compile(r"(?i)[A-Z]{3}_StageFatality(_Level[0-9]+)")),
    (
        ItemTypeEnum.BRUTALITY,
        re.compile(r"(?i)[A-Z]{3}_Brutality[0-9]+(_Level[0-9]+){0,1}"),
    ),
    (
        ItemTypeEnum.GEAR,
        re.compile(r"(?i)[A-Z]{3}(_[A-Za-z0-9]+)*_Gear[A-Z]{1,2}[0-9]+(_Level[0-9]+){0,1}"),
    ),
    (
        ItemTypeEnum.SKIN,
        re.compile(r"(?i)^[A-Z]{3}(_[A-Za-z0-9]+)*_Skin[0-9]*(_Palette[0-9]+){0,1}(_Level[0-9]+){0,1}$"),
    ),
    (ItemTypeEnum.TAUNT, re.compile(r"(?i)[A-Z]{3}_Taunt[0-9]+(_Level[0-9]+){0,1}")),
    (ItemTypeEnum.INTRO, re.compile(r"(?i)[A-Z]{3}_Intro[A-Z]{1,2}(_Level[0-9]+){0,1}")),
    (
        ItemTypeEnum.VICTORY_POSE,
        re.compile(r"(?i)[A-Z]{3}_Victory[A-Z]{1,2}(_Level[0-9]+){0,1}"),
    ),
    (ItemTypeEnum.ICON, re.compile(r"(?i)[A-Z]{3}_IconStyle[0-9]+_[0-9]+")),
    (ItemTypeEnum.AIBUFF, re.compile(r"(?i)[A-Z]{3}_AIFighter[A-Za-z0-9]+_[0-9]+")),
    (
        ItemTypeEnum.AIBUFF,
        re.compile(r"(?i)[A-Z]{3}_[A-Z]{3}_AIFighter[A-Za-z0-9]+_[0-9]+"),
    ),  # I don't know for sure
    (ItemTypeEnum.AUGMENT, re.compile(r"(?i)AUG_[A-Z]{3}_[A-Za-z0-9]+")),  # General
    (ItemTypeEnum.AUGMENT, re.compile(r"(?i)AUG_[A-Z]{3}_[A-Za-z0-9]+_[0-9]+")),  # Per Char
]

UNLOCKABLE_EQUIPMENT = {item[0] for item in ITEM_PATTERNS}

UNLOCKABLES_PATTERNS: List[Tuple[UnlockableTypeEnum, re.Pattern]] = [
    (UnlockableTypeEnum.NONE, re.compile(r"(?i).*[.].*")),
    (UnlockableTypeEnum.ANNO, re.compile(r"(?i)^AnnouncerVoice_.+")),
    (UnlockableTypeEnum.STAGE, re.compile(r"(?i)^BGND_.+")),
    (UnlockableTypeEnum.BGND, re.compile(r"(?i).+Background$")),
    (UnlockableTypeEnum.CHAR, re.compile(r"(?i)^CHAR_.+")),
    (UnlockableTypeEnum.EMOJI, re.compile(r"(?i)^Emoticon[0-9]*")),
    (UnlockableTypeEnum.ENDING, re.compile(r"(?i).+EndingUnlock$")),
    (UnlockableTypeEnum.FATHEAD, re.compile(r"(?i).+FatalityHeadUnlock$")),
    (UnlockableTypeEnum.ICON, re.compile(r"(?i)^[A-Za-z0-9_]+Icon$")),
    (UnlockableTypeEnum.OTHER, re.compile(r"(?i).+Unlock")),
    (UnlockableTypeEnum.SKIN, re.compile(r"(?i).+_Skin$")),
]

UNLOCKABLE_UNLOCKABLES = {item[0] for item in UNLOCKABLES_PATTERNS}

KOLLECTIONS_PATTERNS: List[Tuple[KollectionTypeEnum, re.Pattern]] = [
    (KollectionTypeEnum.MUSIC, re.compile(r"(?i)^Extras_MUS[0-9]+$")),
    (KollectionTypeEnum.ENDING, re.compile(r"(?i)^[A-Z]{3}_EndingUnlock$")),
    (KollectionTypeEnum.RECIPE, re.compile(r"(?i)^Extras_RECIPE[0-9]+$")),
    (KollectionTypeEnum.ARTE, re.compile(r"(?i)^ConceptArtENV_[A-Z]+[0-9]+$")),
    (KollectionTypeEnum.ARTC, re.compile(r"(?i)^ConceptArtCHAR_[A-Z]{3}[0-9]+$")),
    (KollectionTypeEnum.ARTC, re.compile(r"(?i)^CHAR_[A-Z]+$")),
    (KollectionTypeEnum.ARTS, re.compile(r"(?i)^ConceptArtSTORY_[A-Z]+[0-9]+$")),
    (KollectionTypeEnum.FATALITY, re.compile(r"(?i)^[A-Z]{3}_Fatality[0-9]+_Level[0-9]+$")),
]

UNLOCKABLE_KOLLECTION = {item[0] for item in KOLLECTIONS_PATTERNS}

VALID_AUTO_ITEMS = [
    ItemTypeEnum.ABILITY,
    ItemTypeEnum.BRUTALITY,
    ItemTypeEnum.FINISHER,
    ItemTypeEnum.GEAR,
    ItemTypeEnum.ICON,
    ItemTypeEnum.INTRO,
    ItemTypeEnum.SKIN,
    ItemTypeEnum.TAUNT,
    ItemTypeEnum.VICTORY_POSE,
]

def button_match_fn(match: re.Match):
    word = match.group()
    new_word = BUTTON_MAPPINGS.get(word.strip('[]'), word)
    return word if word == new_word else new_word + ' '

def parse_buttons(button_str: str):
    return BUTTON_MAPPINGS_PATTERN.sub(button_match_fn, button_str)

def parse_kollection_type(item_id):
    for item_type, pattern in KOLLECTIONS_PATTERNS:
        if is_full_match(pattern, item_id):
            return item_type.value
    return "Other"


def parse_kollection_name(item_id, type_):
    if type_ == KollectionTypeEnum.ENDING:
        char = item_id.split("_", 1)[0]
        char_name = CHARACTERS.get(char)
        return f"Unlock {char_name}'s Ending"
    return item_id


def parse_unlockable_type(item_id):
    for item_type, pattern in UNLOCKABLES_PATTERNS:
        if is_full_match(pattern, item_id):
            return item_type.value
    return "Other"


def parse_unlockable_name(item_id, type_):
    item_id = separate_cases(item_id)
    item_id = separate_digits(item_id)
    if (
        (item_id[3] == "_" or item_id[3] == " ") and item_id[:3].upper() in CHARACTERS
    ) or item_id[:3] in CHARACTERS:
        item_id = (
            CHARACTERS[item_id[:3].upper()] + " " + item_id[3:]
        )  # Get Player Name from first 3 letters

    if item_id.startswith("KLeague"):
        item_id = "Kombat League" + item_id.split("_", 1)[-1]

    item_id = item_id.replace("GOTY", " Aftermath ")

    if type_ == UnlockableTypeEnum.CHAR.value:
        to_return = item_id.split("_", 1)[-1]
    elif type_ == UnlockableTypeEnum.STAGE.value:
        if item_id.startswith("BGND"):
            to_return = item_id.split("_", 1)[-1]
        else:
            to_return = item_id
    elif type_ == UnlockableTypeEnum.ANNO.value:
        to_return = item_id.rsplit("_", 1)[-1] + " Announcer"
    elif type_ == UnlockableTypeEnum.SKIN.value:
        to_return = item_id.replace("_", " ")
    elif type_ == UnlockableTypeEnum.ICON.value:
        to_return = item_id
    elif type_ == UnlockableTypeEnum.ENDING.value:
        myChar = item_id.split("_", 1)[0].strip()
        to_return = f"{CHARACTERS.get(myChar, myChar)} Ending"
    elif type_ == UnlockableTypeEnum.FATHEAD.value:
        to_return = item_id[:-6]
    elif type_ == UnlockableTypeEnum.EMOJI.value:
        to_return = "Emoticon " + item_id.strip("Emoticon")
    else:
        to_return = item_id
    return re.sub(r"[\t\r\n ]+", " ", to_return.replace("_", " ").strip())


def iter_currency():
    for currency, display_name in KURRENCY.items():
        yield display_name, currency


def iter_characters():
    for char_id, char_name in CHARACTERS.items():
        yield char_name, char_id


def parse_char(char_abbr):
    char_abbr = char_abbr.upper()  # Should be upper be default
    abbr = char_abbr.split("_", 1)[0]

    if abbr in CHARACTERS:
        return CHARACTERS[abbr]

    if abbr in ["AUG", "ANY", "RED"]:  # Augments are AUG_Char_blabla
        try:
            abbr = char_abbr.split("_", 2)[1]
        except Exception:
            pass  # Will just go to Unknown

    return CHARACTERS.get(abbr, "Unknown")


def parse_item_type(item_id):
    for item_type, pattern in ITEM_PATTERNS:
        if is_full_match(pattern, item_id):
            return item_type.value
    return ItemTypeEnum.UNKNOWN.value


def create_item_name(item_id: str, item_type: str):
    if item_type == ItemTypeEnum.ICON.value:
        # CHR_IconStyleX_YY
        char, style, icon_id = item_id.split("_")
        style = re.split(r"([0-9]+)", style)
        if len(style) > 1:
            style = style[1]
        char = CHARACTERS.get(char, "Unknown")
        return f"{char}'s Icon {int(icon_id)} of Style {style}"
    return item_id  # Name not found
