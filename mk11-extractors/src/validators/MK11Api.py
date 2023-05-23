from typing import Any, Dict, List, Literal, Optional, TypedDict


class _UnlockTrackerPayloadType(TypedDict):
    amount: int
    itemType: str
    slug: str
    source: str
    source_detail: str

class _UserDataItemType(TypedDict):
    items: List[_UnlockTrackerPayloadType]

class _UserDataDataType(TypedDict):
    cost: _UserDataItemType
    unlockTracker: _UserDataItemType


class UserDataType(TypedDict):
    data: _UserDataDataType

class HashedRequestType(TypedDict):
    item_slug: str
    ts: str
    vr2: str

class AddGameItemType(HashedRequestType):
    user_data: Dict[Literal["LicenseId"], str]

class IncrementConsumeableType(HashedRequestType):
    inc_amount: int


class UpdateInventoryType(TypedDict):
    add_game_item: List[AddGameItemType]
    create_instance: List
    game_unlockables: List
    inc_consumable: List[IncrementConsumeableType]
    lock_item: List[HashedRequestType]
    unlock_item: List[HashedRequestType]
    update_data: List[HashedRequestType]
    user_data: UserDataType


# Requests

# Responses


class UserBanType(TypedDict):
    ban_end_date: str
    duration: str
    units: str


class AuthResponseType(TypedDict):
    id: str
    created_at: str
    updated_at: str
    token: str
    type: str
    account_id: str
    auth_id: str
    expires_at: int
    fingerprint: Any

# On Error
class AuthErrorResponseType(AuthResponseType):
    code: int
    msg: str
    body: Dict[Literal["account"], "ResponseAccountType"]
    hydra_error: int
    relying_party_error: int


class ResponseProfileKoreType(TypedDict):
    platform_name: str
    build_version: str
    is_lb_banished: Literal["false", "true"]
    is_mm_banished: Literal["false", "true"]
    billboards_clean: bool
    pc_subplatform_name: str
    steamid3_verification_error: int
    steamid64_verified: str
    steamid64_lender: str

class ResponseProfileGameDLCOwnershipType(TypedDict):
    AUX_INT_8: bool
    OWNS_DLC_KOMBAT_PACK: bool

class ResponseProfileGameType(TypedDict):
    mp: Dict
    any: Dict
    sp: Dict
    profile_stats_version: int
    region_id: int
    last_daily_challenge_update: int # TimeStamp
    external_login: Dict
    ai_fighter_team_object: Dict
    ai_fighter_timestamps: Dict
    created_at_milliseconds_modifiable: int # TimeStamp
    inventory_has_upgraded: bool

    # Item Validation
    # Old
    item_hash_validation_last_date_fail2: str # ISOTime
    item_hash_validation_last_reason_fail2: str # Error Message
    item_hash_validation_fail2: int
    #
    dlc_ownership_verification_failed_v2: ResponseProfileGameDLCOwnershipType
    dlc_entitlement_info_valid: bool
    dlc_entitlement_info_valid_prev: bool
    item_hash_validation_last_date_fail_kicker: str # ISOTime
    item_hash_validation_last_reason_fail_kicker: str # Error Message
    item_hash_validation_fail_kicker: int
    # New
    item_hash_validation_last_reason_fail_hacker: str # Error Message
    item_hash_validation_last_date_fail_hacker: str # ISOTime
    item_hash_validation_fail_hacker: int
    #





class ResponseProfileDataType(TypedDict):
    change_count: int
    kore: ResponseProfileKoreType
    game: ResponseProfileGameType
    change_count: int


class ResponseUserInfoCommonType(TypedDict):
    id: str
    updated_at: str
    created_at: str
    data: ResponseProfileDataType
    server_data: Dict
    points: Any


class ResponseProfileType(ResponseUserInfoCommonType):
    account_id: str
    last_login: str
    notifications: Dict
    aggregates: Dict
    user_segments: List[str]

    # Stuff idc about here
    matches: Dict
    cross_match_results: Dict
    calculations: Dict
    files: List
    random_distribution: float
    ...  # Other stuff I can't be bothered with


class ResponseWBIdentityType(TypedDict):
    email: str
    last_sync: str


class AlternateIdentityType(TypedDict):
    id: str
    username: str
    avatar: str
    email: str


class ResponseAccountIdentityType(TypedDict):
    avatar: str  # URL to img
    username: str  # Named ID
    default_username: bool
    personal_data: Dict
    alternate: Dict[str, List[AlternateIdentityType]]


class ResponseAccountType(ResponseUserInfoCommonType):
    deleted: bool
    public_id: str
    identity: ResponseAccountIdentityType
    email_verification: Dict[Literal["state"], str]
    opt_ins: Dict[str, bool]
    auth: Dict[str, List]
    external_accounts: Dict
    privacy_levels: Dict
    state: str  # Profile State as in banned or not
    state_data: UserBanType
    wbplay_data_synced: bool
    wbplay_identity: ResponseWBIdentityType
    locale: Any
    connections: List[Dict]


class AccessResponseType(TypedDict):
    token: str
    profile: ResponseProfileType
    account: ResponseAccountType
    achievements: List
    notifications: List
    maintenance: Optional[Dict]


class PayloadItemDataType(TypedDict):
    Power: int
    ChallengeUserData: Dict
    RandomSeed: int
    ItemVersion: int
    InstanceID: str
    InventoryVersion: int
    ItemLevel: int
    SocketOverrides: int
    Transmogrify: str
    LicenseId: str
    ReferencerCount: int
    ItemDefinitionHandle: str
    Flags: int
    Items: List

class ResponseUnlockEventPayloadItemType(TypedDict):
    id: str
    updated_at: str
    count: int
    account_id: str
    item_slug: str
    data: PayloadItemDataType
    server_data: "InventoryItemServerDataType"
    created_at: str
    currency_sources: List[str]
    actions: List
    result_type: str

class ResponseUnlockEventPayloadType(TypedDict):
    items: List[ResponseUnlockEventPayloadItemType]
    user_data: UserDataType
    profile_data: Dict

class ResponseUnlockTransactionEventType(TypedDict):
    auto_managed: bool
    timestamp: int
    account_id: str
    payload: ResponseUnlockEventPayloadType
    template: str


class ResponseUnlockTransactionType(TypedDict):
    transaction_id: str
    kore_events: List[ResponseUnlockTransactionEventType]
    call_trace: List[str]
    client_version: str
    client_platform: Optional[str]

class ResponseRewardsType(TypedDict):
    rewards: ResponseUnlockEventPayloadType

class ResponseUnlockItemsBodyType(TypedDict):
    transaction: ResponseUnlockTransactionType
    account_id: str
    response: ResponseRewardsType

class ResponseUnlockItemsType(TypedDict):
    body: ResponseUnlockItemsBodyType
    metadata: Dict[Literal["msg"], str]
    return_code: int

# Inventory


class InventoryItemServerDataType(TypedDict):
    name: str
    type_class: str
    item_type: str


class UserInventoryItemType(TypedDict):
    id: str
    updated_at: str
    count: int
    account_id: str
    item_slug: str
    data: Dict
    server_data: InventoryItemServerDataType
    created_at: str
    currency_sources: List
    actions: List
    result_type: str


ResponseInventoryType = List[UserInventoryItemType]

# Body
class AuthBodyCommonType(TypedDict):
    fail_on_missing: Literal[0, 1]
class AuthBodyType(AuthBodyCommonType):
    steam: str

class AuthBodyTypeXbox(AuthBodyCommonType):
    xb1: Literal["header-authorization"]


class AccessBodyType(TypedDict):
    auth_token: str
    options: List[str]

# Headers
class CommonHeaderType(TypedDict):
    HydraApiKey: str
    MIMEType: Literal["application/json"]

class CommonHeaderTypeXbox(CommonHeaderType):
    Authorization: str


class AuthenticatedHeaderType(CommonHeaderType):
    HeaderAccessToken: str


class CommonHeaderExtrasType(CommonHeaderType):
    NrsVersion: str


class InventoryHeaderType(CommonHeaderExtrasType):
    HeaderAccessToken: str
    KoreResponse: bool
    TransactionID: str


AccessHeaderType = AuthHeaderType = CommonHeaderType

KEY_MAPS = {
    "HydraApiKey": "x-hydra-api-key",
    "MIMEType": "Content-Type",
    "HeaderAccessToken": "x-hydra-access-token",
    "NrsVersion": "X-NRS-VER",
    "KoreResponse": "x-nrs-kore-response",
    "TransactionID": "x-nrs-transaction",
    "NRSPlatform": "X-NRS-PLAT",
}

# Custom
class UserGeneratedProfileType(TypedDict):
    created_at: str
    updated_at: str
    account_id: str
    id: str
    platform: str
    game_version: str


class UserGeneratedAccountType(TypedDict):
    type: str
    platform_username: str
    platform_id: str
    public_id: str
    state: str
    state_data: UserBanType


class UserGeneratedInfoType(UserGeneratedProfileType, UserGeneratedAccountType):
    access_token: str
    auth_token: str


class UserItemType(TypedDict):
    item_slug: str
    item_definition: str
    item_name: str
    item_count: int

UserOwnedItemsType = Dict[str, UserItemType]
