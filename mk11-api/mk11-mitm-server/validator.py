from typing import Any, Dict, List, Type, TypedDict, Union
import typing


class PremiumShopType:
    class mRewardItemsType(TypedDict):
        dropWeight: int
        premiumCurrencyPrice: int
        lootItemType: str
        equipmentId: str
        isUniqueToPlayersInventory: bool
        seed: int
        level: int
        dropFlags: int

    class mRewardType(TypedDict):
        items: List["PremiumShopType.mRewardItemsType"]
        rules: List[str]
        name: str
        descriptionOverride: str
        dropCount: int
        dropWeight: int
        dropFlags: int

    class mAvailabilitiesType(TypedDict):
        mReward: List["PremiumShopType.mRewardType"]

    class mSectionType(TypedDict):
        mAvailabilities: List["PremiumShopType.mAvailabilitiesType"]

    class BodyResponseType(TypedDict):
        mTopSection: List["PremiumShopType.mSectionType"]
        mBottomSection: List["PremiumShopType.mSectionType"]

    class BodyType(TypedDict):
        response: "PremiumShopType.BodyResponseType"

    class ResponseType(TypedDict):
        body: "PremiumShopType.BodyType"
        metadata: str
        return_code: int


_T = typing.TypeVar("_T")


def parse_value_type(value: Union[type, str], og_value: type) -> Any:
    """
    Parse a string value into a type.
    """

    if not isinstance(value, str):
        value = str(value)

    if value.startswith("typing."):
        type_name = value.split(".", 1)[1].split("[")[0]
        return eval(type_name), type_name
    elif value.startswith("ForwardRef"):
        type_name = value.split("'")[1]
        return eval(type_name), type_name
    else:
        type_name = og_value.__name__
        return eval(type_name), type_name

def validate_typing(data: Any, typing: Type[_T]) -> _T:
    """
    Validate that the "data" is a TypedDict of type typing.
    """


    for key in data:
        if key not in typing.__annotations__:
            raise TypeError(f"{key} is not a valid key in {typing}")

    for key, value in typing.__annotations__.items():
        value, type_name = parse_value_type(value, value)
        print(f"{key} is {type_name}")
        if key not in data:
            raise ValueError(f"{key} is missing from {typing.__name__}")

        try:
            if not isinstance(data[key], value):
                print(data[key], type(value), value)
                raise ValueError(f"{key} is not of type {type_name}")
        except TypeError as e:
            validate_typing(data[key], value)

        if value == Dict:
            validate_typing(data[key], value)
        elif value == List:
            if not data: # Empty List -> Valid
                continue
            og_value = typing.__annotations__[key]
            value = str(og_value)[11:].strip('[]')
            value, type_name = parse_value_type(value, typing.__annotations__[key])
            for item in data:
                validate_typing(item, value)
            

    ret_data: _T = data
    return ret_data


data = validate_typing(
    {
        "body": {
            "response": {"mTopSection": [{
                "mAvail"
            }], "mBottomSection": []},
        },
        "metadata": "",
        "return_code": 2,
    },
    PremiumShopType.ResponseType,
)
