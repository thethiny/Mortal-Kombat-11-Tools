from flask import Flask, jsonify, request
import requests
from deta import Deta
from exceptions import *
from functools import wraps

supported_platforms = {
    "xbox": "Xbox",
    "steam": "Steam",
    "ps4": "",
    "switch": "",
    "discord": "",
}

app = Flask("mk11_api")

def connect_deta():
    return Deta("a04g52mb_JwN2bFiJFjPynxdZLHRHhgXXvqr7B4Vu")

def connect_base_auth():
    return connect_deta().Base("authentication")

def connect_base_paths():
    return connect_deta().Base("paths")

def get_platform_auth(platform):
    platform = platform.strip().lower()
    mapped_platform = supported_platforms.get(platform)
    if mapped_platform is None:
        raise UserException(f"Platform {platform} is not a correct platform")
    elif mapped_platform == "":
        raise ServerException(f"Unsupported platform {platform}", 501)
    platform = mapped_platform
    auth_base = connect_base_auth()
    platform_auth = auth_base.get(platform)
    if not platform_auth:
        raise UserException(f"No keys found for {platform}")

    return platform_auth

def keys_to_headers(keys):
    headers = {
        "x-hydra-api-key": keys["x-hydra-api-key"],
        "X-NRS-VER": keys["version"],
        "Content-Type": "application/json",
    }
    return headers

def get_platform_headers(platform):
    platform_auth = get_platform_auth(platform)
    return keys_to_headers(platform_auth)

def get_url(path) -> str:
    base = connect_base_paths()
    url: str = base.get(path)["value"] # type: ignore
    return url

def get_root_url() -> str:
    return get_url("root") # type: ignore

def get_full_url(path) -> str:
    root_url = get_root_url()
    resource_url = get_url(path)
    return f"{root_url}{resource_url}"

def get_bundle_name(data):
    if data == "None":
        return None
    return data

def get_is_bundle(data):
    return data > 1

def parse_reward(data):
    price = data["premiumCurrencyPrice"]
    type_ = data["lootItemType"]
    if type_ == "EquipmentItem":
        id_ = data["equipmentId"]
        type_ = "equipment"
        amount = 1
    elif type_ == "SpendableItemLootItem":
        id_ = data["id"]
        type_ = "spendable"
        amount = data["amount"]
    else:
        raise NotImplementedError(f"Unknown type {type_}")
    
    return price, amount, id_, type_

def parse_availabilities(data):
    bundles = []
    for main_item in data:
        availabilities = main_item["mAvailabilities"]
        for availability in availabilities:
            item_end_time = availability["mEndTime"]
            item_start_time = availability["mStartTime"]
            rewards = availability["mReward"]
            bundle_name = get_bundle_name(rewards["name"])
            items_count = rewards["dropCount"]
            is_bundle = get_is_bundle(items_count)
            bundle_items = []
            for reward in rewards["items"]:
                price, amount, id_, type_ = parse_reward(reward)
                bundle_items.append({"price": price, "amount": amount, "id": id_, "type": type_})
            bundles.append({
                "start": item_start_time,
                "end": item_end_time,
                "bundle_name": bundle_name,
                "is_bundle": is_bundle,
                "items": bundle_items,
            })
    return bundles
            

def parse_daily_shop(data):
    bottom_section = data["mBottomSection"]
    top_section = data["mTopSection"]

    top_parsed = parse_availabilities(top_section)
    bottom_parsed = parse_availabilities(bottom_section)

    return top_parsed, bottom_parsed

def error_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServerException as e:
            return jsonify({"error": e.message}), e.status_code
        except UserException as e:
            return jsonify({"error": e.message}), e.status_code
        except NotImplementedError as e:
            return jsonify({"error": str(e)}), 501
    return wrapper

@app.route("/")
@error_decorator
def index():
    return jsonify({"message": "Welcome to the MK11 API"})

@app.route("/daily_shop", methods=["GET"])
@error_decorator
def get_daily_shop_no_platform():
    params: dict = request.args # type: ignore
    platform = params.get("platform", "")
    return get_daily_shop(platform)

@app.route("/daily_shop/<platform>", methods=["GET"])
@error_decorator
def get_daily_shop(platform):
    headers = get_platform_headers(platform)

    url = get_full_url("premium_shop")
    if not url:
        raise ServerException("No URL found for daily shop")
    
    response = requests.get(url, headers=headers)
    return response.json()

@app.route("/daily_shop/<platform>/sections", methods=["GET"])
@error_decorator
def get_daily_shop_sections(platform):
    data = get_daily_shop(platform)

    top, bottom = parse_daily_shop(data)

    return jsonify({"Top": top, "Bottom": bottom})

@app.route("/daily_shop/<platform>/sections/<section>", methods=["GET"])
@error_decorator
def get_daily_shop_sections_section(platform, section):
    data = get_daily_shop_sections(platform)

    json_data: dict = data.json # type: ignore
    if section in json_data:
        return jsonify(json_data[section]), 200 # type: ignore

    raise UserException(f"Section {section} not found", 404)

    


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=4442)