from typing import Dict, List, TypedDict

from src.common import ItemTypeEnum

# MK11ItemDatabase


class MK11EquipmentItemType(TypedDict):
    item_id: str
    item_definition: str


class MK11EquipmentType(TypedDict):
    version: str
    item_slugs: Dict[str, MK11EquipmentItemType]


class MK11EquipmentItemMiscType(TypedDict):
    Flavor: Dict[str, str]
    Description: str
    MoveInfo: str


# Coalesced
class MK11EquipmentItemNameType(TypedDict):
    item_name: str
    item_misc: MK11EquipmentItemMiscType
    attributes: str
    item_type: str


class MK11KollectionGalleryType(TypedDict):
    Characters: Dict[str, str]
    Environments: Dict[str, str]
    Story: Dict[str, str]
    Music: Dict[str, str]
    Endings: Dict[str, str]
    Recipes: Dict[str, str]

class MK11KollectionsDataType(TypedDict):
    Galleries: MK11KollectionGalleryType
    GalleryImageTitles: Dict[str, str]


MK11CharacterDataType = Dict[str, Dict[str, MK11EquipmentItemNameType]]


class MK11EquipmentNameType(TypedDict):
    version: str
    characters: MK11CharacterDataType
    kollections: MK11KollectionsDataType


class MK11KollectionMItemType(TypedDict):
    mLocalizationKey: str
    mPackageName: str
    mThumbnailImage: str
    mCategory: int
    mID: str
    mPage: int
    mUnlockBitIndex: int
    mImage: str
    mIsChild: bool
    mEventID: int


class MK11KollectionDetailsType(TypedDict):
    Name: str
    Type: str


class MK11KollectionSaveItemType(TypedDict):
    mDetails: MK11KollectionDetailsType
    mItem: MK11KollectionMItemType


class MK11KollectionItemType(TypedDict):
    mItems: List[MK11KollectionMItemType]
    mAudioMapping: List[MK11KollectionMItemType]

class MK11KollectionsSaveDataType(TypedDict):
    Music: Dict[str, MK11KollectionSaveItemType]
    EnvironmentsArt: Dict[str, MK11KollectionSaveItemType]
    CharactersArt: Dict[str, MK11KollectionSaveItemType]
    StoryArt: Dict[str, MK11KollectionSaveItemType]
    FatalitiesArt: Dict[str, MK11KollectionSaveItemType]
    Endings: Dict[str, MK11KollectionSaveItemType]
    Recipes: Dict[str, MK11KollectionSaveItemType]
    Other: Dict[str, MK11KollectionSaveItemType]

class MK11KollectionsType(TypedDict):
    version: str
    data: MK11KollectionsSaveDataType


class MK11UnlockablesDataType(TypedDict):
    Characters: Dict[str, str]
    Backgrounds: Dict[str, str]
    Announcers: Dict[str, str]
    Skins: Dict[str, str]
    Other: Dict[str, str]
    Icons: Dict[str, str]
    Endings: Dict[str, str]
    Stages: Dict[str, str]
    FatalityHeads: Dict[str, str]
    Emoticons: Dict[str, str]


class MK11UnlockablesType(TypedDict):
    version: str
    data: MK11UnlockablesDataType


class MK11NamedItemType(MK11EquipmentItemType, MK11EquipmentItemNameType):
    pass


MK11NamedItemsDataType = Dict[str, Dict[str, MK11NamedItemType]]


class MK11NamedItemsType(TypedDict):
    version: str
    data: MK11NamedItemsDataType  # data->charname->slug->MK11NamedItemType
